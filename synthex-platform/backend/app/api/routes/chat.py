"""
POST /v1/chat/completions — OpenAI-Compatible Endpoint
FIX: api_key_id and language now passed to pipeline.
"""
import time, uuid, json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.request import ChatCompletionRequest, Message
from app.models.database import APIKey
from app.api.middleware.auth import require_api_key
from app.core.pipeline import pipeline, detect_language, normalise_model
from app.database import get_db
from app.services.key_service import key_service

router = APIRouter()


@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    key: APIKey = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
):
    """OpenAI-compatible endpoint. Change only base_url in your client."""
    if not request.messages:
        raise HTTPException(400, "'messages' is required")

    messages = [
        Message(role=m.role, content=m.content)
        for m in request.messages
        if m.role in ("user", "assistant")
    ]
    if not messages:
        raise HTTPException(400, "At least one user message required")

    last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
    lang = request.language or detect_language(last_user)
    model_id = normalise_model(request.model)

    if request.stream:
        async def event_stream():
            req_id = f"chatcmpl-{uuid.uuid4().hex[:16]}"
            created = int(time.time())
            async for chunk in pipeline.stream(
                messages, model_id, request.max_tokens or 2000,
                request.temperature or 0.7, api_key_id=str(key.id), language=lang
            ):
                data = {
                    "id": req_id, "object": "chat.completion.chunk",
                    "created": created, "model": request.model,
                    "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}],
                }
                yield f"data: {json.dumps(data)}\n\n"
            yield f"data: {json.dumps({'choices': [{'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(event_stream(), media_type="text/event-stream")

    result = await pipeline.run(
        messages=messages, model_id=model_id,
        max_tokens=request.max_tokens or 2000,
        temperature=request.temperature or 0.7,
        api_key_id=str(key.id), language=lang,
    )

    await key_service.record_usage(
        db=db, key_obj=key, model=model_id,
        provider=result.provider_used,
        input_tokens=result.total_input_tokens,
        output_tokens=result.total_output_tokens,
        cost_usd=result.total_cost_usd,
        latency_ms=result.latency_ms,
        agents_used=result.agents_used,
        success=True,
    )
    await db.commit()

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": result.final_response}, "finish_reason": "stop"}],
        "usage": {
            "prompt_tokens": result.total_input_tokens,
            "completion_tokens": result.total_output_tokens,
            "total_tokens": result.total_input_tokens + result.total_output_tokens,
        },
        "x_synthex": {
            "agents_used": result.agents_used,
            "latency_ms": result.latency_ms,
            "cost_usd": round(result.total_cost_usd, 6),
            "model_canonical": model_id,
        },
    }
