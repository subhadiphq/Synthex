"""
Synthex AI Platform — Backend API v1.0
Production-Grade FastAPI · Multi-Agent Orchestration
"""
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.api.routes import messages, chat, models, keys, usage, health, files, finance, search
from app.api.middleware.logger import RequestLoggerMiddleware
from app.database import init_db
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print(f"🚀 Synthex API v1.0 started — port {settings.PORT}")
    print(f"📡 Providers: OpenRouter, Groq, NVIDIA NIM, DeepSeek, Gemini, Anthropic, OpenAI")
    print(f"🤖 Models: synthex-nova-ultra · synthex-nova-pro · synthex-nova-swift · synthex-nova-forge")
    print(f"🧠 Agents: 16 specialist agents active")
    print(f"🌐 Docs: http://localhost:{settings.PORT}/docs")
    yield
    print("Synthex API shutting down...")


app = FastAPI(
    title="Synthex AI Platform",
    description="""
## Synthex — Multi-Agent AI Orchestration API

**Many minds. One answer.**

Synthex orchestrates multiple AI agents that collaborate, verify, and synthesize
to deliver answers no single model can match.

### Models (Celestial Series)
- `synthex-nova-ultra` — Ultra · 5 agents · Maximum intelligence
- `synthex-nova-pro` — Pro · 3 agents · Best balance (recommended)
- `synthex-nova-swift` — Flash · 1 agent · Fastest response
- `synthex-nova-forge` — Code · 2 agents · Specialist coding

### Authentication
All endpoints require `Authorization: Bearer sx-your-key` header.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestLoggerMiddleware)

# Routes — ordered by priority
app.include_router(health.router,   tags=["Health"])
app.include_router(messages.router, prefix="/v1", tags=["Messages"])
app.include_router(chat.router,     prefix="/v1", tags=["Chat (OpenAI-compatible)"])
app.include_router(models.router,   prefix="/v1", tags=["Models"])
app.include_router(keys.router,     prefix="/v1", tags=["API Keys"])
app.include_router(usage.router,    prefix="/v1", tags=["Usage"])
app.include_router(files.router,    prefix="/v1", tags=["Files"])
app.include_router(finance.router,  prefix="/v1", tags=["Finance Intelligence"])
app.include_router(search.router,   prefix="/v1", tags=["Web Search"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "Synthex AI Platform",
        "version": "1.0.0",
        "tagline": "Many minds. One answer.",
        "models": ["synthex-nova-ultra", "synthex-nova-pro", "synthex-nova-swift", "synthex-nova-forge"],
        "endpoints": {
            "messages": "/v1/messages",
            "chat": "/v1/chat/completions",
            "models": "/v1/models",
            "keys": "/v1/keys",
            "usage": "/v1/usage",
            "files": "/v1/files/upload",
            "finance": "/v1/finance",
            "search": "/v1/search",
            "health": "/health",
            "docs": "/docs",
        },
        "status": "operational",
    }


@app.exception_handler(404)
async def not_found(request: Request, exc):
    return JSONResponse(status_code=404, content={
        "error": {"type": "not_found", "message": f"Endpoint {request.url.path} not found", "docs": "/docs"}
    })


@app.exception_handler(500)
async def server_error(request: Request, exc):
    return JSONResponse(status_code=500, content={
        "error": {"type": "server_error", "message": "Internal server error. Please try again."}
    })


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG, log_level="info")
