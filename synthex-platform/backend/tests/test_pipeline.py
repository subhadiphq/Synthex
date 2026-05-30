"""Pipeline unit tests."""
import pytest


def test_pipeline_result_defaults():
    from app.core.pipeline import PipelineResult
    r = PipelineResult()
    assert r.request_id.startswith("sx-")
    assert r.agents_used == []
    assert r.total_cost_usd == 0.0
    assert r.final_response == ""


def test_detect_language_english():
    from app.core.pipeline import detect_language
    assert detect_language("Hello world") == "en"
    assert detect_language("") == "en"
    assert detect_language("What is AI?") == "en"


def test_detect_language_bengali():
    from app.core.pipeline import detect_language
    assert detect_language("আমি বাংলায় কথা বলছি") == "bn"
    assert detect_language("আপনি কেমন আছেন?") == "bn"


def test_normalise_model_legacy():
    from app.core.pipeline import normalise_model
    assert normalise_model("synthex-nova-ultra") == "synthex-nova-ultra"
    assert normalise_model("synthex-nova-pro")   == "synthex-nova-pro"
    assert normalise_model("synthex-nova-swift") == "synthex-nova-swift"
    assert normalise_model("synthex-nova-forge") == "synthex-nova-forge"
    assert normalise_model("synthex-nova-pro")   == "synthex-nova-pro"


def test_calc_cost():
    from app.core.pipeline import calc_cost
    cost = calc_cost("deepseek", 1000, 500)
    assert cost > 0
    cost_free = calc_cost("groq", 1000, 500)
    assert cost_free >= 0
    cost_unknown = calc_cost("unknown", 1000, 500)
    assert cost_unknown == 0.0


def test_orchestrator_fallback_plan():
    from app.core.orchestrator import MasterOrchestrator
    orch = MasterOrchestrator()
    config = orch.get_agent_config("general", "moderate", "synthex-nova-pro")
    assert "run_reasoning" in config
    assert config["run_reasoning"] is True


def test_orchestrator_flash_config():
    from app.core.orchestrator import MasterOrchestrator
    orch = MasterOrchestrator()
    config = orch.get_agent_config("general", "simple", "synthex-nova-swift")
    assert config["run_reflection"] is False
    assert config["run_debate"] is False


def test_pipeline_instance():
    from app.core.pipeline import pipeline, SynthexPipeline
    assert isinstance(pipeline, SynthexPipeline)
