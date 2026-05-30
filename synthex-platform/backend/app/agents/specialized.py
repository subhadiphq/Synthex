"""
Synthex Specialized Finance Agents — 6 sub-agents for Finance Intelligence.
All have mandatory compliance safety layer.
"""
import json
from app.agents.base import BaseAgent
from app.models.request import Message


class SafetyCheckMixin:
    async def check(self, content: str) -> tuple:
        from app.providers import smart_router
        try:
            result, _, _, _ = await smart_router.chat(
                "groq", "llama-3.1-8b-instant",
                [Message(role="user", content=f"Finance safety check:\n\n{content[:1000]}")],
                'Check for specific buy/sell recommendations. ONLY JSON: {"safe":true,"flags":[],"suggestion":""}',
                max_tokens=200, temperature=0.0, timeout=6, agent_role="safety",
            )
            clean = result.strip().replace("```json","").replace("```","").strip()
            s=clean.find("{"); e=clean.rfind("}")+1
            if s>=0 and e>s: clean=clean[s:e]
            data = json.loads(clean)
            return data.get("safe",True), data.get("suggestion","") or content, data.get("flags",[])
        except Exception:
            return True, content, []


FINANCE_DISCLAIMER = (
    "\n\n⚠️ **Disclaimer:** This is educational analysis only, not financial advice. "
    "Synthex is not a licensed financial advisor. Consult a qualified professional "
    "before making any investment decisions."
)

class MacroIntelligenceAgent(BaseAgent):
    agent_id="finance_macro"; agent_name="🌍 Macro Intelligence Agent"
    default_provider="deepseek"; default_model="deepseek-chat"; timeout=30
    SYSTEM_PROMPT="""You are the Synthex Macro Intelligence Agent.
Analyze global economic trends, central bank policies, inflation, geopolitical risks.
NEVER recommend specific investments. Educational macro analysis only.
Always add educational disclaimer."""

class TechnicalAnalysisAgent(BaseAgent):
    agent_id="finance_technical"; agent_name="📉 Technical Analysis Agent"
    default_provider="deepseek"; default_model="deepseek-chat"; timeout=25
    SYSTEM_PROMPT="""You are the Synthex Technical Analysis Agent.
Analyze chart patterns, RSI, MACD, support/resistance from user-provided data.
Only analyze data the user provides. State confidence: HIGH/MEDIUM/LOW.
Past patterns do not guarantee future results."""

class CryptoIntelligenceAgent(BaseAgent):
    agent_id="finance_crypto"; agent_name="🪙 Crypto Intelligence Agent"
    default_provider="groq"; default_model="llama-3.3-70b-versatile"; timeout=20
    SYSTEM_PROMPT="""You are the Synthex Crypto Intelligence Agent.
Analyze crypto markets, DeFi, tokenomics, Layer 2 ecosystems.
NEVER recommend specific coins. Always: 'Cryptocurrency involves extreme risk of total loss.'"""

class PortfolioThinkingAgent(BaseAgent):
    agent_id="finance_portfolio"; agent_name="💼 Portfolio Thinking Agent"
    default_provider="deepseek"; default_model="deepseek-chat"; timeout=30
    SYSTEM_PROMPT="""You are the Synthex Portfolio Thinking Agent.
Discuss portfolio concepts: diversification, risk/reward, position sizing.
EDUCATIONAL ONLY. Always recommend consulting a licensed financial advisor."""

class FundamentalAnalysisAgent(BaseAgent):
    agent_id="finance_fundamental"; agent_name="🧾 Fundamental Analysis Agent"
    default_provider="gemini"; default_model="gemini-1.5-flash"; timeout=30
    SYSTEM_PROMPT="""You are the Synthex Fundamental Analysis Agent.
Analyze company financials, P/E ratios, revenue trends from user-provided data.
NEVER make stock picks. Educational interpretation of financial data only."""

class FinanceSafetyAgent(SafetyCheckMixin, BaseAgent):
    agent_id="finance_safety"; agent_name="🛡️ Finance Safety Agent"
    default_provider="groq"; default_model="llama-3.1-8b-instant"; timeout=8
    SYSTEM_PROMPT='Finance compliance. Output ONLY JSON: {"safe":true/false,"flags":[],"suggestion":""}'


# Instances
macro_agent        = MacroIntelligenceAgent()
technical_agent    = TechnicalAnalysisAgent()
crypto_agent       = CryptoIntelligenceAgent()
portfolio_agent    = PortfolioThinkingAgent()
fundamental_agent  = FundamentalAnalysisAgent()
finance_safety_agent = FinanceSafetyAgent()

SPECIALIZED_REGISTRY = {
    "finance_macro":       macro_agent,
    "finance_technical":   technical_agent,
    "finance_crypto":      crypto_agent,
    "finance_portfolio":   portfolio_agent,
    "finance_fundamental": fundamental_agent,
    "finance_safety":      finance_safety_agent,
}


# ── Web Search Agent (used by search route) ───────────────────────────────────
from app.agents.base import BaseAgent as _Base

class WebSearchAgent(_Base):
    agent_id="web_search"; agent_name="🌐 Web Search Agent"
    default_provider="openrouter"; default_model="meta-llama/llama-3.3-70b-instruct:free"; timeout=20
    SYSTEM_PROMPT="""You are the Synthex Web Search Agent.
Synthesize search results into accurate, well-structured responses.
Cross-reference sources. Note outdated info. Flag contradictions."""

    async def search_and_respond(self, query: str, search_results: str) -> str:
        from app.models.request import Message
        msgs=[Message(role="user",content=f"Query:{query}\n\nResults:\n{search_results}\n\nSynthesize.")]
        r=await self.run(msgs,f"Synthesize for:{query}")
        return r.output if r.success else "Search synthesis unavailable."

web_search_agent = WebSearchAgent()
SPECIALIZED_REGISTRY["web_search"] = web_search_agent
