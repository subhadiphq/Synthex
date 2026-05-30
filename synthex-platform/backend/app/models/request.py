"""
Synthex API Request/Response Schemas — v1.0
All Pydantic models for every endpoint.
OpenAI-compatible + Synthex native format.
"""
from typing import Optional, List, Literal, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ── Core Message Types ────────────────────────────────────────────────────────

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class MessageResponse(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str


# ── Synthex Native Request/Response ───────────────────────────────────────────

class SynthexRequest(BaseModel):
    model: str = Field(default="synthex-nova-pro")
    prompt: Optional[str] = None
    messages: Optional[List[Message]] = None
    max_tokens: int = Field(default=2000, ge=1, le=8000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    stream: bool = False
    language: str = Field(default="auto", description="auto|en|bn")
    system: Optional[str] = None

    class Config:
        json_schema_extra = {"example": {
            "model": "synthex-nova-pro",
            "messages": [{"role": "user", "content": "Hello Synthex!"}],
            "max_tokens": 1000
        }}

class AgentTrace(BaseModel):
    agent_id: str
    agent_name: str
    provider: str
    model: str
    output: str
    latency_ms: int
    tokens_used: int

class SynthexUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0

class SynthexChoice(BaseModel):
    index: int = 0
    message: MessageResponse
    finish_reason: str = "stop"

class SynthexResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[SynthexChoice]
    usage: SynthexUsage
    system_fingerprint: str = "synthex-v1"
    agents_used: List[str] = []
    agent_traces: Optional[List[AgentTrace]] = None
    synthesis_method: str = "multi-agent"


# ── OpenAI-Compatible ─────────────────────────────────────────────────────────

class ChatCompletionMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completions request."""
    model: str = "synthex-nova-pro"
    messages: List[ChatCompletionMessage] = []
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False
    language: Optional[str] = None
    system: Optional[str] = None

    class Config:
        json_schema_extra = {"example": {
            "model": "synthex-nova-pro",
            "messages": [{"role": "user", "content": "Hello!"}],
            "stream": False
        }}

class OpenAIChatRequest(BaseModel):
    """Alias for backward compatibility."""
    model: str = "synthex-nova-pro"
    messages: List[Message]
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False


# ── API Key Management ────────────────────────────────────────────────────────

class CreateKeyRequest(BaseModel):
    name: str = Field(default="My API Key", max_length=100)
    email: str = Field(..., description="Your email address")
    plan: str = Field(default="free", pattern="^(free|pro|enterprise)$")

class APIKeyResponse(BaseModel):
    id: str
    key: str
    name: str
    email: str
    plan: str
    is_active: bool
    monthly_limit: int
    monthly_used: int
    created_at: datetime
    reset_at: Optional[datetime] = None
    message: str = ""

    class Config:
        from_attributes = True

class APIKeyPublicResponse(BaseModel):
    id: str
    key_preview: str
    name: str
    plan: str
    is_active: bool
    monthly_limit: int
    monthly_used: int
    created_at: datetime


# ── Usage & Stats ─────────────────────────────────────────────────────────────

class UsageStats(BaseModel):
    total_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    monthly_used: int = 0
    monthly_limit: int = 200
    plan: str = "free"
    reset_at: Optional[str] = None


# ── Models List ───────────────────────────────────────────────────────────────

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = 1735000000
    owned_by: str = "synthex"
    description: str = ""
    context_length: int = 128000
    agents: int = 3
    avg_latency: str = "~3s"
    tier: str = "pro"
    plan_required: str = "free"

class ModelsListResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]


# ── Streaming ─────────────────────────────────────────────────────────────────

class StreamDelta(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None

class StreamChoice(BaseModel):
    index: int = 0
    delta: StreamDelta
    finish_reason: Optional[str] = None

class StreamChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoice]
