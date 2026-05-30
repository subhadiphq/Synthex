<div align="center">

<br/>

```
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░  ███████╗██╗   ██╗███╗   ██╗████████╗██╗  ██╗███████╗██╗  ██╗  ░
░  ██╔════╝╚██╗ ██╔╝████╗  ██║╚══██╔══╝██║  ██║██╔════╝╚██╗██╔╝  ░
░  ███████╗ ╚████╔╝ ██╔██╗ ██║   ██║   ███████║█████╗   ╚███╔╝   ░
░  ╚════██║  ╚██╔╝  ██║╚██╗██║   ██║   ██╔══██║██╔══╝   ██╔██╗   ░
░  ███████║   ██║   ██║ ╚████║   ██║   ██║  ██║███████╗██╔╝ ██╗  ░
░  ╚══════╝   ╚═╝   ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  ░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

### ✦ Many Minds. One Answer. ✦

**Production-grade multi-agent AI orchestration platform.**
16 specialist agents · 7 AI providers · 3-tier automatic failover · OpenAI-compatible

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-6C63FF?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-00D4AA?style=for-the-badge)]()
[![OpenAI](https://img.shields.io/badge/OpenAI-Compatible-412991?style=for-the-badge&logo=openai&logoColor=white)]()
[![Agents](https://img.shields.io/badge/Agents-16_Specialist-F5A623?style=for-the-badge)]()

<br/>

```
User Request  →  Σ Orchestrator  →  ┌─ α Reasoning ─┐
                                    ├─ δ Research   ─┤  →  λ Synthesis  →  μ Safety  →  Answer
                                    └─ β Reflection ─┘
```

[**Chat UI**](frontend/chat/) · [**Dashboard**](frontend/dashboard/) · [**API Docs**](frontend/docs/) · [**Landing**](frontend/landing/)

</div>

---

## ◈ NOVA Series — Model Lineup

| Model | Name | Agents | Latency | Plan | Best For |
|:------|:-----|:------:|:-------:|:----:|:---------|
| `synthex-nova-ultra` | **Nova Ultra** | 5 | ~8s | Pro | Complex research · Deep analysis |
| `synthex-nova-pro` | **Nova Pro** | 3 | ~3s | Free | Daily production · **Recommended ✓** |
| `synthex-nova-swift` | **Nova Swift** | 1 | <1s | Free | Real-time apps · Fast Q&A |
| `synthex-nova-forge` | **Nova Forge** | 2 | ~2s | Free | Code generation · ZIP analysis |

```
Intelligence ──────────────────────────────────────────▶
Nova Swift   ████░░░░░░  fastest
Nova Forge   ██████░░░░  code specialist
Nova Pro     ████████░░  balanced ✓ recommended
Nova Ultra   ██████████  maximum
```

---

## ◈ Architecture

```
╔══════════════════════════════════════════════════════════════════════╗
║                    SYNTHEX PLATFORM v1.0.0                          ║
╠══════════════════════════════════════════════════════════════════════╣
║  CLIENT  →  FastAPI  →  Auth  →  Rate Limit  →  Intelligence Engine ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  TIER 0:  Σ  Master Orchestrator  (DeepSeek Chat)                   ║
║                                                                      ║
║  TIER 1:  α Reasoning  (DeepSeek R1)                                ║
║           β Reflection (Groq 70B)                                   ║
║           γ Planning   (DeepSeek Chat)                              ║
║                                                                      ║
║  TIER 2:  δ Research    (Gemini 1.5 Flash · 1M context)             ║
║           ε Coding      (NVIDIA Qwen3-Coder 480B)                   ║
║           ζ Finance     (DeepSeek R1)                               ║
║           η Data        (OpenRouter Free)                            ║
║           θ Content     (Claude Haiku via OpenRouter)               ║
║           ι Health      (Gemini Flash)                               ║
║                                                                      ║
║  TIER 3:  κ Memory      (Groq 8B)                                   ║
║           λ Synthesis   (Claude Sonnet · ultra / DeepSeek · pro)   ║
║           μ Safety      (Groq 8B + policy rules)                    ║
║           ν Compression (Groq 8B · 40-60% token saving)            ║
║           ξ Tools       (OpenRouter · search/calc)                  ║
║           ο Workflow    (DeepSeek Chat)                              ║
║                                                                      ║
║  TIER 4:  ρ Debate      (Groq 70B · Nova Ultra only)               ║
╠══════════════════════════════════════════════════════════════════════╣
║  PROVIDERS:  Groq · OpenRouter · NVIDIA · DeepSeek · Gemini         ║
║              Anthropic* · OpenAI*  (* via OpenRouter, no key needed)║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## ◈ Quick Start

```bash
git clone https://github.com/your-username/synthex-platform.git
cd synthex-platform/backend
cp .env.example .env
# Edit .env — add your API keys
pip install -r requirements.txt
python main.py
```

```
🚀 Synthex API v1.0 started — port 8000
🧠 16 agents initialized
📡 7 providers online
🌐 Docs: http://localhost:8000/docs
```

### Create API Key

```bash
curl -X POST http://localhost:8000/v1/keys \
  -H "Content-Type: application/json" \
  -d '{"name":"My App","email":"you@email.com","plan":"free"}'
```

```json
{"key": "sx-xxxxxxxxxxxxxxxxxxxx", "plan": "free", "monthly_limit": 200}
```

---

## ◈ OpenAI Drop-in Replacement

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-api.railway.app/v1",
    api_key="sx-your-key-here",
)

# Nova Pro — 3 agents, recommended
response = client.chat.completions.create(
    model="synthex-nova-pro",
    messages=[{"role": "user", "content": "Explain quantum computing simply"}],
)

# Nova Swift — sub-second, streaming
stream = client.chat.completions.create(
    model="synthex-nova-swift",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True,
)

# Nova Forge — code specialist (480B)
code = client.chat.completions.create(
    model="synthex-nova-forge",
    messages=[{"role": "user", "content": "Write a production FastAPI server with JWT auth"}],
)

# Bengali — auto-detected
bn_response = client.chat.completions.create(
    model="synthex-nova-pro",
    messages=[{"role": "user", "content": "বাংলাদেশের অর্থনীতি বিশ্লেষণ করো"}],
)
```

---

## ◈ API Endpoints

| Method | Endpoint | Auth | Description |
|:------:|:---------|:----:|:------------|
| `POST` | `/v1/messages` | ✓ | Main Synthex — multi-agent pipeline |
| `POST` | `/v1/chat/completions` | ✓ | OpenAI-compatible |
| `GET`  | `/v1/models` | ✗ | NOVA Series model catalog |
| `POST` | `/v1/keys` | ✗ | Create API key |
| `GET`  | `/v1/keys/me` | ✓ | Key info + usage |
| `GET`  | `/v1/usage` | ✓ | Usage stats |
| `GET`  | `/v1/usage/logs` | ✓ | Request history |
| `POST` | `/v1/files/upload` | ✓ | File analysis (ZIP/CSV/code) |
| `POST` | `/v1/finance` | ✓ | Finance intelligence (Pro) |
| `POST` | `/v1/search` | ✓ | Web search synthesis |
| `GET`  | `/health` | ✗ | Health check |
| `GET`  | `/docs` | ✗ | Swagger UI |

---

## ◈ Provider Failover

```
Every agent has 3-4 tier automatic failover:

α Reasoning:  DeepSeek R1  →  OpenRouter DeepSeek  →  Groq 70B  →  OpenRouter Free
ε Coding:     NVIDIA 480B  →  OpenRouter Qwen       →  Groq 70B  →  OpenRouter Free
λ Synthesis:  Claude Sonnet (ultra) / DeepSeek (pro)  →  Groq  →  OpenRouter Free
μ Safety:     Groq 8B  →  OpenRouter Free   [always available]

System NEVER crashes — free tier is always the last resort.
```

---

## ◈ Deploy

### Railway (Recommended)

```bash
# 1. Push backend/ to a new GitHub repo (files at root, not in subfolder)
# 2. railway.app → New Project → Deploy from GitHub
# 3. Settings → Root Directory: leave empty (main.py is at root)
# 4. Variables tab → add all API keys
# 5. Deploy ✅
```

### Environment Variables

```env
# REQUIRED (both free)
GROQ_API_KEY=gsk_xxxx
OPENROUTER_API_KEY=sk-or-xxxx

# RECOMMENDED (improves quality significantly)
DEEPSEEK_API_KEY=sk-xxxx
GEMINI_API_KEY=AIzaxxxx
NVIDIA_API_KEY=nvapi-xxxx

# SERVER
DATABASE_URL=sqlite+aiosqlite:///./synthex.db
SECRET_KEY=random-32-char-string
PORT=8000

# NOTE: Anthropic & OpenAI accessed via OpenRouter — no separate key needed
```

### Docker

```bash
docker build -t synthex .
docker run -p 8000:8000 --env-file .env synthex
```

---

## ◈ Project Structure

```
synthex-platform/
├── backend/                        FastAPI backend
│   ├── main.py                     Application entry point
│   ├── requirements.txt
│   ├── nixpacks.toml               Railway build config
│   ├── railway.json                Railway deploy config
│   ├── Dockerfile
│   ├── .env.example
│   └── app/
│       ├── agents/
│       │   ├── __init__.py         16-agent registry (Tier 0–4)
│       │   ├── base.py             BaseAgent + auto-fallback
│       │   └── specialized.py      Finance + WebSearch sub-agents
│       ├── providers/
│       │   ├── __init__.py         SmartRouter + 3-tier failover chains
│       │   ├── groq.py
│       │   ├── openrouter.py
│       │   ├── deepseek.py
│       │   ├── gemini.py
│       │   ├── nvidia.py
│       │   ├── anthropic.py
│       │   └── openai.py
│       ├── core/
│       │   ├── pipeline.py         Multi-agent orchestration engine
│       │   ├── orchestrator.py     Intent classification
│       │   ├── memory.py           Conversation memory
│       │   └── web_search.py       DuckDuckGo integration (free)
│       ├── api/routes/
│       │   ├── messages.py         POST /v1/messages
│       │   ├── chat.py             POST /v1/chat/completions
│       │   ├── models.py           GET /v1/models
│       │   ├── keys.py             Key management
│       │   ├── usage.py            Usage + logs
│       │   ├── files.py            File upload & analysis
│       │   ├── finance.py          Finance intelligence
│       │   ├── search.py           Web search
│       │   └── health.py           Health check
│       ├── models/
│       │   ├── synthex.py          NOVA Series model definitions
│       │   ├── database.py         SQLAlchemy ORM
│       │   └── request.py          Pydantic schemas
│       └── services/
│           ├── key_service.py      API key lifecycle
│           ├── cache_service.py    Response caching
│           └── rate_limiter.py     Rate limiting
│
├── frontend/                       Web interface (zero dependencies)
│   ├── index.html                  Navigation hub
│   ├── chat/                       Chat interface (dark · streaming · Bengali)
│   ├── dashboard/                  API management · usage stats · tester
│   ├── docs/                       Interactive API documentation
│   └── landing/                    Product landing page
│
└── README.md
```

---

## ◈ Roadmap

```
PHASE 1 — Foundation (Now)           ✅
  ✅ FastAPI + 16-agent pipeline
  ✅ NOVA Series: ultra · pro · swift · forge
  ✅ 7 providers + 3-tier failover
  ✅ OpenAI-compatible API
  ✅ Bengali auto-detection
  ✅ Streaming SSE
  ✅ File intelligence (ZIP/CSV/code)
  ✅ Finance AI with compliance layer
  ✅ Web frontend: Chat · Dashboard · Docs · Landing
  ◻  Production deployment

PHASE 2 — Growth (Days 90–180)
  ◻  Stripe billing (Free / Pro $29 / Enterprise)
  ◻  Pinecone vector memory
  ◻  Usage analytics dashboard
  ◻  Rate limiting per IP

PHASE 3 — Scale (Days 180–365)
  ◻  Enterprise white-label API
  ◻  Kubernetes auto-scaling
  ◻  Agent marketplace

PHASE 4 — AI OS (Year 2+)
  ◻  SynthexLM foundation model
  ◻  Multi-modal agents
  ◻  100K users · Series A
```

---

## ◈ Tech Stack

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| API | FastAPI 0.115 | Async HTTP, SSE streaming |
| DB | SQLAlchemy + aiosqlite | ORM, async queries |
| Reasoning | DeepSeek R1 | Chain-of-thought |
| Speed | Groq LPU Llama-8B | <1s inference |
| Code | NVIDIA Qwen3-480B | Code specialist |
| Research | Gemini 1.5 Flash | 1M context window |
| Synthesis | Claude Sonnet 4.5 | Premium synthesis |
| Hub | OpenRouter | 100+ model access |
| Frontend | HTML5 + CSS3 + Vanilla JS | Zero-dependency |
| Deploy | Railway + Vercel | Cloud hosting |

---

<div align="center">

```
Built with 16 specialist agents.
Powered by 7 AI provider networks.
NOVA Series — Many Minds. One Answer.
```

**Synthex AI Platform v1.0.0**

</div>
