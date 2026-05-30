"""
Synthex Provider Registry — 7 AI Providers with 3-tier per-agent failover.
Every agent has Primary → Secondary → Emergency (always free) fallback.
"""
import asyncio
from typing import List, Optional, Tuple
from app.models.request import Message


class ProviderError(Exception):
    pass


class ProviderRegistry:
    def __init__(self):
        self._providers = {}
        self._load_all()

    def _load_all(self):
        loaders = [
            ("groq",       "app.providers.groq",       "GroqProvider"),
            ("openrouter", "app.providers.openrouter",  "OpenRouterProvider"),
            ("deepseek",   "app.providers.deepseek",    "DeepSeekProvider"),
            ("gemini",     "app.providers.gemini",      "GeminiProvider"),
            ("nvidia",     "app.providers.nvidia",      "NVIDIAProvider"),
            ("anthropic",  "app.providers.anthropic",   "AnthropicProvider"),
            ("openai",     "app.providers.openai",      "OpenAIProvider"),
        ]
        for name, module, cls in loaders:
            try:
                import importlib
                mod = importlib.import_module(module)
                self._providers[name] = getattr(mod, cls)()
            except Exception as e:
                print(f"⚠️  {name} provider not loaded: {e}")

    def get(self, name: str):
        return self._providers.get(name)

    def available(self) -> list:
        return list(self._providers.keys())


registry = ProviderRegistry()


# ── Per-Agent Fallback Chains ─────────────────────────────────────────────────
AGENT_FALLBACKS = {
    "reasoning":      [("deepseek","deepseek-chat"),("openrouter","deepseek/deepseek-chat-v3-0324:free"),("groq","llama-3.3-70b-versatile"),("openrouter","meta-llama/llama-3.3-70b-instruct:free")],
    "reflection":     [("groq","llama-3.3-70b-versatile"),("gemini","gemini-1.5-flash"),("openrouter","meta-llama/llama-3.3-70b-instruct:free")],
    "planning":       [("deepseek","deepseek-chat"),("groq","llama-3.3-70b-versatile"),("openrouter","meta-llama/llama-3.3-70b-instruct:free")],
    "research":       [("gemini","gemini-1.5-flash"),("openrouter","google/gemini-2.0-flash-lite-001:free"),("groq","llama-3.3-70b-versatile"),("openrouter","meta-llama/llama-3.3-70b-instruct:free")],
    "coding":         [("nvidia","qwen/qwen3-coder-480b-a35b-instruct"),("openrouter","qwen/qwen3-235b-a22b:free"),("groq","llama-3.3-70b-versatile"),("openrouter","meta-llama/llama-3.3-70b-instruct:free")],
    "finance":        [("deepseek","deepseek-chat"),("groq","llama-3.3-70b-versatile"),("openrouter","meta-llama/llama-3.3-70b-instruct:free")],
    "data_analysis":  [("openrouter","meta-llama/llama-3.3-70b-instruct:free"),("groq","llama-3.3-70b-versatile"),("gemini","gemini-1.5-flash")],
    "content":        [("openrouter","anthropic/claude-haiku-4-5"),("deepseek","deepseek-chat"),("groq","llama-3.3-70b-versatile"),("openrouter","meta-llama/llama-3.3-70b-instruct:free")],
    "health":         [("gemini","gemini-1.5-flash"),("groq","llama-3.3-70b-versatile"),("openrouter","meta-llama/llama-3.3-70b-instruct:free")],
    "memory":         [("groq","llama-3.1-8b-instant"),("openrouter","meta-llama/llama-3.1-8b-instruct:free")],
    "synthesis":      [("deepseek","deepseek-chat"),("groq","llama-3.3-70b-versatile"),("openrouter","meta-llama/llama-3.3-70b-instruct:free")],
    "synthesis_premium": [("openrouter","anthropic/claude-sonnet-4-5"),("deepseek","deepseek-chat"),("groq","llama-3.3-70b-versatile"),("openrouter","meta-llama/llama-3.3-70b-instruct:free")],
    "safety":         [("groq","llama-3.1-8b-instant"),("openrouter","meta-llama/llama-3.1-8b-instruct:free")],
    "compression":    [("groq","llama-3.1-8b-instant"),("openrouter","meta-llama/llama-3.1-8b-instruct:free")],
    "tools":          [("openrouter","meta-llama/llama-3.3-70b-instruct:free"),("groq","llama-3.3-70b-versatile")],
    "workflow":       [("deepseek","deepseek-chat"),("groq","llama-3.3-70b-versatile"),("openrouter","meta-llama/llama-3.3-70b-instruct:free")],
    "debate":         [("groq","llama-3.3-70b-versatile"),("openrouter","meta-llama/llama-3.3-70b-instruct:free"),("deepseek","deepseek-chat")],
    "flash_direct":   [("groq","llama-3.1-8b-instant"),("openrouter","meta-llama/llama-3.1-8b-instruct:free"),("groq","llama-3.3-70b-versatile")],
    "orchestrator":   [("groq","llama-3.1-8b-instant"),("openrouter","meta-llama/llama-3.1-8b-instruct:free"),("deepseek","deepseek-chat")],
    "default":        [("groq","llama-3.3-70b-versatile"),("openrouter","meta-llama/llama-3.3-70b-instruct:free"),("deepseek","deepseek-chat")],
}


class SmartRouter:
    """Routes requests through 3-tier fallback chains. Never crashes."""

    async def chat(self, provider_name: str, model: str, messages: List[Message],
                   system_prompt: Optional[str] = None, max_tokens: int = 2000,
                   temperature: float = 0.7, timeout: int = 30,
                   agent_role: str = "default") -> Tuple[str, int, int, str]:
        # Build deduped chain: primary first, then fallbacks
        chain = [(provider_name, model)]
        for p, m in AGENT_FALLBACKS.get(agent_role, AGENT_FALLBACKS["default"]):
            if (p, m) not in chain:
                chain.append((p, m))

        last_err = "all providers failed"
        for pid, mid in chain:
            provider = registry.get(pid)
            if not provider:
                continue
            try:
                result = await asyncio.wait_for(
                    provider.chat(messages, mid, system_prompt, max_tokens, temperature),
                    timeout=timeout,
                )
                if result and result[0]:
                    return result[0], result[1], result[2], pid
            except asyncio.TimeoutError:
                last_err = f"{pid} timeout {timeout}s"
            except Exception as e:
                last_err = f"{pid}: {str(e)[:80]}"
                continue

        # Emergency: graceful degradation — never crash
        return (
            f"I'm experiencing temporary high load. Please retry in a moment. (Debug: {last_err[:60]})",
            0, 0, "error"
        )


smart_router = SmartRouter()
