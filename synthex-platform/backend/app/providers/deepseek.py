"""
DeepSeek Provider
GPT-4 quality at 10x cheaper price.
Used for: reasoning (deepseek-r1), synthesis (deepseek-chat-v3).
Cost: ~$0.00014/1K tokens input — cheapest paid option.
"""

import json
from typing import AsyncGenerator, List, Optional
from app.providers.base import BaseProvider, ProviderError
from app.models.request import Message
from app.config import settings


class DeepSeekProvider(BaseProvider):
    name = "deepseek"
    base_url = settings.DEEPSEEK_BASE_URL
    timeout = 40

    def __init__(self):
        super().__init__()
        self.api_key = settings.DEEPSEEK_API_KEY

    async def chat(
        self,
        messages: List[Message],
        model: str = "deepseek-chat",
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> tuple[str, int, int]:
        client = await self._get_client()

        # deepseek-reasoner doesn't support system in messages the same way
        built_messages = self._build_messages(messages, system_prompt)

        payload = {
            "model": model,
            "messages": built_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response = await client.post("/chat/completions", json=payload)
            if response.status_code != 200:
                raise ProviderError(self.name, f"HTTP {response.status_code}: {response.text[:300]}", response.status_code)

            data = response.json()

            if "error" in data:
                raise ProviderError(self.name, data["error"].get("message", "Unknown"))

            content = data["choices"][0]["message"]["content"]

            # For deepseek-reasoner, also extract reasoning_content if present
            reasoning = data["choices"][0]["message"].get("reasoning_content", "")
            if reasoning:
                content = f"[Reasoning]\n{reasoning}\n\n[Answer]\n{content}"

            usage = data.get("usage", {})
            return content, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)

        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(self.name, str(e))

    async def stream(
        self,
        messages: List[Message],
        model: str = "deepseek-chat",
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


DEEPSEEK_MODELS = {
    "chat": "deepseek-chat",         # deepseek-chat-v3 — general purpose
    "reasoner": "deepseek-reasoner", # deepseek-r1 — deep reasoning
}
