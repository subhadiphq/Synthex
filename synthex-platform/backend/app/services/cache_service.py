"""
Synthex Cache Service
Simple in-memory cache for repeated identical requests.
Upgrade to Redis when scale requires.
"""
import hashlib
import time
from typing import Optional


class CacheService:
    def __init__(self, ttl: int = 300):  # 5 min default TTL
        self._cache: dict[str, tuple] = {}  # key -> (value, expires_at)
        self.ttl = ttl

    def _key(self, model: str, messages: list) -> str:
        content = f"{model}:{str(messages)}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, model: str, messages: list) -> Optional[str]:
        key = self._key(model, messages)
        if key in self._cache:
            value, expires_at = self._cache[key]
            if time.time() < expires_at:
                return value
            del self._cache[key]
        return None

    def set(self, model: str, messages: list, response: str):
        key = self._key(model, messages)
        self._cache[key] = (response, time.time() + self.ttl)

    def clear_expired(self):
        now = time.time()
        self._cache = {k: v for k, v in self._cache.items() if v[1] > now}

    def stats(self) -> dict:
        return {"cached_items": len(self._cache)}


cache_service = CacheService()
