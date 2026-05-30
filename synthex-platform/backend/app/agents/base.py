"""Synthex BaseAgent — all 16 agents extend this. Automatic 3-tier fallback via agent_role."""
import time, asyncio
from typing import List, Optional
from app.models.request import Message


class AgentResult:
    def __init__(self):
        self.agent_id = ""; self.agent_name = ""; self.output = ""
        self.success = False; self.provider_used = ""; self.model_used = ""
        self.input_tokens = 0; self.output_tokens = 0; self.latency_ms = 0
        self.error: Optional[str] = None
    def __repr__(self):
        return f"<AgentResult agent={self.agent_id} ok={self.success} provider={self.provider_used}>"


class BaseAgent:
    agent_id: str = "base"; agent_name: str = "Base"
    default_provider: str = "groq"; default_model: str = "llama-3.1-8b-instant"
    timeout: int = 20; SYSTEM_PROMPT: str = "You are a helpful AI assistant."

    async def run(self, messages: List[Message], task: str,
                  context: Optional[str] = None, max_tokens: int = 1000,
                  temperature: float = 0.7) -> AgentResult:
        from app.providers import smart_router
        start = time.time()
        r = AgentResult()
        r.agent_id = self.agent_id; r.agent_name = self.agent_name
        system = self.SYSTEM_PROMPT
        if context: system = f"{system}\n\nContext:\n{context}"
        if task:    system = f"{system}\n\nYour task: {task}"
        try:
            content, in_tok, out_tok, provider = await smart_router.chat(
                provider_name=self.default_provider, model=self.default_model,
                messages=messages, system_prompt=system, max_tokens=max_tokens,
                temperature=temperature, timeout=self.timeout, agent_role=self.agent_id,
            )
            r.output=content; r.success=True; r.input_tokens=in_tok
            r.output_tokens=out_tok; r.provider_used=provider; r.model_used=self.default_model
        except asyncio.TimeoutError:
            r.success=False; r.error=f"{self.agent_id} timeout after {self.timeout}s"
        except Exception as e:
            r.success=False; r.error=str(e)
        r.latency_ms = int((time.time()-start)*1000)
        return r
