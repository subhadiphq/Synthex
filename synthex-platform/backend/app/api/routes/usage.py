"""Usage statistics and request history endpoint."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional
from app.models.database import APIKey, UsageLog
from app.api.middleware.auth import require_api_key
from app.database import get_db
from app.services.key_service import key_service

router = APIRouter()


@router.get("/usage")
async def get_usage(
    key: APIKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Get usage statistics for current API key."""
    stats = await key_service.get_usage_stats(db, key)
    return {
        "key_id": str(key.id),
        "name": key.name,
        "plan": key.plan,
        "usage": stats,
        "key_created": key.created_at.isoformat() if key.created_at else None,
        "last_used": key.last_used_at.isoformat() if key.last_used_at else None,
    }


@router.get("/usage/logs")
async def get_usage_logs(
    key: APIKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Get recent request logs for current API key."""
    result = await db.execute(
        select(UsageLog)
        .where(UsageLog.api_key_id == key.id)
        .order_by(desc(UsageLog.created_at))
        .limit(limit)
    )
    logs = result.scalars().all()
    return {
        "total": len(logs),
        "recent": [
            {
                "id": str(log.id),
                "model": log.model,
                "provider": log.provider,
                "input_tokens": log.input_tokens,
                "output_tokens": log.output_tokens,
                "total_tokens": log.total_tokens,
                "cost_usd": round(log.cost_usd, 6),
                "latency_ms": log.latency_ms,
                "agents_used": log.agents_used,
                "success": log.success,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }
