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
        if command[:2] == ["/bin/ollama", "list"]:
            return SimpleNamespace(returncode=0, stdout="qwen3.5:9b 123 MB\n", stderr="")
        if command[0] in {"/bin/node", "/bin/npm"} and "list" not in command:
            return SimpleNamespace(returncode=0, stdout="v22.0.0\n", stderr="")
        if "-encoders" in command:
            return SimpleNamespace(returncode=0, stdout="V..... h264_nvenc NVIDIA NVENC\n", stderr="")
        if command[0] == "/bin/npm" and "list" in command:
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


def test_media_smoke_uses_resolved_windows_command_shims(monkeypatch):
    from app.health import media

    resolved = {
        "node": r"C:\Program Files\nodejs\node.exe",
        "npm": r"C:\Program Files\nodejs\npm.cmd",
        "npx": r"C:\Program Files\nodejs\npx.cmd",
        "ffmpeg": r"C:\ffmpeg\bin\ffmpeg.exe",
        "ffprobe": r"C:\ffmpeg\bin\ffprobe.exe",
        "ollama": r"C:\Program Files\Ollama\ollama.exe",
    }
    monkeypatch.setattr(media.shutil, "which", lambda name: resolved.get(name))
    monkeypatch.setattr(media.importlib.util, "find_spec", lambda name: None)

    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        if command[0] == resolved["ollama"]:
            return SimpleNamespace(returncode=0, stdout="qwen3.5:9b 6.6 GB\n", stderr="")
        if command[0] in {resolved["node"], resolved["npm"]}:
            return SimpleNamespace(returncode=0, stdout="v24.0.0\n", stderr="")
        if command[0] == resolved["ffmpeg"]:
            return SimpleNamespace(returncode=0, stdout="V..... h264_nvenc\n", stderr="")
        raise AssertionError(command)

    monkeypatch.setattr(media.subprocess, "run", fake_run)

    result = media.run_media_smoke(deep=False)

    assert result["npm"]["ok"] is True
    assert result["remotion"]["ok"] is True
    assert any(command[0] == resolved["npm"] for command in commands)


def test_tiny_render_uses_resolved_windows_npx_shim(monkeypatch):
    from pathlib import Path

    from app.health import media

    resolved = {
        "node": r"C:\Program Files\nodejs\node.exe",
        "npm": r"C:\Program Files\nodejs\npm.cmd",
        "npx": r"C:\Program Files\nodejs\npx.cmd",
    }
    monkeypatch.setattr(media.shutil, "which", lambda name: resolved.get(name))

    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        Path(command[5]).write_bytes(b"video")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(media.subprocess, "run", fake_run)

    result = media._tiny_render()

    assert result["ok"] is True
    assert commands[0][0] == resolved["npx"]


def test_media_subprocess_decodes_utf8_with_replacement(monkeypatch):
    from app.health import media

    captured = {}

    def fake_run(command, **kwargs):
        captured.update(kwargs)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(media.subprocess, "run", fake_run)
    media._run(["tool"])

    assert captured["encoding"] == "utf-8"
    assert captured["errors"] == "replace"


def test_deep_whisper_forces_real_transcription_inference(monkeypatch):
    from app.captions import align
    from app.health import media

    calls = {"transcribe": 0, "release": 0}

    class FakeTranscriber:
        model_size = "small.en"
        device = "cpu"
        compute_type = "int8"
        fallback_reason = "Library cublas64_12.dll is not found or cannot be loaded"

        def transcribe(self, path, word_timestamps=True, vad_filter=True):
            calls["transcribe"] += 1
            assert word_timestamps is False
            assert vad_filter is False
            return iter([SimpleNamespace(text="")]), SimpleNamespace(language="en")

        def release(self):
            calls["release"] += 1

    monkeypatch.setattr(media.importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(align, "FasterWhisperTranscriber", FakeTranscriber)

    result = media._deep_whisper()

    assert result["ok"] is True
    assert calls == {"transcribe": 1, "release": 1}
    assert "CPU fallback" in result["detail"]


def test_media_smoke_missing_tools_are_reported_not_raised(monkeypatch):
    from app.health import media

    monkeypatch.setattr(media.shutil, "which", lambda name: None)
    monkeypatch.setattr(media.importlib.util, "find_spec", lambda name: None)

    result = media.run_media_smoke(deep=False)

    assert result["ffmpeg"]["ok"] is False
    assert result["ollama_model"]["ok"] is False
    assert result["chatterbox"]["ok"] is False
    assert result["tiny_render"]["ok"] is None
