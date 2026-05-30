"""
Synthex NOVA Series — Model Definitions v1.0

NOVA SERIES (International · Memorable · Unique):
  synthex-nova-ultra  — 5 agents · Maximum intelligence
  synthex-nova-pro    — 3 agents · Balanced (recommended)
  synthex-nova-swift  — 1 agent  · Sub-second speed
  synthex-nova-forge  — 2 agents · Code specialist
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SynthexModel:
    id: str
    display_name: str
    series: str = "NOVA"
    tier: str = "pro"
    description: str = ""
    tagline: str = ""
    context_length: int = 128000
    max_output_tokens: int = 3000
    agents: int = 3
    avg_latency_s: float = 3.0
    cost_multiplier: float = 1.0
    plan_required: str = "free"
    supports_streaming: bool = True
    supports_files: bool = True
    primary_provider: str = "deepseek"
    synthesis_engine: str = "DeepSeek Chat"


NOVA_ULTRA = SynthexModel(
    id="synthex-nova-ultra",
    display_name="Nova Ultra",
    tier="ultra",
    description="Maximum intelligence. Full 5-agent stack: Reasoning + Reflection + Research + Debate + Synthesis.",
    tagline="Where all intelligence converges.",
    context_length=128000, max_output_tokens=4000, agents=5,
    avg_latency_s=8.0, cost_multiplier=4.0, plan_required="pro",
    primary_provider="deepseek", synthesis_engine="Claude Sonnet 4.5",
)

NOVA_PRO = SynthexModel(
    id="synthex-nova-pro",
    display_name="Nova Pro",
    tier="pro",
    description="Best quality-speed balance. 3 agents: Reasoning + Reflection + Synthesis. Recommended for production.",
    tagline="Quality-speed optimized. Recommended for most use cases.",
    context_length=128000, max_output_tokens=3000, agents=3,
    avg_latency_s=3.0, cost_multiplier=1.0, plan_required="free",
    primary_provider="deepseek", synthesis_engine="DeepSeek Chat",
)

NOVA_SWIFT = SynthexModel(
    id="synthex-nova-swift",
    display_name="Nova Swift",
    tier="swift",
    description="Ultra-low latency via Groq LPU. Single agent, sub-second response. Best for real-time apps.",
    tagline="Fastest AI responses on the market.",
    context_length=32000, max_output_tokens=2000, agents=1,
    avg_latency_s=0.8, cost_multiplier=0.1, plan_required="free",
    supports_files=False, primary_provider="groq",
    synthesis_engine="Groq LPU Llama-8B",
)

NOVA_FORGE = SynthexModel(
    id="synthex-nova-forge",
    display_name="Nova Forge",
    tier="forge",
    description="Specialist code intelligence. NVIDIA 480B Qwen3-Coder + code review. ZIP analysis supported.",
    tagline="ZIP in. Perfect code out.",
    context_length=128000, max_output_tokens=4000, agents=2,
    avg_latency_s=2.0, cost_multiplier=0.8, plan_required="free",
    primary_provider="nvidia", synthesis_engine="NVIDIA Qwen3-Coder 480B",
)


SYNTHEX_MODELS = {
    # NOVA Series (canonical names)
    "synthex-nova-ultra": NOVA_ULTRA,
    "synthex-nova-pro":   NOVA_PRO,
    "synthex-nova-swift": NOVA_SWIFT,
    "synthex-nova-forge": NOVA_FORGE,
    # Legacy aliases (backward compatible)
    "synthex-ultra-1": NOVA_ULTRA,
    "synthex-pro-1":   NOVA_PRO,
    "synthex-flash-1": NOVA_SWIFT,
    "synthex-code-1":  NOVA_FORGE,
    "synthex-nexus-1": NOVA_ULTRA,
    "synthex-arc-1":   NOVA_PRO,
    "synthex-pulse-1": NOVA_SWIFT,
    "synthex-forge-1": NOVA_FORGE,
    # OpenAI aliases (drop-in compatible)
    "gpt-4o":        NOVA_ULTRA,
    "gpt-4":         NOVA_PRO,
    "gpt-4-turbo":   NOVA_PRO,
    "gpt-3.5-turbo": NOVA_SWIFT,
    "gpt-4o-mini":   NOVA_SWIFT,
}


def get_model(model_id: str) -> Optional[SynthexModel]:
    return SYNTHEX_MODELS.get(model_id)


ALL_MODEL_IDS = [
    "synthex-nova-ultra",
    "synthex-nova-pro",
    "synthex-nova-swift",
    "synthex-nova-forge",
]
