"""
Phase 4: Comparison Engine

Takes normalized product data from multiple sites and produces a structured
comparison matrix identifying cheapest, best value, best specs, etc.
"""

import json
import logging
from typing import Dict, Any, List
from ..providers.registry import get_llm_provider
from ..providers.gemini import safe_json_parse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a product comparison engine for an e-commerce intelligence platform.

INPUT: A list of normalized products from different sellers (same or similar product).
Each product has: title, seller, normalized_specs, normalized_price, rating, availability, shipping.

OUTPUT: A structured comparison analysis (JSON only).

RULES:
1. Compare ALL products objectively.
2. Identify winners in each category.
3. Flag any missing data rather than guessing.
4. All monetary comparisons must account for currency.

OUTPUT FORMAT:
{
  "product_name": "<canonical product name>",
  "total_sellers": <int>,
  "price_comparison": {
    "cheapest": {"seller": "", "price": 0, "currency": ""},
    "most_expensive": {"seller": "", "price": 0, "currency": ""},
    "average_price": 0,
    "price_range": ""
  },
  "rating_comparison": {
    "highest_rated": {"seller": "", "score": 0, "count": 0},
    "average_rating": 0
  },
  "availability_summary": {
    "in_stock_count": 0,
    "out_of_stock_sellers": []
  },
  "shipping_comparison": {
    "fastest": {"seller": "", "timeframe": ""},
    "free_shipping_sellers": []
  },
  "spec_highlights": {
    "common_specs": {},
    "differences": []
  },
  "value_analysis": {
    "best_value": {"seller": "", "reason": ""},
    "best_overall": {"seller": "", "reason": ""}
  },
  "seller_details": [
    {
      "seller": "",
      "domain": "",
      "price": 0,
      "currency": "",
      "rating": null,
      "in_stock": true,
      "shipping": ""
    }
  ]
}
"""


class ComparisonEngine:
    def __init__(self):
        self.llm = get_llm_provider()

    def compare(self, normalized_products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes a list of normalized product dicts and produces a comparison matrix.
        """
        if not normalized_products:
            return {}

        if len(normalized_products) == 1:
            p = normalized_products[0]
            return {
                "product_name": p.get("title", "Unknown Product"),
                "total_sellers": 1,
                "price_comparison": {
                    "cheapest": {
                        "seller": p.get("seller", {}).get("name", ""),
                        "price": p.get("normalized_price", {}).get("amount", 0),
                        "currency": p.get("normalized_price", {}).get("currency", ""),
                    },
                    "most_expensive": None,
                    "average_price": p.get("normalized_price", {}).get("amount", 0),
                    "price_range": "Single seller",
                },
                "seller_details": [self._build_seller_detail(p)],
                "note": "Only one seller found. Comparison requires multiple sellers.",
            }

        prompt = "Products to compare:\n\n"
        for i, product in enumerate(normalized_products):
            prompt += f"--- Seller {i + 1} ---\n"
            prompt += json.dumps(product, indent=2, default=str)
            prompt += "\n\n"

        try:
            logger.info(f"ComparisonEngine running for {len(normalized_products)} products")
            response_text = self.llm.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)

            return safe_json_parse(response_text, fallback={
                "error": "Failed to parse comparison",
                "raw_products": len(normalized_products),
            })

        except Exception as e:
            logger.exception("ComparisonEngine failed")
            return {"error": str(e)}

    def _build_seller_detail(self, product: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "seller": product.get("seller", {}).get("name", "Unknown"),
            "domain": product.get("seller", {}).get("domain", ""),
            "price": product.get("normalized_price", {}).get("amount", 0),
            "currency": product.get("normalized_price", {}).get("currency", ""),
            "rating": product.get("rating", {}).get("score"),
            "in_stock": product.get("availability", {}).get("in_stock", True),
            "shipping": product.get("shipping", {}).get("timeframe", ""),
        }
