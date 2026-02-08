"""
Gemini implementation of LLMProvider.
Uses the REST API with native JSON response mode for guaranteed valid output.
"""

import logging
import requests
import json
from typing import Optional, Dict, Any

from .base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """
    Uses Gemini API with response_mime_type=application/json
    to guarantee structurally valid JSON output.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required.")
        self.api_key = api_key
        self.model = model
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def generate(self, prompt: str, system_prompt: str = "", response_schema: Optional[Dict[str, Any]] = None) -> str:
        """
        Sends the text to Gemini with native JSON mode enabled.
        Optionally passes a response_schema for stricter structured output.
        """
        generation_config = {
            "response_mime_type": "application/json",
        }
        if response_schema:
            generation_config["response_schema"] = response_schema

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": generation_config
        }

        try:
            res = requests.post(
                self.url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=120
            )
            res.raise_for_status()
            data = res.json()

            candidates = data.get("candidates", [])
            if not candidates:
                logger.error(f"Gemini returned no candidates: {data}")
                return "{}"

            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
            return text

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request to Gemini failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise RuntimeError(f"Gemini API failure: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error inside GeminiProvider.generate")
            raise


def safe_json_parse(raw_text: str, fallback: Any = None) -> Any:
    """
    Robustly parse JSON from LLM output. Since Gemini's JSON mode is enabled,
    this should rarely fail — but this handles edge cases like truncated output
    or unexpected wrapping.
    """
    cleaned = raw_text.strip()

    # Strip markdown code fences if present (defensive)
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find a JSON object/array boundary
        for start_char, end_char in [('{', '}'), ('[', ']')]:
            start = cleaned.find(start_char)
            end = cleaned.rfind(end_char)
            if start != -1 and end > start:
                try:
                    return json.loads(cleaned[start:end + 1])
                except json.JSONDecodeError:
                    continue
        logger.warning(f"Failed to parse JSON from LLM output: {cleaned[:200]}")
        return fallback
