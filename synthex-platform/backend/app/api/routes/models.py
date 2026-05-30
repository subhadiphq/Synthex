"""GET /v1/models — Synthex NOVA Series model catalog."""
from fastapi import APIRouter

router = APIRouter()

MODELS = [
    {
        "id": "synthex-nova-ultra",
        "object": "model",
        "display_name": "Nova Ultra",
        "series": "NOVA",
        "tier": "ultra",
        "tagline": "Where all intelligence converges.",
        "description": "Maximum intelligence. Full 5-agent stack: Deep Reasoning + Reflection + Research + Debate + Synthesis via Claude Sonnet 4.5.",
        "agents": 5,
        "avg_latency": "~8s",
        "context_length": 128000,
        "max_output_tokens": 4000,
        "plan_required": "pro",
        "supports_streaming": True,
        "supports_files": True,
        "synthesis_engine": "Claude Sonnet 4.5",
        "agent_stack": ["reasoning", "research", "planning", "reflection", "debate", "synthesis"],
    },
    {
        "id": "synthex-nova-pro",
        "object": "model",
        "display_name": "Nova Pro",
        "series": "NOVA",
        "tier": "pro",
        "tagline": "Quality-speed optimized. Recommended for most use cases.",
        "description": "Best quality-speed balance. 3 agents: Deep Reasoning + Reflection + Synthesis. Best for daily production workloads.",
        "agents": 3,
        "avg_latency": "~3s",
        "context_length": 128000,
        "max_output_tokens": 3000,
        "plan_required": "free",
        "supports_streaming": True,
        "supports_files": True,
        "synthesis_engine": "DeepSeek Chat",
        "agent_stack": ["reasoning", "reflection", "synthesis"],
    },
    {
        "id": "synthex-nova-swift",
        "object": "model",
        "display_name": "Nova Swift",
        "series": "NOVA",
        "tier": "swift",
        "tagline": "Fastest AI responses on the market.",
        "description": "Ultra-low latency via Groq LPU. Single agent, sub-second inference. Ideal for real-time apps and chatbots.",
        "agents": 1,
        "avg_latency": "<1s",
        "context_length": 32000,
        "max_output_tokens": 2000,
        "plan_required": "free",
        "supports_streaming": True,
        "supports_files": False,
        "synthesis_engine": "Groq LPU Llama-8B",
        "agent_stack": ["flash_direct"],
    },
    {
        "id": "synthex-nova-forge",
        "object": "model",
        "display_name": "Nova Forge",
        "series": "NOVA",
        "tier": "forge",
        "tagline": "ZIP in. Perfect code out.",
        "description": "Specialist code intelligence. NVIDIA 480B Qwen3-Coder for generation + Reflection Agent for review. ZIP file analysis.",
        "agents": 2,
        "avg_latency": "~2s",
        "context_length": 128000,
        "max_output_tokens": 4000,
        "plan_required": "free",
        "supports_streaming": False,
        "supports_files": True,
        "synthesis_engine": "NVIDIA Qwen3-Coder 480B",
        "agent_stack": ["coding", "reflection"],
    },
]


@router.get("/models")
async def list_models():
    return {
        "object": "list",
        "series": "NOVA",
        "data": MODELS,
        "openai_compatible": True,
        "legacy_aliases": {
            "gpt-4o":        "synthex-nova-ultra",
            "gpt-4":         "synthex-nova-pro",
            "gpt-3.5-turbo": "synthex-nova-swift",
            "gpt-4o-mini":   "synthex-nova-swift",
        },
        "pricing_usd_per_1k_tokens": {
            "synthex-nova-swift": {"input": 0.0005, "output": 0.002},
            "synthex-nova-pro":   {"input": 0.003,  "output": 0.012},
            "synthex-nova-forge": {"input": 0.002,  "output": 0.008},
            "synthex-nova-ultra": {"input": 0.010,  "output": 0.040},
        },
    }


@router.get("/models/{model_id}")
async def get_model_info(model_id: str):
    for m in MODELS:
        if m["id"] == model_id:
            return m
    # Check legacy aliases
    aliases = {
        "synthex-ultra-1": "synthex-nova-ultra",
        "synthex-pro-1": "synthex-nova-pro",
        "synthex-flash-1": "synthex-nova-swift",
        "synthex-code-1": "synthex-nova-forge",
    }
    if model_id in aliases:
        canonical = aliases[model_id]
        for m in MODELS:
            if m["id"] == canonical:
                return {**m, "requested_as": model_id, "canonical_id": canonical}
    return {"error": f"Model '{model_id}' not found", "available": [m["id"] for m in MODELS]}
