"""
POST /v1/finance — Finance & Trading Intelligence
Dedicated endpoint for financial analysis with mandatory safety checks.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List

from app.models.request import Message
from app.models.database import APIKey
from app.api.middleware.auth import require_api_key
from app.database import get_db
from app.agents.specialized import (
    macro_agent, technical_agent, crypto_agent,
    portfolio_agent, finance_safety_agent
)
from app.agents.base import AgentResult
import asyncio, time, uuid

router = APIRouter()


class FinanceRequest(BaseModel):
    query: str
    analysis_type: str = "general"  # general | macro | technical | crypto | portfolio
    data: Optional[str] = None  # User-provided market data
    max_tokens: int = 1500


class FinanceResponse(BaseModel):
    id: str
    analysis_type: str
    response: str
    agents_used: List[str]
    disclaimer: str
    latency_ms: int


DISCLAIMER = (
    "⚠️ DISCLAIMER: This is educational analysis only, not financial advice. "
    "Synthex is not a licensed financial advisor. Always consult a qualified "
    "financial professional before making investment decisions. Past analysis "
    "does not guarantee future results."
)


@router.post("/finance", response_model=FinanceResponse)
async def finance_analysis(
    request: FinanceRequest,
    key: APIKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
):
    """
    Finance intelligence endpoint.
    Runs specialized finance agents with mandatory safety checks.
    """
    if key.plan == "free":
        raise HTTPException(
            status_code=403,
            detail={"error": {"type": "plan_error",
                              "message": "Finance AI requires Pro plan. Upgrade at synthex.ai/upgrade"}}
        )

    start = time.time()
    messages = [Message(role="user", content=request.query +
                        (f"\n\nProvided data:\n{request.data}" if request.data else ""))]

    # Select agent based on type
    agent_map = {
        "macro": macro_agent,
        "technical": technical_agent,
        "crypto": crypto_agent,
        "portfolio": portfolio_agent,
        "general": macro_agent,
    }
    primary_agent = agent_map.get(request.analysis_type, macro_agent)
    task = f"Analyze: {request.query}"

    # Run primary agent
    result: AgentResult = await primary_agent.run(messages, task, max_tokens=request.max_tokens)

    # Always run safety check
    raw_content = result.output if result.success else "Analysis unavailable."
    try:
        is_safe, safe_content, flags = await finance_safety_agent.check(raw_content)
    except Exception:
        is_safe, safe_content, flags = True, raw_content, []

    final_content = safe_content if not is_safe else raw_content
    # Always append disclaimer
    if DISCLAIMER not in final_content:
        final_content += f"\n\n{DISCLAIMER}"

    return FinanceResponse(
        id=f"fin-{uuid.uuid4().hex[:12]}",
        analysis_type=request.analysis_type,
        response=final_content,
        agents_used=[primary_agent.agent_id, "finance_safety"],
        disclaimer=DISCLAIMER,
        latency_ms=int((time.time() - start) * 1000),
    )
