"""
NVIDIA NIM Provider
47+ free enterprise-grade models.
Used for: coding (Qwen3-Coder-480B), safety checks, embeddings.
"""

import json
from typing import AsyncGenerator, List, Optional
from app.providers.base import BaseProvider, ProviderError
from app.models.request import Message
from app.config import settings


class NVIDIAProvider(BaseProvider):
    name = "nvidia"
    base_url = settings.NVIDIA_BASE_URL

    def __init__(self):
        super().__init__()
        self.api_key = settings.NVIDIA_API_KEY
        self.timeout = 45  # Larger models need more time

    async def chat(
        self,
        messages: List[Message],
        model: str = "qwen/qwen3-coder-480b-a35b-instruct",
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
        model: str = "qwen/qwen3-coder-480b-a35b-instruct",
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

    async def safety_check(self, content: str) -> tuple[bool, str]:
        """
        Check content safety using NVIDIA nemotron-content-safety.
        Returns: (is_safe, reason)
        """
        try:
            from app.models.request import Message as Msg
            response, _, _ = await self.chat(
                messages=[Msg(role="user", content=content)],
                model="nvidia/llama-3.1-nemotron-nano-8b-v1",
                system_prompt="You are a content safety classifier. Respond with only 'SAFE' or 'UNSAFE: <reason>'.",
                max_tokens=100,
                temperature=0.0,
            )
            if response.upper().startswith("UNSAFE"):
                return False, response
            return True, "safe"
        except Exception:
            return True, "check_failed"  # Fail open


NVIDIA_MODELS = {
    "coder": "qwen/qwen3-coder-480b-a35b-instruct",
    "safety": "nvidia/llama-3.1-nemotron-nano-8b-v1",
    "reasoning": "nvidia/llama-3.3-nemotron-super-49b-v1",
    "general": "meta/llama-3.3-70b-instruct",
}
