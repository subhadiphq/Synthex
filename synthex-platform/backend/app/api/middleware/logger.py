"""Request logging middleware."""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        ms = int((time.time() - start) * 1000)
        print(f"[{response.status_code}] {request.method} {request.url.path} — {ms}ms")
        response.headers["X-Response-Time"] = f"{ms}ms"
        response.headers["X-Powered-By"] = "Synthex"
        return response
