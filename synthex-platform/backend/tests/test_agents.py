"""Agent unit tests — verify structure and fallback logic."""
import pytest
import asyncio


def test_all_agents_importable():
    from app.agents import AGENT_REGISTRY, ALL_AGENTS
    assert len(AGENT_REGISTRY) >= 16
    required = ["reasoning","reflection","planning","research","coding",
                "finance","health","memory","synthesis","safety",
                "compression","tools","workflow","debate"]
    for a in required:
        assert a in AGENT_REGISTRY, f"Missing agent: {a}"


def test_all_agents_have_system_prompt():
    from app.agents import AGENT_REGISTRY
    for agent_id, agent in AGENT_REGISTRY.items():
        assert hasattr(agent, "SYSTEM_PROMPT"), f"{agent_id} missing SYSTEM_PROMPT"
        assert len(agent.SYSTEM_PROMPT) > 20, f"{agent_id} SYSTEM_PROMPT too short"


def test_synthesis_agent_prompt_valid():
    from app.agents import synthesis_agent
    p = synthesis_agent.SYSTEM_PROMPT
    assert "Synthesis" in p or "Lambda" in p
    assert "SYSTEM_PROMPT" not in p  # no double-nesting


def test_safety_agent_has_check():
    from app.agents import safety_agent
    assert hasattr(safety_agent, "check"), "safety_agent must have check() method"


def test_finance_safety_has_check():
    from app.agents.specialized import finance_safety_agent
    assert hasattr(finance_safety_agent, "check"), "finance_safety_agent must have check()"


def test_memory_agent_extract():
    from app.agents import memory_agent
    assert hasattr(memory_agent, "extract_context")


def test_compression_agent_compress():
    from app.agents import compression_agent
    assert hasattr(compression_agent, "compress")


def test_agent_base_timeout_positive():
    from app.agents import AGENT_REGISTRY
    for agent_id, agent in AGENT_REGISTRY.items():
        assert agent.timeout > 0, f"{agent_id} timeout must be positive"


def test_specialized_registry():
    from app.agents.specialized import SPECIALIZED_REGISTRY
    assert "finance_macro" in SPECIALIZED_REGISTRY
    assert "finance_safety" in SPECIALIZED_REGISTRY
    assert "web_search" in SPECIALIZED_REGISTRY
