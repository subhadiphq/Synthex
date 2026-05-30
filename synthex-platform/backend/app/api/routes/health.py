"""Health check — /health and /ping."""
import time
from fastapi import APIRouter
from app.providers import registry
from app.models.synthex import ALL_MODEL_IDS

router = APIRouter()
_start_time = time.time()


@router.get("/health")
async def health():
    """Full health check with provider status."""
    return {
        "status": "operational",
        "platform": "Synthex AI",
        "series": "NOVA",
        "version": "1.0.0",
        "uptime_seconds": int(time.time() - _start_time),
        "providers_available": registry.available(),
        "models": ALL_MODEL_IDS,
        "agents": 16,
    }


@router.get("/ping")
async def ping():
    """Minimal health check for load balancers."""
    return {"status": "ok", "service": "synthex-api"}
