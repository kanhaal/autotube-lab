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
        "AUTOTUBE_VISUAL_CRITIC=0",
    }
    for line in expected:
        assert line in text


def test_windows_setup_checks_local_media_dependencies_without_downloading_models():
    text = Path("scripts/setup_windows.ps1").read_text(encoding="utf-8").lower()
    for dependency in ("python", "ffmpeg", "ffprobe", "ollama", "node", "npm"):
        assert dependency in text
    assert Path("video/package-lock.json").is_file()
    assert "npm ci" in text
    assert "npm install" not in text
    assert "& ollama pull" not in text
    assert "ollama pull qwen3.5:9b" in text


def test_scheduled_task_remains_render_only_during_supervised_rollout():
    text = Path("scripts/install_task.ps1").read_text(encoding="utf-8")
    assert "run-daily --render" in text
    assert "run-daily --live" not in text


def test_caption_transcriber_defaults_can_be_overridden_by_environment(monkeypatch):
    from app.captions.align import FasterWhisperTranscriber

    monkeypatch.setenv("AUTOTUBE_CAPTION_MODEL", "medium.en")
    monkeypatch.setenv("AUTOTUBE_CAPTION_DEVICE", "cpu")
    monkeypatch.setenv("AUTOTUBE_CAPTION_COMPUTE_TYPE", "int8")

    transcriber = FasterWhisperTranscriber()

    assert transcriber.model_size == "medium.en"
    assert transcriber.device == "cpu"
    assert transcriber.compute_type == "int8"


def test_cli_tts_backend_can_be_overridden_by_environment(monkeypatch):
    import app.narration.backend as backend
    from app.cli import _build_channel_tts

    selected = []

    class FakeBackend:
        name = "fake"

        def synthesize(self, text, out, voice_profile):
            return out

    def select(name, **deps):
        selected.append(name)
        return FakeBackend()

    monkeypatch.setattr(backend, "select_tts_backend", select)
    monkeypatch.setenv("AUTOTUBE_TTS_BACKEND", "kokoro")

    _build_channel_tts(
        {
            "voice": {
                "profile": "default",
                "backend": "chatterbox",
                "fallback_backend": "kokoro",
            }
        }
    )

    assert selected[0] == "kokoro"
