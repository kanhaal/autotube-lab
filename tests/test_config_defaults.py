from __future__ import annotations

from pathlib import Path


def test_env_example_documents_professional_media_defaults():
    text = Path(".env.example").read_text(encoding="utf-8")
    expected = {
        "AUTOTUBE_RENDERER=professional",
        "AUTOTUBE_TTS_BACKEND=chatterbox",
        "AUTOTUBE_LLM_MODEL=qwen3.5:9b",
        "AUTOTUBE_CAPTION_MODEL=small.en",
        "AUTOTUBE_AUDIO_LIBRARY=config/audio/library.yml",
    }
    for line in expected:
        assert line in text


def test_windows_setup_checks_local_media_dependencies_without_downloading_models():
    text = Path("scripts/setup_windows.ps1").read_text(encoding="utf-8").lower()
    for dependency in ("python", "ffmpeg", "ffprobe", "ollama", "node", "npm"):
        assert dependency in text
    assert "npm ci" in text
    assert "& ollama pull" not in text
    assert "ollama pull qwen3.5:9b" in text


def test_scheduled_task_remains_render_only_during_supervised_rollout():
    text = Path("scripts/install_task.ps1").read_text(encoding="utf-8")
    assert "run-daily --render" in text
    assert "run-daily --live" not in text
