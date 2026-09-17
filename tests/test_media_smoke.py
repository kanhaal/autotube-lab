from __future__ import annotations

from types import SimpleNamespace


def test_media_smoke_reports_lightweight_dependency_state(monkeypatch):
    from app.health import media

    available = {"ffmpeg", "ffprobe", "node", "npm", "ollama"}
    monkeypatch.setattr(media.shutil, "which", lambda name: f"/bin/{name}" if name in available else None)
    monkeypatch.setattr(
        media.importlib.util,
        "find_spec",
        lambda name: object() if name in {"chatterbox", "kokoro", "faster_whisper"} else None,
    )

    def fake_run(command, **kwargs):
        joined = " ".join(command)
        if command[:2] == ["ollama", "list"]:
            return SimpleNamespace(returncode=0, stdout="qwen3.5:9b 123 MB\n", stderr="")
        if command[0] in {"node", "npm"}:
            return SimpleNamespace(returncode=0, stdout="v22.0.0\n", stderr="")
        if "-encoders" in command:
            return SimpleNamespace(returncode=0, stdout="V..... h264_nvenc NVIDIA NVENC\n", stderr="")
        if "npm" in command and "list" in command:
            return SimpleNamespace(returncode=0, stdout="@remotion/cli@4\n", stderr="")
        raise AssertionError(joined)

    monkeypatch.setattr(media.subprocess, "run", fake_run)

    result = media.run_media_smoke(deep=False)

    assert result["ollama_model"]["ok"] is True
    assert result["node"]["ok"] is True
    assert result["npm"]["ok"] is True
    assert result["remotion"]["ok"] is True
    assert result["ffmpeg"]["ok"] is True
    assert result["ffprobe"]["ok"] is True
    assert result["nvenc"]["ok"] is True
    assert result["chatterbox"]["ok"] is True
    assert result["kokoro"]["ok"] is True
    assert result["faster_whisper"]["ok"] is True
    assert result["tiny_render"]["ok"] is None


def test_media_smoke_missing_tools_are_reported_not_raised(monkeypatch):
    from app.health import media

    monkeypatch.setattr(media.shutil, "which", lambda name: None)
    monkeypatch.setattr(media.importlib.util, "find_spec", lambda name: None)

    result = media.run_media_smoke(deep=False)

    assert result["ffmpeg"]["ok"] is False
    assert result["ollama_model"]["ok"] is False
    assert result["chatterbox"]["ok"] is False
    assert result["tiny_render"]["ok"] is None
