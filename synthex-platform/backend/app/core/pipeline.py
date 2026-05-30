"""
Synthex Intelligence Pipeline — v1.0
Orchestrates all 16 agents for ultra-1, pro-1, flash-1, code-1.
"""
import asyncio, time, uuid, json
from typing import List, Optional, AsyncGenerator
from app.models.request import Message
from app.models.synthex import get_model
from app.agents import (reasoning_agent, reflection_agent, planning_agent,
    research_agent, coding_agent, synthesis_agent, safety_agent,
    debate_agent, memory_agent, AGENT_REGISTRY)
from app.agents.base import AgentResult
from app.providers import smart_router
from app.config import settings


def detect_language(text: str) -> str:
    bn = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
    return "bn" if len(text) > 0 and bn > len(text) * 0.1 else "en"


class PipelineResult:
    def __init__(self):
        self.request_id = f"sx-{uuid.uuid4().hex[:16]}"
        self.model_id = ""; self.final_response = ""
        self.agents_used: List[str] = []; self.agent_traces: List[dict] = []
        self.total_input_tokens = 0; self.total_output_tokens = 0
        self.total_cost_usd = 0.0; self.latency_ms = 0
        self.provider_used = ""; self.language = "en"


COSTS = {
    "deepseek":   {"input":0.00027,  "output":0.0011},
    "groq":       {"input":0.00005,  "output":0.00008},
    "openrouter": {"input":0.0,      "output":0.0},
    "nvidia":     {"input":0.0,      "output":0.0},
    "gemini":     {"input":0.00015,  "output":0.0006},
    "anthropic":  {"input":0.00025,  "output":0.00125},
    "openai":     {"input":0.00015,  "output":0.0006},
    "error":      {"input":0.0,      "output":0.0},
}


def calc_cost(provider: str, in_tok: int, out_tok: int) -> float:
    c = COSTS.get(provider, COSTS["error"])
    return (in_tok/1000*c["input"]) + (out_tok/1000*c["output"])


def trace(a: AgentResult) -> dict:
    return {"agent_id":a.agent_id,"agent_name":a.agent_name,"provider":a.provider_used,
            "model":a.model_used,"output_preview":a.output[:200]+"..." if len(a.output)>200 else a.output,
            "latency_ms":a.latency_ms,"tokens":a.input_tokens+a.output_tokens,"success":a.success}


def normalise_model(model_id: str) -> str:
    """Map all legacy/OpenAI model names to NOVA Series canonical names."""
    mapping = {
        # NOVA canonical (pass-through)
        "synthex-nova-ultra":  "synthex-nova-ultra",
        "synthex-nova-pro":    "synthex-nova-pro",
        "synthex-nova-swift":  "synthex-nova-swift",
        "synthex-nova-forge":  "synthex-nova-forge",
        # Legacy v1 names
        "synthex-ultra-1":     "synthex-nova-ultra",
        "synthex-pro-1":       "synthex-nova-pro",
        "synthex-flash-1":     "synthex-nova-swift",
        "synthex-code-1":      "synthex-nova-forge",
        # Even older names
        "synthex-nexus-1":     "synthex-nova-ultra",
        "synthex-arc-1":       "synthex-nova-pro",
        "synthex-pulse-1":     "synthex-nova-swift",
        "synthex-forge-1":     "synthex-nova-forge",
        # OpenAI aliases
        "gpt-4o":              "synthex-nova-ultra",
        "gpt-4":               "synthex-nova-pro",
        "gpt-4-turbo":         "synthex-nova-pro",
        "gpt-3.5-turbo":       "synthex-nova-swift",
        "gpt-4o-mini":         "synthex-nova-swift",
    }
    return mapping.get(model_id, "synthex-nova-pro")  # safe default


class SynthexPipeline:

    async def run(self, messages: List[Message], model_id: str = "synthex-nova-pro",
                  max_tokens: int = 2000, temperature: float = 0.7,
                  api_key_id: Optional[str] = None, language: Optional[str] = None) -> PipelineResult:
        start = time.time()
        r = PipelineResult(); r.model_id = model_id
        last_user = next((m.content for m in reversed(messages) if m.role=="user"), "")
        lang = language or detect_language(last_user)
        r.language = lang
        model_id = normalise_model(model_id)

        if model_id == "synthex-nova-swift":
            result = await self._flash(messages, r, max_tokens, temperature, start, lang)
        elif model_id == "synthex-nova-forge":
            result = await self._code(messages, r, max_tokens, start, lang)
        elif model_id == "synthex-nova-ultra":
            result = await self._ultra(messages, r, max_tokens, temperature, start, lang)
        else:
            result = await self._pro(messages, r, max_tokens, temperature, start, lang)

        if api_key_id and result.final_response:
            asyncio.create_task(self._memory(api_key_id, messages, result.final_response))
        return result

    async def _flash(self, messages, r, max_tokens, temperature, start, lang):
        li = "Respond entirely in Bengali (বাংলা)." if lang=="bn" else "Respond in English."
        content, in_tok, out_tok, provider = await smart_router.chat(
            "groq","llama-3.1-8b-instant",messages,
            f"You are Synthex Flash — ultra-fast, accurate AI assistant.\n{li}",
            max_tokens,temperature,timeout=settings.PULSE_TIMEOUT,agent_role="flash_direct")
        r.final_response=content; r.agents_used=["flash_direct"]
        r.total_input_tokens=in_tok; r.total_output_tokens=out_tok
        r.total_cost_usd=calc_cost(provider,in_tok,out_tok); r.provider_used=provider
        r.latency_ms=int((time.time()-start)*1000)
        return r

    async def _code(self, messages, r, max_tokens, start, lang):
        li = "Respond in Bengali (বাংলা)." if lang=="bn" else "Respond in English."
        code_r = await coding_agent.run(messages,"Write production-quality code",max_tokens=max_tokens)
        agents=[code_r]
        if code_r.success:
            rev_msgs = messages+[Message(role="assistant",content=code_r.output)]
            rev_r = await reflection_agent.run(rev_msgs,"Review code: bugs, security, improvements",max_tokens=700)
            agents.append(rev_r)
            ctx=f"Code Output:\n{code_r.output}\n\nCode Review:\n{rev_r.output if rev_r.success else 'N/A'}"
            content,in_tok,out_tok,provider=await smart_router.chat(
                "groq","llama-3.3-70b-versatile",messages,
                f"You are Synthex Code. Synthesize into one perfect response with clean code.\n{li}\n\nAgent outputs:\n{ctx}",
                max_tokens,0.3,timeout=25,agent_role="synthesis")
        else:
            content=code_r.output or "Code generation failed. Please retry."
            in_tok,out_tok,provider=0,0,"error"
        r.final_response=content; r.agents_used=[a.agent_id for a in agents if a.success]
        r.agent_traces=[trace(a) for a in agents]
        r.total_input_tokens=sum(a.input_tokens for a in agents)+in_tok
        r.total_output_tokens=sum(a.output_tokens for a in agents)+out_tok
        r.total_cost_usd=calc_cost(provider,r.total_input_tokens,r.total_output_tokens)
        r.provider_used=provider; r.latency_ms=int((time.time()-start)*1000)
        return r

    async def _pro(self, messages, r, max_tokens, temperature, start, lang):
        # Parallel: reasoning
        rea_r = await reasoning_agent.run(messages,"Analyze thoroughly",max_tokens=1500)
        successful = [rea_r] if rea_r.success else []
        # Sequential: reflection
        if successful:
            ref_r = await reflection_agent.run(messages,"Critique the reasoning",
                context=f"Reasoning:\n{rea_r.output[:700]}",max_tokens=700)
            if ref_r.success: successful.append(ref_r)
        content = await self._synthesize(messages,successful,max_tokens,temperature,lang,premium=False)
        if settings.ENABLE_SAFETY_CHECK:
            try:
                ok,safe_c,_ = await safety_agent.check(content)
                if not ok and safe_c: content=safe_c
            except: pass
        r.final_response=content; r.agents_used=[a.agent_id for a in successful]+["synthesis"]
        r.agent_traces=[trace(a) for a in successful]
        r.total_input_tokens=sum(a.input_tokens for a in successful)
        r.total_output_tokens=sum(a.output_tokens for a in successful)
        r.total_cost_usd=sum(calc_cost(a.provider_used,a.input_tokens,a.output_tokens) for a in successful)
        r.latency_ms=int((time.time()-start)*1000)
        return r

    async def _ultra(self, messages, r, max_tokens, temperature, start, lang):
        # Parallel: reasoning + research + planning
        tasks=[
            reasoning_agent.run(messages,"Deep analysis, chain-of-thought",max_tokens=1500),
            research_agent.run(messages,"Gather all relevant facts and context",max_tokens=1000),
            planning_agent.run(messages,"Identify structure and best approach",max_tokens=800),
        ]
        outputs=await asyncio.gather(*tasks,return_exceptions=True)
        successful=[o for o in outputs if isinstance(o,AgentResult) and o.success]
        # Reflection
        if successful:
            ro=next((a.output for a in successful if a.agent_id=="reasoning"),"")
            if ro:
                ref_r=await reflection_agent.run(messages,"Deep critique",context=f"Reasoning:\n{ro[:900]}",max_tokens=800)
                if ref_r.success: successful.append(ref_r)
        # Debate (adversarial)
        if successful:
            ro=next((a.output for a in successful if a.agent_id=="reasoning"),"")
            if ro:
                deb_r=await debate_agent.run(messages,"Challenge the reasoning vigorously",context=f"Main reasoning:\n{ro[:600]}",max_tokens=600)
                if deb_r.success: successful.append(deb_r)
        content=await self._synthesize(messages,successful,max_tokens,temperature,lang,premium=True)
        if settings.ENABLE_SAFETY_CHECK:
            try:
                ok,safe_c,_=await safety_agent.check(content)
                if not ok and safe_c: content=safe_c
            except: pass
        r.final_response=content; r.agents_used=[a.agent_id for a in successful]+["synthesis","safety"]
        r.agent_traces=[trace(a) for a in successful]
        r.total_input_tokens=sum(a.input_tokens for a in successful)
        r.total_output_tokens=sum(a.output_tokens for a in successful)
        r.total_cost_usd=sum(calc_cost(a.provider_used,a.input_tokens,a.output_tokens) for a in successful)
        r.latency_ms=int((time.time()-start)*1000)
        return r

    async def _synthesize(self, messages, agents, max_tokens, temperature, lang, premium=False):
        li = "IMPORTANT: Respond entirely in Bengali (বাংলা)." if lang=="bn" else "Respond in clear English."
        if not agents:
            content,_,_,_=await smart_router.chat("groq","llama-3.3-70b-versatile",messages,
                f"You are Synthex, a highly intelligent AI assistant. {li}",max_tokens,temperature,
                timeout=20,agent_role="synthesis")
            return content
        ctx="\n\n---\n\n".join(f"[{a.agent_name}]\n{a.output}" for a in agents if a.output)
        role = "synthesis_premium" if premium else "synthesis"
        provider = "openrouter" if premium else "deepseek"
        model = "anthropic/claude-sonnet-4-5" if premium else "deepseek-chat"
        system=(f"{synthesis_agent.SYSTEM_PROMPT}\n\n{li}\n\n"
                f"Specialist outputs:\n{ctx}\n\n"
                f"Write the final unified response. Do NOT mention agents.")
        content,_,_,_=await smart_router.chat(provider,model,messages,system,
            max_tokens,temperature,timeout=25,agent_role=role)
        return content

    async def _memory(self, api_key_id, messages, response):
        try:
            from app.core.memory import get_memory
            mem=get_memory(api_key_id)
            parts=[f"{m.role}: {m.content[:250]}" for m in messages[-4:]]
            parts.append(f"assistant: {response[:250]}")
            extracted=await memory_agent.extract_context("\n".join(parts))
            for fact in extracted.get("key_facts",[]): mem.add_key_fact(fact) if fact else None
        except: pass

    async def stream(self, messages, model_id="synthex-nova-pro", max_tokens=2000,
                     temperature=0.7, api_key_id=None, language=None):
        model_id=normalise_model(model_id)
        if model_id=="synthex-nova-swift":
            async for chunk in self._stream_flash(messages,max_tokens,temperature,language):
                yield chunk
            return
        result=await self.run(messages,model_id,max_tokens,temperature,api_key_id,language)
        words=result.final_response.split(" ")
        for i,w in enumerate(words):
            yield w+(" " if i<len(words)-1 else "")
            await asyncio.sleep(0.008)

    async def _stream_flash(self, messages, max_tokens, temperature, lang):
        from app.providers import registry
        li="Respond in Bengali." if lang=="bn" else "Respond in English."
        groq=registry.get("groq")
        if groq and hasattr(groq,"stream"):
            try:
                async for chunk in groq.stream(messages=messages,model="llama-3.1-8b-instant",
                    system_prompt=f"You are Synthex Flash. {li}",
                    max_tokens=max_tokens,temperature=temperature):
                    yield chunk
                return
            except: pass
        # fallback
        r=PipelineResult()
        result=await self._flash(messages,r,max_tokens,temperature,time.time(),lang or "en")
        for i,w in enumerate(result.final_response.split(" ")):
            yield w+(" " if i<len(result.final_response.split(" "))-1 else "")
            await asyncio.sleep(0.01)


pipeline = SynthexPipeline()
