"""
Abstract base classes for provider abstraction.

The application should never depend on a specific provider directly.
Instead, all services depend on these abstract interfaces, and concrete
implementations are injected at runtime based on configuration.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared data models
# ---------------------------------------------------------------------------

class SearchResultItem(BaseModel):
    """A single search result returned by a SearchProvider."""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    markdown: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """The complete response from a search operation."""
    query: str
    results: List[SearchResultItem] = Field(default_factory=list)
    provider: str = ""
    success: bool = True
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Abstract providers
# ---------------------------------------------------------------------------

class SearchProvider(ABC):
    """
    Abstract search provider.
    Implementations must be able to search the web and optionally return
    the scraped markdown content of each result page.
    """

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> SearchResponse:
        """
        Execute a web search for *query* and return up to *limit* results.
        """
        ...


class CrawlerProvider(ABC):
    """
    Abstract crawler provider.
    Given a URL, return its page content as markdown.
    """

    @abstractmethod
    def crawl(self, url: str) -> Optional[str]:
        """Crawl *url* and return markdown content."""
        ...


class LLMProvider(ABC):
    """
    Abstract LLM provider.
    Used for structured extraction, normalization, and recommendations.
    """

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a text completion."""
        ...
