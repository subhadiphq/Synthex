"""
Base Provider — Abstract class for all AI providers.
All providers (OpenRouter, Groq, NVIDIA, DeepSeek, etc.) extend this.
"""

import time
import httpx
from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Optional
from app.models.request import Message


class ProviderError(Exception):
    """Raised when a provider call fails."""
    def __init__(self, provider: str, message: str, status_code: int = 500):
        self.provider = provider
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{provider}] {message}")


class BaseProvider(ABC):
    """Abstract base for all AI providers."""

    name: str = "base"
    base_url: str = ""
    api_key: str = ""
    timeout: int = 30

    def __init__(self):
        self._client = None

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    async def chat(
        self,
        messages: List[Message],
        model: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> tuple[str, int, int]:
        """
        Send chat completion request.
        Returns: (response_text, input_tokens, output_tokens)
        """
        raise NotImplementedError

    async def stream(
        self,
        messages: List[Message],
        model: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """Stream tokens."""
        raise NotImplementedError

    def _build_messages(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
    ) -> list:
        """Build message list for OpenAI-compatible API."""
        result = []
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        for msg in messages:
            result.append({"role": msg.role, "content": msg.content})
        return result

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
