"""
Synthex API Key Service
Handles key generation, validation, rate limiting, and usage tracking.
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.database import APIKey, UsageLog
from app.config import settings


class APIKeyService:

    async def create_key(
        self,
        db: AsyncSession,
        name: str,
        email: str,
        plan: str = "free",
    ) -> APIKey:
        """Create a new API key."""
        monthly_limit = settings.FREE_MONTHLY if plan == "free" else 999999

        key = APIKey(
            name=name,
            email=email,
            plan=plan,
            monthly_limit=monthly_limit,
            reset_at=datetime.utcnow() + timedelta(days=30),
        )
        db.add(key)
        await db.flush()
        await db.refresh(key)
        return key

    async def get_key(self, db: AsyncSession, api_key: str) -> Optional[APIKey]:
        """Look up API key."""
        result = await db.execute(
            select(APIKey).where(APIKey.key == api_key, APIKey.is_active == True)
        )
        return result.scalar_one_or_none()

    async def validate_key(
        self, db: AsyncSession, api_key: str
    ) -> tuple[bool, str, Optional[APIKey]]:
        """
        Validate API key and check limits.
        Returns: (is_valid, error_message, key_object)
        """
        if not api_key or not api_key.startswith("sx-"):
            return False, "Invalid API key format. Keys must start with 'sx-'", None

        key_obj = await self.get_key(db, api_key)
        if not key_obj:
            return False, "Invalid or revoked API key", None

        # Check monthly limit
        await self._maybe_reset_monthly(db, key_obj)

        if key_obj.monthly_used >= key_obj.monthly_limit:
            return (
                False,
                f"Monthly limit reached ({key_obj.monthly_limit} syntheses). Upgrade to Pro for unlimited access.",
                None,
            )

        return True, "", key_obj

    async def record_usage(
        self,
        db: AsyncSession,
        key_obj: APIKey,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: int,
        agents_used: list,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """Record usage after a successful request."""
        log = UsageLog(
            api_key_id=key_obj.id,
            model=model,
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            agents_used=",".join(agents_used),
            success=success,
            error_message=error,
        )
        db.add(log)

        # Update key stats
        await db.execute(
            update(APIKey)
            .where(APIKey.id == key_obj.id)
            .values(
                monthly_used=APIKey.monthly_used + 1,
                total_requests=APIKey.total_requests + 1,
                total_tokens=APIKey.total_tokens + input_tokens + output_tokens,
                total_cost_usd=APIKey.total_cost_usd + cost_usd,
                last_used_at=datetime.utcnow(),
            )
        )

    async def get_usage_stats(self, db: AsyncSession, key_obj: APIKey) -> dict:
        """Get usage statistics for an API key."""
        return {
            "total_requests": key_obj.total_requests,
            "total_tokens": key_obj.total_tokens,
            "total_cost_usd": round(key_obj.total_cost_usd, 6),
            "monthly_used": key_obj.monthly_used,
            "monthly_limit": key_obj.monthly_limit,
            "plan": key_obj.plan,
            "reset_at": key_obj.reset_at.isoformat() if key_obj.reset_at else None,
        }

    async def revoke_key(self, db: AsyncSession, key_id: str) -> bool:
        """Revoke an API key."""
        result = await db.execute(
            update(APIKey).where(APIKey.id == key_id).values(is_active=False)
        )
        return result.rowcount > 0

    async def _maybe_reset_monthly(self, db: AsyncSession, key_obj: APIKey):
        """Reset monthly usage counter if month has passed."""
        if key_obj.reset_at and datetime.utcnow() > key_obj.reset_at:
            await db.execute(
                update(APIKey)
                .where(APIKey.id == key_obj.id)
                .values(
                    monthly_used=0,
                    reset_at=datetime.utcnow() + timedelta(days=30),
                )
            )
            key_obj.monthly_used = 0


key_service = APIKeyService()
