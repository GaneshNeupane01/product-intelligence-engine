"""
Phase 2: Parser Agent
Extracts structured JSON from raw Markdown using an LLM.
"""

import logging
from typing import Dict, Any
from ..providers.registry import get_llm_provider
from ..providers.gemini import safe_json_parse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert data extraction agent for an e-commerce intelligence platform.
Your ONLY job is to extract product information from the provided raw markdown.
- Do NOT reason, summarize, or evaluate the product.
- Extract exactly what is given.
- Format the output strictly matching the provided JSON schema.
- If a specific field is not found in the markdown, populate it with null, "", or {}.

EXPECTED OUTPUT SCHEMA (JSON only, no markdown blocks):
{
  "title": "",
  "brand": "",
  "model": "",
  "category": "",
  "price": {
     "amount": 0,
     "currency": "",
     "original_amount": null
  },
  "seller": {
     "name": "",
     "domain": ""
  },
  "shipping": {
     "cost": "",
     "timeframe": ""
  },
  "availability": {
     "in_stock": true,
     "stock_count": null
  },
  "specifications": {
     "key": "value"
  },
  "reviews": [],
  "rating": {
     "score": null,
     "out_of": 5,
     "count": null
  },
  "images": []
}
"""

class ParserAgent:
    def __init__(self):
        self.llm = get_llm_provider()

    def parse(self, markdown_content: str, url: str) -> Dict[str, Any]:
        """
        Parses raw markdown into structured JSON.
        """
        if not markdown_content.strip():
            return {}

        prompt = f"Source URL: {url}\n\nRAW MARKDOWN TO EXTRACT:\n{markdown_content}"

        try:
            logger.info(f"ParserAgent running for URL: {url}")
            response_text = self.llm.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)

            structured_data = safe_json_parse(response_text, fallback={})
            if structured_data:
                structured_data["source_url"] = url
            return structured_data

        except Exception as e:
            logger.exception("Error in ParserAgent extraction.")
            return {}
