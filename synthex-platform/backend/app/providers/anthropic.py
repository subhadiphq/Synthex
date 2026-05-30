"""
Anthropic Claude Provider
Used for: premium synthesis, content writing (Pro plan).
Most expensive — only used when truly needed.
"""

import json
from typing import AsyncGenerator, List, Optional
from app.providers.base import BaseProvider, ProviderError
from app.models.request import Message
from app.config import settings


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    base_url = "https://api.anthropic.com"
    timeout = 40

    def __init__(self):
        super().__init__()
        self.api_key = settings.ANTHROPIC_API_KEY

    @property
    def headers(self) -> dict:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    async def chat(
        self,
        messages: List[Message],
        model: str = "claude-haiku-4-5",
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> tuple[str, int, int]:
        if not self.api_key:
            raise ProviderError(self.name, "No Anthropic API key configured")

        client = await self._get_client()

        # Build Anthropic-format messages
        anthropic_messages = [
            {"role": m.role, "content": m.content}
            for m in messages if m.role != "system"
        ]

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": anthropic_messages,
            "temperature": temperature,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = await client.post("/v1/messages", json=payload)
            if response.status_code != 200:
                raise ProviderError(self.name, f"HTTP {response.status_code}: {response.text[:200]}")

            data = response.json()
            content = data["content"][0]["text"]
            usage = data.get("usage", {})
            return content, usage.get("input_tokens", 0), usage.get("output_tokens", 0)

        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(self.name, str(e))


ANTHROPIC_MODELS = {
    "haiku": "claude-haiku-4-5",       # Fast, cheap
    "sonnet": "claude-sonnet-4-5-20250514",     # Best balance
}
