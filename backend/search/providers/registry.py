"""
Provider registry — returns the correct provider based on environment config.

Usage:
    provider = get_search_provider()
    results  = provider.search("RTX 5070", limit=5)
"""

import os
from .base import SearchProvider, LLMProvider
from .firecrawl import FirecrawlSearchProvider
from .gemini import GeminiProvider

def get_search_provider() -> SearchProvider:
    """
    Factory that returns a SearchProvider instance based on the
    SEARCH_PROVIDER environment variable.
    """
    provider_name = os.getenv("SEARCH_PROVIDER", "firecrawl").lower()

    if provider_name == "firecrawl":
        api_key = os.getenv("FIRECRAWL_API_KEY", "")
        return FirecrawlSearchProvider(api_key=api_key)
    else:
        raise ValueError(
            f"Unknown search provider: '{provider_name}'. "
        )

def get_llm_provider() -> LLMProvider:
    """
    Factory that returns an LLMProvider instance.
    """
    provider_name = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_name == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "")
        return GeminiProvider(api_key=api_key)
    else:
        raise ValueError(f"Unknown LLM provider: '{provider_name}'")

