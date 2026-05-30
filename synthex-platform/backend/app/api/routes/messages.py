"""
POST /v1/messages  — Synthex native format
POST /v1/synthesize — alias

FIX: api_key_id now passed to pipeline for memory extraction.
FIX: stream() signature includes api_key_id and language.
"""
import time
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.models.request import (
    SynthexRequest, SynthexResponse, SynthexChoice,
    MessageResponse, SynthexUsage, AgentTrace
)
from app.models.database import APIKey
from app.api.middleware.auth import require_api_key
from app.core.pipeline import pipeline
from app.database import get_db
from app.services.key_service import key_service
from app.models.request import Message

router = APIRouter()


@router.post("/messages", response_model=SynthexResponse)
@router.post("/synthesize", response_model=SynthexResponse)
async def create_message(
    request: SynthexRequest,
    key: APIKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Main Synthex endpoint — runs multi-agent pipeline."""

    # Build messages list
    if request.messages:
        messages = request.messages
    elif request.prompt:
        messages = [Message(role="user", content=request.prompt)]
    else:
        raise HTTPException(400, "Provide either 'messages' or 'prompt'")

    # Plan access check
    from app.models.synthex import get_model
    model_def = get_model(request.model)
    if model_def and model_def.plan_required == "pro" and key.plan == "free":
        raise HTTPException(
            status_code=403,
            detail={"error": {
                "type": "plan_error",
                "message": f"{request.model} requires Pro plan. Upgrade at synthex.ai/upgrade",
            }},
        )

    language = getattr(request, "language", "auto") or "auto"

    # Streaming
    if request.stream:
        async def event_stream():
            request_id = f"sx-{uuid.uuid4().hex[:16]}"
            created = int(time.time())
            async for chunk in pipeline.stream(
                messages, request.model, request.max_tokens,
                request.temperature, api_key_id=str(key.id), language=language
            ):
                data = {
                    "id": request_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": request.model,
                    "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}],
                }
                yield f"data: {json.dumps(data)}\n\n"
            yield f"data: {json.dumps({'choices': [{'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # Non-streaming
    result = await pipeline.run(
        messages=messages,
        model_id=request.model,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        api_key_id=str(key.id),
        language=language,
    )

    await key_service.record_usage(
        db=db, key_obj=key, model=request.model,
        provider=result.provider_used,
        input_tokens=result.total_input_tokens,
        output_tokens=result.total_output_tokens,
        cost_usd=result.total_cost_usd,
        latency_ms=result.latency_ms,
        agents_used=result.agents_used,
        success=True,
    )
    await db.commit()

    traces = None
    if key.plan in ("pro", "enterprise") and result.agent_traces:
        traces = [AgentTrace(
            agent_id=t["agent_id"], agent_name=t["agent_name"],
            provider=t["provider"], model=t["model"],
            output=t.get("output_preview", ""),
            latency_ms=t["latency_ms"], tokens_used=t["tokens"],
        ) for t in result.agent_traces]

    return SynthexResponse(
        id=result.request_id,
        created=int(time.time()),
        model=request.model,
        choices=[SynthexChoice(
            message=MessageResponse(content=result.final_response),
            finish_reason="stop",
        )],
        usage=SynthexUsage(
            prompt_tokens=result.total_input_tokens,
            completion_tokens=result.total_output_tokens,
            total_tokens=result.total_input_tokens + result.total_output_tokens,
            cost_usd=round(result.total_cost_usd, 6),
        ),
        agents_used=result.agents_used,
        agent_traces=traces,
        synthesis_method="multi-agent" if len(result.agents_used) > 1 else "single-agent",
    )
