"""
OpenRouter Provider
Access to 25+ free models via a single API key.
Free models: Llama-3.3-70B, Gemma, Qwen, GPT-oss, etc.
"""

import json
from typing import AsyncGenerator, List, Optional
from app.providers.base import BaseProvider, ProviderError
from app.models.request import Message
from app.config import settings


class OpenRouterProvider(BaseProvider):
    name = "openrouter"
    base_url = settings.OPENROUTER_BASE_URL

    def __init__(self):
        super().__init__()
        self.api_key = settings.OPENROUTER_API_KEY

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://synthex.ai",
            "X-Title": "Synthex AI Platform",
        }

    async def chat(
        self,
        messages: List[Message],
        model: str = "meta-llama/llama-3.3-70b-instruct:free",
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

            if "error" in data:
                raise ProviderError(self.name, data["error"].get("message", "Unknown error"))

            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            return content, input_tokens, output_tokens

        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(self.name, str(e))

    async def stream(
        self,
        messages: List[Message],
        model: str = "meta-llama/llama-3.3-70b-instruct:free",
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


# Free models available on OpenRouter
FREE_MODELS = {
    "general": "meta-llama/llama-3.3-70b-instruct:free",
    "fast": "google/gemma-3-9b-it:free",
    "research": "google/gemma-3-27b-it:free",
    "reasoning": "openai/gpt-4o:free",  # when available
    "coding": "qwen/qwen3-coder-480b-a35b-instruct:free",
}
