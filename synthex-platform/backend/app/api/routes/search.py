"""
POST /v1/search — Web Search endpoint
Uses DuckDuckGo (free, no API key) + AI synthesis.

FIX: format_results (not format_search_results) is correct import.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.models.database import APIKey
from app.api.middleware.auth import require_api_key
from app.core.web_search import search_duckduckgo, format_results
from app.agents.specialized import web_search_agent
from app.models.request import Message
import time, uuid

router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    synthesize: bool = True
    max_results: int = Field(default=5, ge=1, le=10)


@router.post("/search")
async def web_search(
    request: SearchRequest,
    key: APIKey = Depends(require_api_key),
):
    """Search the web and synthesize results with AI."""
    start = time.time()

    results = await search_duckduckgo(request.query, request.max_results)
    raw = format_results(results)

    synthesized = raw
    if request.synthesize and results:
        try:
            synthesized = await web_search_agent.search_and_respond(request.query, raw)
        except Exception:
            synthesized = raw

    return {
        "id": f"srch-{uuid.uuid4().hex[:10]}",
        "query": request.query,
        "results_count": len(results),
        "synthesized_response": synthesized,
        "raw_results": results[:5],  # limit raw output
        "latency_ms": int((time.time() - start) * 1000),
    }
