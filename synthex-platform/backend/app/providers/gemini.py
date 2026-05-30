"""
Google Gemini Provider
Best for: research, long-context (1M tokens), health AI.
Free tier is very generous.
"""

import json
import httpx
from typing import List, Optional
from app.providers.base import BaseProvider, ProviderError
from app.models.request import Message
from app.config import settings


class GeminiProvider(BaseProvider):
    name = "gemini"
    base_url = "https://generativelanguage.googleapis.com"
    timeout = 30

    def __init__(self):
        super().__init__()
        self.api_key = settings.GEMINI_API_KEY

    async def chat(
        self,
        messages: List[Message],
        model: str = "gemini-1.5-flash",
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> tuple[str, int, int]:
        """Call Gemini API with native format."""
        if not self.api_key:
            raise ProviderError(self.name, "No Gemini API key configured")

        # Build Gemini-format messages
        contents = []
        for msg in messages:
            role = "user" if msg.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg.content}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }

        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        url = f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)

            if response.status_code != 200:
                raise ProviderError(self.name, f"HTTP {response.status_code}: {response.text[:200]}")

            data = response.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            usage = data.get("usageMetadata", {})
            in_tok = usage.get("promptTokenCount", 0)
            out_tok = usage.get("candidatesTokenCount", 0)
            return content, in_tok, out_tok

        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(self.name, str(e))


GEMINI_MODELS = {
    "flash": "gemini-1.5-flash",   # Fast, free
    "pro": "gemini-1.5-pro",       # Best quality, 1M context
    "flash2": "gemini-2.0-flash",  # Latest
}
