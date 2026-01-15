"""
Gemini implementation of LLMProvider.
We use the REST API approach for compatibility and robustness without heavy SDKs.
"""

import logging
import requests
import json
import os
from typing import Optional

from .base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """
    Uses Gemini API for structured generation via JSON schema.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required.")
        self.api_key = api_key
        self.model = model
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Sends the text to Gemini. Since Phase 2 demands JSON Extraction, 
        we instruct the model heavily to return standard JSON.
        """
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "response_mime_type": "application/json",
            }
        }

        try:
            res = requests.post(
                self.url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
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

