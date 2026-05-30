"""
Synthex Rate Limiter
Simple in-memory rate limiting.
Upgrade to Redis when scale requires.
"""
import time
from collections import defaultdict
from app.config import settings


class RateLimiter:
    def __init__(self):
        # {key: [(timestamp), ...]}
        self._windows: dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str, plan: str = "free") -> tuple[bool, int]:
        """
        Check if request is allowed.
        Returns: (allowed, retry_after_seconds)
        """
        rpm = settings.PRO_RPM if plan == "pro" else settings.FREE_RPM
        now = time.time()
        window_start = now - 60  # 1-minute window

        # Clean old entries
        self._windows[key] = [t for t in self._windows[key] if t > window_start]

        if len(self._windows[key]) >= rpm:
            oldest = self._windows[key][0]
            retry_after = int(60 - (now - oldest)) + 1
            return False, retry_after

        self._windows[key].append(now)
        return True, 0

    def get_usage(self, key: str) -> dict:
        """Get current rate limit usage."""
        now = time.time()
        window_start = now - 60
        recent = [t for t in self._windows.get(key, []) if t > window_start]
        return {"requests_in_last_minute": len(recent)}


rate_limiter = RateLimiter()
