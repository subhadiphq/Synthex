"""
Synthex Auth Middleware
Validates sx-... API keys on protected endpoints.
"""

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.key_service import key_service
from app.models.database import APIKey

bearer_scheme = HTTPBearer(auto_error=False)


async def require_api_key(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> APIKey:
    """
    Dependency: Validate Bearer token as Synthex API key.
    Usage: key: APIKey = Depends(require_api_key)
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "type": "authentication_error",
                    "message": "API key required. Include 'Authorization: Bearer sx-...' header.",
                    "docs": "https://synthex.ai/docs#authentication",
                }
            },
        )

    token = credentials.credentials
    is_valid, error_msg, key_obj = await key_service.validate_key(db, token)

    if not is_valid:
        raise HTTPException(
            status_code=401 if "Invalid" in error_msg else 429,
            detail={
                "error": {
                    "type": "authentication_error" if "Invalid" in error_msg else "rate_limit_error",
                    "message": error_msg,
                    "docs": "https://synthex.ai/docs",
                }
            },
        )

    return key_obj


async def optional_api_key(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Optional auth — for endpoints that work with or without key."""
    if not credentials:
        return None
    _, _, key_obj = await key_service.validate_key(db, credentials.credentials)
    return key_obj
