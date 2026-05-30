"""Synthex Configuration — All settings from environment variables."""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server
    PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    SECRET_KEY: str = "synthex-change-this-in-production-minimum-32-chars"

    # CORS — set ALLOWED_ORIGINS in .env for production
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5500",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        # Add your production frontend URL in .env:
        # ALLOWED_ORIGINS=["https://your-app.vercel.app"]
    ]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./synthex.db"

    # AI Providers
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    GROQ_API_KEY: str = ""
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    NVIDIA_API_KEY: str = ""
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Rate Limits
    FREE_RPM: int = 10
    PRO_RPM: int = 60
    FREE_MONTHLY: int = 200

    # Timeouts (seconds)
    PULSE_TIMEOUT: int = 8
    ARC_TIMEOUT: int = 30
    NEXUS_TIMEOUT: int = 60
    FORGE_TIMEOUT: int = 25

    # Features
    ENABLE_SAFETY_CHECK: bool = True
    ENABLE_CONTEXT_COMPRESSION: bool = True
    ENABLE_CACHING: bool = True
    ENABLE_RATE_LIMITING: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow extra env vars without error
        extra = "ignore"


settings = Settings()
