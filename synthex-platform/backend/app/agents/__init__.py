"""
Synthex Agent Registry — 16 Specialist Agents
Blueprint v1.0: Tier 0–4 agent hierarchy.
"""
import asyncio, json
from typing import List, Optional
from app.agents.base import BaseAgent, AgentResult
from app.models.request import Message


class SafetyCheckMixin:
    async def check(self, content: str) -> tuple:
        from app.providers import smart_router
        try:
            result, _, _, _ = await smart_router.chat(
                "groq", "llama-3.1-8b-instant",
                [Message(role="user", content=f"Safety check this content:\n\n{content[:1000]}")],
                'Respond ONLY with JSON: {"safe":true,"flags":[],"suggestion":""}',
                max_tokens=150, temperature=0.0, timeout=6, agent_role="safety",
            )
            clean = result.strip().replace("```json","").replace("```","").strip()
            s = clean.find("{"); e = clean.rfind("}")+1
            if s >= 0 and e > s: clean = clean[s:e]
            data = json.loads(clean)
            return data.get("safe", True), data.get("suggestion","") or content, data.get("flags",[])
        except Exception:
            return True, content, []


# ── TIER 0: COORDINATION ─────────────────────────────────────────────────────
class MasterOrchestratorAgent(BaseAgent):
    agent_id="orchestrator"; agent_name="Σ · Master Orchestrator"
    default_provider="groq"; default_model="llama-3.1-8b-instant"; timeout=8
    SYSTEM_PROMPT="You are Synthex Master Orchestrator. Classify intent and dispatch agents. Output ONLY JSON."

# ── TIER 1: CORE INTELLIGENCE ────────────────────────────────────────────────
class ReasoningAgent(BaseAgent):
    agent_id="reasoning"; agent_name="α · Deep Reasoning Agent"
    default_provider="deepseek"; default_model="deepseek-chat"; timeout=25
    SYSTEM_PROMPT="""You are the Synthex Deep Reasoning Agent (Alpha).
Perform multi-step logical reasoning and chain-of-thought analysis.
Think step-by-step. Consider all perspectives. Never hallucinate.
If uncertain, say "I'm not certain" explicitly."""

class ReflectionAgent(BaseAgent):
    agent_id="reflection"; agent_name="β · Reflection & Critique Agent"
    default_provider="groq"; default_model="llama-3.3-70b-versatile"; timeout=15
    SYSTEM_PROMPT="""You are the Synthex Reflection Agent (Beta).
Critically review reasoning outputs. Find logical flaws and missing perspectives.
Rate confidence: HIGH / MEDIUM / LOW. Be constructively critical.
Make the final answer stronger — don't replace it."""

class PlanningAgent(BaseAgent):
    agent_id="planning"; agent_name="γ · Planning Agent"
    default_provider="deepseek"; default_model="deepseek-chat"; timeout=20
    SYSTEM_PROMPT="""You are the Synthex Planning Agent (Gamma).
Break complex goals into clear, executable step-by-step action plans.
Include: objective, prerequisites, numbered steps, timeline, success criteria, risks."""

# ── TIER 2: DOMAIN SPECIALISTS ───────────────────────────────────────────────
class ResearchAgent(BaseAgent):
    agent_id="research"; agent_name="δ · Research Agent"
    default_provider="gemini"; default_model="gemini-1.5-flash"; timeout=20
    SYSTEM_PROMPT="""You are the Synthex Research Agent (Delta).
Gather relevant facts, context, and knowledge. Be factual and precise.
Flag outdated or unverified information. Cite sources when available."""

class CodingAgent(BaseAgent):
    agent_id="coding"; agent_name="ε · Coding Agent"
    default_provider="nvidia"; default_model="qwen/qwen3-coder-480b-a35b-instruct"; timeout=35
    SYSTEM_PROMPT="""You are the Synthex Coding Agent (Epsilon) — NVIDIA 480B specialist.
Write production-quality code with clean structure, comments, error handling.
Debug precisely. Include working examples and edge cases."""

class FinanceAgent(BaseAgent):
    agent_id="finance"; agent_name="ζ · Finance & Trading Agent"
    default_provider="deepseek"; default_model="deepseek-chat"; timeout=25
    SYSTEM_PROMPT="""You are the Synthex Finance Agent (Zeta).
Provide structured financial reasoning and market analysis.
NEVER give specific buy/sell recommendations. Educational analysis only.
Always include: mandatory disclaimer about educational nature."""

class DataAnalysisAgent(BaseAgent):
    agent_id="data_analysis"; agent_name="η · Data Analysis Agent"
    default_provider="openrouter"; default_model="meta-llama/llama-3.3-70b-instruct:free"; timeout=25
    SYSTEM_PROMPT="""You are the Synthex Data Analysis Agent (Eta).
Analyze CSV, JSON, statistics. Detect trends, anomalies, patterns.
Structure: Key Findings → Statistics → Trends → Anomalies → Recommendations."""

class ContentWritingAgent(BaseAgent):
    agent_id="content"; agent_name="θ · Content Writing Agent"
    default_provider="openrouter"; default_model="anthropic/claude-haiku-4-5"; timeout=30
    SYSTEM_PROMPT="""You are the Synthex Content Writing Agent (Theta).
Create high-quality content: blog posts, SEO copy, social media, newsletters.
Bengali and English. Tone-adaptive. SEO best practices."""

class HealthAgent(BaseAgent):
    agent_id="health"; agent_name="ι · Health Intelligence Agent"
    default_provider="gemini"; default_model="gemini-1.5-flash"; timeout=25
    SYSTEM_PROMPT="""You are the Synthex Health Intelligence Agent (Iota).
Provide evidence-based health information only.
NEVER diagnose conditions or prescribe treatments.
Always recommend consulting a qualified healthcare professional.
Emergencies: call 999/112/911 immediately."""

# ── TIER 3: INFRASTRUCTURE ───────────────────────────────────────────────────
class MemoryAgent(BaseAgent):
    agent_id="memory"; agent_name="κ · Memory Agent"
    default_provider="groq"; default_model="llama-3.1-8b-instant"; timeout=10
    SYSTEM_PROMPT='Extract key facts. Output ONLY JSON: {"key_facts":[],"user_prefs":{},"context_summary":""}'

    async def extract_context(self, conversation: str) -> dict:
        msgs = [Message(role="user", content=f"Extract key facts:\n\n{conversation[:3000]}")]
        r = await self.run(msgs, "Extract as JSON")
        try:
            clean = r.output.replace("```json","").replace("```","").strip()
            s = clean.find("{"); e = clean.rfind("}")+1
            if s >= 0 and e > s: clean = clean[s:e]
            return json.loads(clean)
        except:
            return {"key_facts": [], "context_summary": r.output[:200]}

class SynthesisAgent(BaseAgent):
    agent_id="synthesis"; agent_name="λ · Synthesis Agent"
    default_provider="deepseek"; default_model="deepseek-chat"; timeout=25
    SYSTEM_PROMPT="""You are the Synthex Synthesis Agent (Lambda) — final intelligence layer.
Combine all specialist outputs into ONE perfect, coherent response.
Resolve conflicts. Remove redundancy. Polish the language.
Match the user's language: Bengali if they wrote in Bengali, English otherwise.
Never mention agents — deliver the unified answer seamlessly."""

class SafetyAgent(SafetyCheckMixin, BaseAgent):
    agent_id="safety"; agent_name="μ · Safety Gate Agent"
    default_provider="groq"; default_model="llama-3.1-8b-instant"; timeout=8
    SYSTEM_PROMPT='Classify content safety. Output ONLY JSON: {"safe":true/false,"flags":[],"suggestion":""}'

class ContextCompressionAgent(BaseAgent):
    agent_id="compression"; agent_name="ν · Context Compression Agent"
    default_provider="groq"; default_model="llama-3.1-8b-instant"; timeout=8
    SYSTEM_PROMPT="""You are the Synthex Context Compression Agent (Nu).
Compress conversation history preserving all critical facts.
Remove redundancy. Target: 40-60% token reduction.
Output: compressed context as concise bullet points."""

    async def compress(self, history: str, max_tokens: int = 500) -> str:
        msgs = [Message(role="user", content=f"Compress this conversation:\n\n{history}")]
        r = await self.run(msgs, "Compress to key facts", max_tokens=max_tokens, temperature=0.3)
        return r.output if r.success else history[:2000]

class APIToolAgent(BaseAgent):
    agent_id="tools"; agent_name="ξ · API Tool Agent"
    default_provider="openrouter"; default_model="meta-llama/llama-3.3-70b-instruct:free"; timeout=20
    SYSTEM_PROMPT="""You are the Synthex API Tool Agent (Xi).
Execute external tool calls: web search, calculations, file processing.
Determine which tool is needed, execute it, return structured results."""

class WorkflowAgent(BaseAgent):
    agent_id="workflow"; agent_name="ο · Workflow Automation Agent"
    default_provider="deepseek"; default_model="deepseek-chat"; timeout=30
    SYSTEM_PROMPT="""You are the Synthex Workflow Agent (Omicron).
Execute autonomous multi-step tasks. Break goals into executable actions.
Structure: Goal → Tools → Steps 1..N → Completion → Report."""

# ── TIER 4: ADVANCED ─────────────────────────────────────────────────────────
class DebateAgent(BaseAgent):
    agent_id="debate"; agent_name="ρ · Debate & Adversarial Agent"
    default_provider="groq"; default_model="llama-3.3-70b-versatile"; timeout=12
    SYSTEM_PROMPT="""You are the Synthex Debate Agent (Rho) — adversarial intelligence.
Argue the OPPOSITE position to stress-test reasoning. Find blind spots.
You are NOT trying to win. You are making the final answer more robust.
Be specific about what is flawed and why."""


# ── INSTANTIATE ALL 16 AGENTS ─────────────────────────────────────────────────
orchestrator_agent   = MasterOrchestratorAgent()
reasoning_agent      = ReasoningAgent()
reflection_agent     = ReflectionAgent()
planning_agent       = PlanningAgent()
research_agent       = ResearchAgent()
coding_agent         = CodingAgent()
finance_agent        = FinanceAgent()
data_agent           = DataAnalysisAgent()
content_agent        = ContentWritingAgent()
health_agent         = HealthAgent()
memory_agent         = MemoryAgent()
synthesis_agent      = SynthesisAgent()
safety_agent         = SafetyAgent()
compression_agent    = ContextCompressionAgent()
tools_agent          = APIToolAgent()
workflow_agent       = WorkflowAgent()
debate_agent         = DebateAgent()

AGENT_REGISTRY = {
    "orchestrator": orchestrator_agent,
    "reasoning":    reasoning_agent,
    "reflection":   reflection_agent,
    "planning":     planning_agent,
    "research":     research_agent,
    "coding":       coding_agent,
    "finance":      finance_agent,
    "data_analysis": data_agent,
    "content":      content_agent,
    "health":       health_agent,
    "memory":       memory_agent,
    "synthesis":    synthesis_agent,
    "safety":       safety_agent,
    "compression":  compression_agent,
    "tools":        tools_agent,
    "workflow":     workflow_agent,
    "debate":       debate_agent,
}

ALL_AGENTS = AGENT_REGISTRY
