"""
Phase 3: Specification Normalizer Agent

Takes parsed product JSON from multiple sites and normalizes inconsistent
specification formats into a unified schema.

Examples:
    "16 GB" / "16GB" / "16 Gigabytes" / "16G RAM"  →  {"ram": "16 GB"}
    "6.7 inch" / '6.7"' / "6.7-inch AMOLED"       →  {"display_size": "6.7 inches"}
"""

import json
import logging
from typing import Dict, Any, List
from ..providers.registry import get_llm_provider
from ..providers.gemini import safe_json_parse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a specification normalization engine for a product intelligence platform.

INPUT: A product's raw "specifications" object extracted from a website.
OUTPUT: A normalized specifications object with standardized keys and values.

RULES:
1. Standardize all keys to snake_case (e.g. "Display Size" → "display_size")
2. Standardize units:
   - RAM/Storage: always "X GB" or "X TB" (with space)
   - Display: "X inches"  
   - Battery: "X mAh"
   - Weight: "X g" or "X kg"
   - Resolution: "WxH" (e.g. "1920x1080")
   - Refresh Rate: "X Hz"
   - Frequency/Clock: "X GHz"
3. Remove marketing fluff. Keep only factual specs.
4. If a spec key is unclear, use the most standard name (e.g. "Proc" → "processor")
5. Group related specs logically.

ALSO PRODUCE a "normalized_price" object:
{
  "amount": <number or null>,
  "currency": "<3-letter ISO code or original>",
  "original_amount": <number or null>
}
- Parse price strings like "NPR 28,999" or "$599.99" or "Rs 1,08,000" into numeric amount + currency.

OUTPUT FORMAT (JSON only):
{
  "normalized_specs": {
    "key": "value"
  },
  "normalized_price": {
    "amount": 0,
    "currency": "",
    "original_amount": null
  }
}
"""


class NormalizerAgent:
    def __init__(self):
        self.llm = get_llm_provider()

    def normalize(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes a single parsed product's specifications and price.
        Returns dict with "normalized_specs" and "normalized_price".
        """
        specs = parsed_data.get("specifications", {})
        price = parsed_data.get("price", {})
        title = parsed_data.get("title", "")

        if not specs and not price:
            return {"normalized_specs": {}, "normalized_price": {}}

        prompt = f"""Product: {title}

Raw Specifications:
{json.dumps(specs, indent=2)}

Raw Price Object:
{json.dumps(price, indent=2)}
"""
        try:
            logger.info(f"NormalizerAgent running for: {title}")
            response_text = self.llm.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)

            result = safe_json_parse(response_text, fallback={})
            return {
                "normalized_specs": result.get("normalized_specs", {}),
                "normalized_price": result.get("normalized_price", {}),
            }
        except Exception as e:
            logger.exception("NormalizerAgent failed")
            return {"normalized_specs": specs, "normalized_price": price}
