"""
Groq Provider — Powered by LPU chips
World's fastest inference. Used for synthex-nova-swift.
Free tier: generous rate limits.
"""

import json
from typing import AsyncGenerator, List, Optional
from app.providers.base import BaseProvider, ProviderError
from app.models.request import Message
from app.config import settings


class GroqProvider(BaseProvider):
    name = "groq"
    base_url = settings.GROQ_BASE_URL

    def __init__(self):
        super().__init__()
        self.api_key = settings.GROQ_API_KEY

    async def chat(
        self,
        messages: List[Message],
        model: str = "llama-3.1-8b-instant",
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> tuple[str, int, int]:
        client = await self._get_client()

        payload = {
            "model": model,
            "messages": self._build_messages(messages, system_prompt),
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response = await client.post("/chat/completions", json=payload)
            if response.status_code != 200:
                raise ProviderError(self.name, f"HTTP {response.status_code}: {response.text[:200]}", response.status_code)

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return content, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)

        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(self.name, str(e))

    async def stream(
        self,
        messages: List[Message],
        model: str = "llama-3.1-8b-instant",
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        client = await self._get_client()

        payload = {
            "model": model,
            "messages": self._build_messages(messages, system_prompt),
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }

        async with client.stream("POST", "/chat/completions", json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError):
                        continue


# Available Groq models
GROQ_MODELS = {
    "flash": "llama-3.1-8b-instant",        # Fastest — synthex-nova-swift
    "pro": "llama-3.3-70b-versatile",       # High quality
    "specdec": "llama-3.3-70b-specdec",     # Speculative decoding
}
