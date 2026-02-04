"""
Phase 5: Recommendation Agent

Takes the comparison matrix and generates human-friendly, actionable insights.

Instead of raw data tables, produces natural language recommendations like:
  "BestBuy is $10 cheaper, but Amazon offers free shipping and easier returns.
   Overall recommendation: Amazon offers the better value."
"""

import json
import logging
from typing import Dict, Any
from ..providers.registry import get_llm_provider
from ..providers.gemini import safe_json_parse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a shopping recommendation advisor for a product intelligence platform.

INPUT: A structured comparison matrix of multiple sellers for the same product.
OUTPUT: Human-friendly, actionable shopping recommendations.

RULES:
1. Be concise but insightful.
2. Always explain WHY you recommend something — don't just state facts.
3. Consider price, shipping, availability, ratings, and specs.
4. If data is missing for some sellers, mention it as a caveat.
5. Use a friendly, professional tone.
6. Highlight deals, warnings, and trade-offs.
7. Provide a "confidence_score" integer (1-10) indicating how confident you are in your "best pick" based on the data provided.

OUTPUT FORMAT (JSON only):
{
  "summary": "<1-2 sentence executive summary>",
  "best_pick": {
    "seller": "",
    "reason": ""
  },
  "budget_pick": {
    "seller": "",
    "reason": ""
  },
  "insights": [
    "<insight 1>",
    "<insight 2>",
    "<insight 3>"
  ],
  "warnings": [
    "<warning if any>"
  ],
  "verdict": "<final 2-3 sentence verdict>",
  "confidence_score": <int 1-10>
}
"""


class RecommendationAgent:
    def __init__(self):
        self.llm = get_llm_provider()

    def recommend(self, comparison_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates recommendations from the comparison matrix.
        """
        if not comparison_data or comparison_data.get("error"):
            return {
                "summary": "Unable to generate recommendations due to insufficient data.",
                "insights": [],
                "warnings": ["Comparison data was incomplete or errored."],
                "verdict": "Please try again with a different search query.",
            }

        prompt = f"Comparison Matrix:\n{json.dumps(comparison_data, indent=2, default=str)}"

        try:
            logger.info("RecommendationAgent generating insights")
            response_text = self.llm.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)

            return safe_json_parse(response_text, fallback={
                "summary": "Recommendation generation encountered a parsing error.",
                "insights": [],
                "warnings": ["The AI output could not be parsed."],
                "verdict": "Please try your search again.",
            })

        except Exception as e:
            logger.exception("RecommendationAgent failed")
            return {
                "summary": "Recommendation generation failed.",
                "insights": [],
                "warnings": [str(e)],
                "verdict": "An unexpected error occurred.",
            }
