"""
OpenAI Provider — GPT-4o-mini
Used for: code review/verification, structured output, fallback.
Cost: ~$0.00015/1K input — cheapest paid option.
"""
import json
from typing import AsyncGenerator, List, Optional
from app.providers.base import BaseProvider, ProviderError
from app.models.request import Message
from app.config import settings


class OpenAIProvider(BaseProvider):
    name = "openai"
    base_url = "https://api.openai.com"
    timeout = 30

    def __init__(self):
        super().__init__()
        self.api_key = settings.OPENAI_API_KEY

    async def chat(self, messages: List[Message], model: str = "gpt-4o-mini",
                   system_prompt: Optional[str] = None, max_tokens: int = 2000,
                   temperature: float = 0.7) -> tuple[str, int, int]:
        client = await self._get_client()
        payload = {
            "model": model,
            "messages": self._build_messages(messages, system_prompt),
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        try:
            response = await client.post("/v1/chat/completions", json=payload)
            if response.status_code != 200:
                raise ProviderError(self.name, f"HTTP {response.status_code}: {response.text[:200]}")
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return content, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(self.name, str(e))

    async def stream(self, messages: List[Message], model: str = "gpt-4o-mini",
                     system_prompt: Optional[str] = None, max_tokens: int = 2000,
                     temperature: float = 0.7) -> AsyncGenerator[str, None]:
        client = await self._get_client()
        payload = {"model": model, "messages": self._build_messages(messages, system_prompt),
                   "max_tokens": max_tokens, "temperature": temperature, "stream": True}
        async with client.stream("POST", "/v1/chat/completions", json=payload) as response:
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

OPENAI_MODELS = {
    "fast": "gpt-4o-mini",
    "smart": "gpt-4o",
}
