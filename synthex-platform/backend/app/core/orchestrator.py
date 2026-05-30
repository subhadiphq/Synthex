"""
Synthex Master Orchestrator Agent
The central brain that receives all requests, classifies intent,
decomposes tasks, dispatches agents, and manages the pipeline.
"""

import json
import asyncio
from typing import List, Optional
from app.models.request import Message
from app.providers import smart_router
from app.config import settings


ORCHESTRATOR_SYSTEM = """You are the Synthex Master Orchestrator — the intelligent coordinator of a multi-agent AI system.

Your job:
1. Analyze the user's request carefully
2. Classify the primary intent
3. Assign specific tasks to each specialist agent

Respond ONLY with valid JSON (no markdown, no explanation):
{
  "intent": "one of: chat|code|research|analysis|writing|math|planning|finance|health|general",
  "complexity": "one of: simple|moderate|complex",
  "reasoning_task": "what the reasoning agent should focus on",
  "reflection_task": "what to critically verify or challenge",
  "research_task": "what facts or context to gather (or 'none' if not needed)",
  "synthesis_guidance": "how to combine the outputs into a great final answer",
  "response_language": "en or bn based on user's message language"
}"""


class MasterOrchestrator:
    """
    Orchestrates the full multi-agent pipeline.
    Every request goes through this orchestrator.
    """

    async def analyze(
        self,
        messages: List[Message],
        model_id: str = "synthex-nova-pro",
    ) -> dict:
        """
        Step 1: Analyze request and create agent task plan.
        Returns orchestration plan as dict.
        """
        # Use latest user message for classification
        user_message = next(
            (m.content for m in reversed(messages) if m.role == "user"),
            ""
        )

        prompt = f"""User request: "{user_message}"
Model requested: {model_id}

Create the orchestration plan."""

        try:
            content, _, _ , _ = await smart_router.chat(
                provider_name="groq",  # Fast classification
                model="llama-3.1-8b-instant",
                messages=[Message(role="user", content=prompt)],
                system_prompt=ORCHESTRATOR_SYSTEM,
                max_tokens=400,
                temperature=0.3,
                timeout=8,
            )

            # Parse JSON response
            clean = content.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            clean = clean.strip()

            plan = json.loads(clean)
            return plan

        except (json.JSONDecodeError, Exception):
            # Fallback plan if orchestrator fails
            return {
                "intent": "general",
                "complexity": "moderate",
                "reasoning_task": "Analyze and respond to the user's request thoroughly",
                "reflection_task": "Verify accuracy and completeness of the response",
                "research_task": "none",
                "synthesis_guidance": "Combine insights into a clear, helpful response",
                "response_language": "en",
            }

    def get_agent_config(self, intent: str, complexity: str, model_id: str) -> dict:
        """
        Determine which agents to run based on intent and model.
        """
        from app.models.synthex import get_model
        model = get_model(model_id)

        config = {
            "run_reasoning": True,
            "run_reflection": True,
            "run_research": False,
            "run_debate": False,
            "run_safety": settings.ENABLE_SAFETY_CHECK,
        }

        if model_id == "synthex-nova-swift":
            # Flash mode — single agent, no extra steps
            return {
                "run_reasoning": True,
                "run_reflection": False,
                "run_research": False,
                "run_debate": False,
                "run_safety": settings.ENABLE_SAFETY_CHECK,
            }

        if model_id == "synthex-nova-ultra":
            # Ultra — all agents
            config["run_research"] = True
            config["run_debate"] = True

        if model_id == "synthex-nova-pro":
            if intent in ["research", "analysis", "finance"] or complexity == "complex":
                config["run_research"] = True

        return config


orchestrator = MasterOrchestrator()


# Language detection helper
def detect_language(text: str) -> str:
    """Detect if text is Bengali or English."""
    bengali_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
    return "bn" if bengali_chars > len(text) * 0.1 else "en"
