"""
Search service — orchestrates the full pipeline (Phases 1-5).

Pipeline:
  1. Create SearchQuery record
  2. Search provider → top N URLs
  3. Store SearchResult + RawMarkdown
  4. Phase 2+3: Parse + Normalize in parallel (per result)
  5. Phase 4: Comparison Engine → ComparisonResult (per query)
  6. Phase 5: Recommendation Agent → Recommendation (per query)
  7. Mark complete
"""

import logging
import concurrent.futures
from django.utils import timezone

from .models import (
    SearchQuery, SearchResult, RawMarkdown,
    ParsedProduct, NormalizedProduct, ComparisonResult, Recommendation,
)
from .providers.registry import get_search_provider

logger = logging.getLogger(__name__)


def _parse_and_normalize(parser_agent, normalizer_agent, search_result, raw_md, item):
    """
    Run Phase 2 (parse) + Phase 3 (normalize) for a single search result.
    Designed to be called concurrently via ThreadPoolExecutor.
    """
    if not parser_agent or not item.markdown:
        return None

    parsed_data = parser_agent.parse(item.markdown, item.url)
    parsed_product = ParsedProduct.objects.create(
        search_result=search_result,
        raw_markdown=raw_md,
        data=parsed_data,
    )

    if normalizer_agent and parsed_data:
        norm_result = normalizer_agent.normalize(parsed_data)
        NormalizedProduct.objects.create(
            parsed_product=parsed_product,
            normalized_specs=norm_result.get("normalized_specs", {}),
            normalized_price=norm_result.get("normalized_price", {}),
        )
        return {
            "title": parsed_data.get("title", ""),
            "seller": parsed_data.get("seller", {}),
            "normalized_specs": norm_result.get("normalized_specs", {}),
            "normalized_price": norm_result.get("normalized_price", {}),
            "rating": parsed_data.get("rating", {}),
            "availability": parsed_data.get("availability", {}),
            "shipping": parsed_data.get("shipping", {}),
            "source_url": item.url,
        }

    return None


def execute_search(query: str, num_sites: int = 5, persona: str = "General") -> SearchQuery:
    """
    Run the full search + intelligence pipeline.
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

        # 3. Store results + markdown (Phase 1)
        search_query.status = "crawling"
        search_query.save(update_fields=["status"])

        # Init agents
        from .agents.parser import ParserAgent
        from .agents.normalizer import NormalizerAgent
        from .agents.comparator import ComparisonEngine
        from .agents.recommender import RecommendationAgent

        parser_agent = None
        normalizer_agent = None
        try:
            parser_agent = ParserAgent()
            normalizer_agent = NormalizerAgent()
        except ValueError:
            logger.warning("No LLM Provider active. Skipping AI pipeline.")

        # Phase 1: Store all search results + raw markdown first (fast, no LLM)
        result_pairs = []
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
            result_pairs.append((search_result, raw_md, item))

        # Phase 2+3: Parse and normalize all results in parallel
        search_query.status = "parsing"
        search_query.save(update_fields=["status"])

        normalized_products = []

        if parser_agent:
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(result_pairs), 5)) as executor:
                futures = {
                    executor.submit(
                        _parse_and_normalize,
                        parser_agent, normalizer_agent,
                        sr, rm, it,
                    ): it.url
                    for sr, rm, it in result_pairs
                }
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            normalized_products.append(result)
                    except Exception as e:
                        logger.error(f"Parse/normalize failed for {futures[future]}: {e}")

        # Pre-Comparison Filter: Drop poorly parsed products with 0 price to avoid AI confusion
        # (We explicitly do NOT drop out-of-stock items, allowing the AI to notify the user they exist but are unavailable)
        valid_normalized_products = []
        for p in normalized_products:
            price_amount = p.get("normalized_price", {}).get("amount")
            if price_amount and float(price_amount) > 0:
                valid_normalized_products.append(p)

        # Phase 4: Compare (query-level, not per-result)
        if len(valid_normalized_products) >= 1:
            search_query.status = "comparing"
            search_query.save(update_fields=["status"])

            try:
                comparator = ComparisonEngine()
                comparison_data = comparator.compare(valid_normalized_products)
                ComparisonResult.objects.create(
                    search_query=search_query,
                    data=comparison_data,
                )

                # Phase 5: Recommend
                search_query.status = "recommending"
                search_query.save(update_fields=["status"])

                try:
                    recommender = RecommendationAgent()
                    recommendation_data = recommender.recommend(comparison_data, persona=persona)
                    Recommendation.objects.create(
                        search_query=search_query,
                        data=recommendation_data,
                    )
                except Exception as e:
                    logger.error(f"Recommendation failed: {e}")

            except Exception as e:
                logger.error(f"Comparison failed: {e}")

        # Final: Mark complete
        search_query.status = "completed"
        search_query.completed_at = timezone.now()
        search_query.save(update_fields=["status", "completed_at"])

        logger.info(
            f"Pipeline completed: '{query}' — {len(response.results)} results, "
            f"{len(normalized_products)} normalized, comparison + recommendation done"
        )

    except Exception as exc:
        logger.exception(f"Pipeline failed for '{query}'")
        search_query.status = "failed"
        search_query.error_message = str(exc)
        search_query.save(update_fields=["status", "error_message"])

    return search_query
