"""
Search service — orchestrates the search pipeline for Phase 1.

1. Create a SearchQuery record
2. Call the search provider
3. Store each SearchResult + RawMarkdown
4. Return the completed SearchQuery
"""

import logging
from django.utils import timezone

from .models import SearchQuery, SearchResult, RawMarkdown
from .providers.registry import get_search_provider

logger = logging.getLogger(__name__)


def execute_search(query: str, num_sites: int = 5) -> SearchQuery:
    """
    Run the full Phase 1 search pipeline:
      1. Persist the query
      2. Hit the search provider
      3. Store results + markdown
      4. Return updated SearchQuery
    """

    # 1. Create the search record
    search_query = SearchQuery.objects.create(
        query=query,
        num_sites=num_sites,
        status="searching",
    )

    try:
        # 2. Get the search provider and execute
        provider = get_search_provider()
        search_query.provider = provider.__class__.__name__
        search_query.save(update_fields=["provider"])

        response = provider.search(query=query, limit=num_sites)

        if not response.success:
            search_query.status = "failed"
            search_query.error_message = response.error
            search_query.save(update_fields=["status", "error_message"])
            return search_query

        # 3. Store each result and its markdown
        search_query.status = "crawling"
        search_query.save(update_fields=["status"])
        
        # Init Parser (Phase 2)
        from .agents.parser import ParserAgent
        from .models import ParsedProduct
        
        parser_agent = None
        try:
            parser_agent = ParserAgent()
        except ValueError:
            logger.warning("No LLM Provider active. Skipping Phase 2 parsing.")

        for idx, item in enumerate(response.results):
            search_result = SearchResult.objects.create(
                search_query=search_query,
                url=item.url,
                title=item.title or "",
                description=item.description or "",
                position=idx + 1,
            )

            raw_md = RawMarkdown.objects.create(
                search_result=search_result,
                content=item.markdown or "",
            )
            
            if parser_agent and item.markdown:
                search_query.status = "parsing"
                search_query.save(update_fields=["status"])
                
                parsed_data = parser_agent.parse(item.markdown, item.url)
                ParsedProduct.objects.create(
                    search_result=search_result,
                    raw_markdown=raw_md,
                    data=parsed_data
                )

        # 4. Mark complete
        search_query.status = "completed"
        search_query.completed_at = timezone.now()
        search_query.save(update_fields=["status", "completed_at"])

        logger.info(
            f"Search completed: '{query}' — {len(response.results)} results"
        )

    except Exception as exc:
        logger.exception(f"Search pipeline failed for '{query}'")
        search_query.status = "failed"
        search_query.error_message = str(exc)
        search_query.save(update_fields=["status", "error_message"])

    return search_query
