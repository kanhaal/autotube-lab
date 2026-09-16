from app.scripting.engine import OllamaScriptEngine


def test_ollama_uses_qwen35_9b_by_default(monkeypatch):
    monkeypatch.delenv("AUTOTUBE_LLM_MODEL", raising=False)

    engine = OllamaScriptEngine()

    assert engine.model == "qwen3.5:9b"


def test_ollama_model_can_be_overridden_by_environment(monkeypatch):
    monkeypatch.setenv("AUTOTUBE_LLM_MODEL", "qwen3:8b")

    engine = OllamaScriptEngine()

    assert engine.model == "qwen3:8b"
