"""
Synthex Database Models
SQLAlchemy ORM models for all tables.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def generate_api_key() -> str:
    """Generate sx-... format API key."""
    raw = uuid.uuid4().hex + uuid.uuid4().hex
    return f"sx-{raw[:48]}"


class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key: Mapped[str] = mapped_column(String(60), unique=True, index=True, default=generate_api_key)
    name: Mapped[str] = mapped_column(String(100), default="My API Key")
    email: Mapped[str] = mapped_column(String(255), index=True)
    plan: Mapped[str] = mapped_column(String(20), default="free")  # free | pro | enterprise
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    monthly_limit: Mapped[int] = mapped_column(Integer, default=200)
    monthly_used: Mapped[int] = mapped_column(Integer, default=0)
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    reset_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    usage_logs: Mapped[list["UsageLog"]] = relationship(back_populates="api_key", lazy="dynamic")


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    api_key_id: Mapped[str] = mapped_column(String(36), ForeignKey("api_keys.id"), index=True)
    model: Mapped[str] = mapped_column(String(50))           # synthex-nova-pro etc.
    provider: Mapped[str] = mapped_column(String(50))         # openrouter, groq, etc.
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    agents_used: Mapped[str] = mapped_column(String(200), default="")
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    api_key: Mapped["APIKey"] = relationship(back_populates="usage_logs")


class RequestLog(Base):
    __tablename__ = "request_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    api_key_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    endpoint: Mapped[str] = mapped_column(String(200))
    method: Mapped[str] = mapped_column(String(10))
    status_code: Mapped[int] = mapped_column(Integer)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
