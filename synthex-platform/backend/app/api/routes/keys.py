"""API Key management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.request import CreateKeyRequest, APIKeyResponse
from app.models.database import APIKey
from app.api.middleware.auth import require_api_key
from app.database import get_db
from app.services.key_service import key_service

router = APIRouter()

@router.post("/keys", response_model=APIKeyResponse)
async def create_api_key(request: CreateKeyRequest, db: AsyncSession = Depends(get_db)):
    """Create a new API key. Returns the full key ONCE — save it immediately."""
    key = await key_service.create_key(db, request.name, request.email, request.plan)
    return APIKeyResponse(
        id=key.id, key=key.key, name=key.name, email=key.email,
        plan=key.plan, is_active=key.is_active,
        monthly_limit=key.monthly_limit, monthly_used=key.monthly_used,
        created_at=key.created_at,
    )

@router.get("/keys/me")
async def get_my_key(key: APIKey = Depends(require_api_key)):
    """Get info about the current API key."""
    return {
        "id": key.id,
        "key_preview": key.key[:8] + "..." + key.key[-4:],
        "name": key.name, "plan": key.plan,
        "is_active": key.is_active,
        "monthly_limit": key.monthly_limit,
        "monthly_used": key.monthly_used,
        "total_requests": key.total_requests,
        "created_at": key.created_at,
    }

@router.delete("/keys/{key_id}")
async def revoke_key(key_id: str, key: APIKey = Depends(require_api_key), db: AsyncSession = Depends(get_db)):
    """Revoke an API key."""
    if key.id != key_id:
        raise HTTPException(status_code=403, detail="Cannot revoke another key")
    success = await key_service.revoke_key(db, key_id)
    return {"revoked": success}
