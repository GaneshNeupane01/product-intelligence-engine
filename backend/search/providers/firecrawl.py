"""
Firecrawl implementation of SearchProvider.

This utilizes a two-step process to prevent duplicate domains:
1. Hit /v1/search (no scrape) with a larger limit to get metadata and URLs.
2. Filter the results so that there is only 1 result per domain.
3. Hit /v1/scrape concurrently via ThreadPoolExecutor for the distinct URLs.
"""

import logging
import requests
import concurrent.futures
from urllib.parse import urlparse
from typing import Optional, List, Dict, Any

from .base import SearchProvider, SearchResponse, SearchResultItem

logger = logging.getLogger(__name__)

FIRECRAWL_SEARCH_URL = "https://api.firecrawl.dev/v1/search"
FIRECRAWL_SCRAPE_URL = "https://api.firecrawl.dev/v1/scrape"


class FirecrawlSearchProvider(SearchProvider):
    """
    Search and Scrape orchestrator using Firecrawl.
    Ensures that we don't scrape multiple pages from the exact same site,
    maximizing diverse product sourcing.
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Firecrawl API key is required")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _get_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc.replace("www.", "").lower()
        except Exception:
            return url

    def _scrape_url(self, item: Dict[str, Any]) -> Optional[SearchResultItem]:
        url = item.get("url")
        if not url:
            return None
            
        logger.info(f"Scraping {url}...")
        
        # We optimize scrape options to get the purest body content available
        scrape_payload = {
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": True,
            "excludeTags": [
                "nav", "footer", "aside", "header", "script", "style", 
                "noscript", "svg", "button", "iframe", "img"
            ],
        }

        try:
            res = requests.post(
                FIRECRAWL_SCRAPE_URL,
                headers=self.headers,
                json=scrape_payload,
                timeout=60,
            )
            res.raise_for_status()
            data = res.json()
            
            scraped_data = data.get("data", {})
            markdown = scraped_data.get("markdown", "")
            
            if not markdown:
                return None
                
            return SearchResultItem(
                url=url,
                title=item.get("title") or scraped_data.get("metadata", {}).get("title") or "",
                description=item.get("description", ""),
                markdown=markdown,
                metadata=scraped_data.get("metadata", {}),
            )
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    def search(self, query: str, limit: int = 5) -> SearchResponse:
        # PRO APPROACH:
        # 1. Fetch a naturally ranked, robust pool of metadata results from the search engine.
        # 2. Python-level Post-filtering: By NOT forcefully appending `-site:` operators to the query, 
        #    we allow the search algorithm to use its native semantic relevance. 
        #    We then safely strip out the noise (YouTube, Instagram) and duplicates locally.
        search_limit = max(limit * 4, 15)
        
        excluded_domains = [
            "youtube.com", "youtu.be", "facebook.com", "twitter.com", 
            "instagram.com", "reddit.com", "wikipedia.org", "tiktok.com", 
            "pinterest.com", "linkedin.com", "x.com", "news.google.com",
            "quora.com", "medium.com"
        ]

        search_payload = {
            "query": query,
            "limit": search_limit,
            # Omitting scrapeOptions keeps it a fast metadata-only search
        }

        try:
            logger.info(f"Firecrawl search (metadata only): query='{query}', mapping top {search_limit} URLs")
            response = requests.post(
                FIRECRAWL_SEARCH_URL,
                headers=self.headers,
                json=search_payload,
                timeout=30,
            )
            response.raise_for_status()
            search_data = response.json()
            
            # Step 2: Extract distinct domains up to the requested 'limit'
            raw_items = search_data.get("data", [])
            unique_items = []
            seen_domains = set()
            
            for item in raw_items:
                url = item.get("url", "")
                domain = self._get_domain(url)
                
                # Check for completely invalid domains or if an excluded domain leaked through
                if not domain or any(ex in domain for ex in excluded_domains):
                    continue
                    
                if domain not in seen_domains:
                    seen_domains.add(domain)
                    unique_items.append(item)
                    if len(unique_items) == limit:
                        break
                        
            logger.info(f"Found {len(unique_items)} unique retail/blog domains for processing (target was {limit}).")
            
            # Step 3: Concurrently scrape the unique domains
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=limit) as executor:
                futures = {executor.submit(self._scrape_url, item): item for item in unique_items}
                
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        results.append(result)

            # Sort results to broadly maintain the initial search ranking order
            url_order = {item["url"]: idx for idx, item in enumerate(unique_items)}
            results.sort(key=lambda r: url_order.get(r.url, 999))

            logger.info(f"Successfully finished scraping {len(results)} distinct pages.")
            return SearchResponse(
                query=query,
                results=results,
                provider="firecrawl",
                success=True,
            )

        except requests.exceptions.Timeout:
            logger.error("Firecrawl request timed out")
            return SearchResponse(
                query=query,
                provider="firecrawl",
                success=False,
                error="Search request timed out. Please try again.",
            )
        except requests.exceptions.HTTPError as exc:
            error_msg = str(exc)
            try:
                error_data = exc.response.json()
                error_msg = error_data.get("error", error_msg)
            except Exception:
                pass
            logger.error(f"Firecrawl HTTP error: {error_msg}")
            return SearchResponse(
                query=query,
                provider="firecrawl",
                success=False,
                error=f"Search API error: {error_msg}",
            )
        except Exception as exc:
            logger.exception("Unexpected Firecrawl error")
            return SearchResponse(
                query=query,
                provider="firecrawl",
                success=False,
                error=f"Unexpected error: {str(exc)}",
            )
