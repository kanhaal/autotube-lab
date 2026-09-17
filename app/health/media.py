from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def _result(ok: bool | None, detail: str = "") -> dict[str, Any]:
    return {"ok": ok, "detail": detail}


def _run(command: list[str], *, cwd: Path | None = None, timeout: int = 30):
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def _tool(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    return _result(path is not None, path or "not found")


def _module(name: str) -> dict[str, Any]:
    available = importlib.util.find_spec(name) is not None
    return _result(available, "importable" if available else "not installed")


def _command_version(name: str) -> dict[str, Any]:
    executable = shutil.which(name)
    if executable is None:
        return _result(False, "not found")
    try:
        completed = _run([executable, "--version"])
    except (OSError, subprocess.SubprocessError) as exc:
        return _result(False, str(exc))
    detail = (completed.stdout or completed.stderr).strip().splitlines()
    return _result(completed.returncode == 0, detail[0] if detail else "")


def _ollama_model() -> dict[str, Any]:
    executable = shutil.which("ollama")
    if executable is None:
        return _result(False, "ollama not found")
    model = os.getenv("AUTOTUBE_LLM_MODEL", "qwen3.5:9b")
    try:
        completed = _run([executable, "list"])
    except (OSError, subprocess.SubprocessError) as exc:
        return _result(False, str(exc))
    found = completed.returncode == 0 and any(
        line.split()[0] == model for line in completed.stdout.splitlines() if line.split()
    )
    return _result(found, model if found else f"{model} not installed")


def _remotion() -> dict[str, Any]:
    npm = shutil.which("npm")
    if npm is None:
        return _result(False, "npm not found")
    try:
        completed = _run(
            [npm, "--prefix", "video", "list", "@remotion/cli", "--depth=0"],
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return _result(False, str(exc))
    output = (completed.stdout + completed.stderr).strip()
    return _result(completed.returncode == 0, output)


def _nvenc() -> dict[str, Any]:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        return _result(False, "ffmpeg not found")
    try:
        completed = _run([ffmpeg, "-hide_banner", "-encoders"])
    except (OSError, subprocess.SubprocessError) as exc:
        return _result(False, str(exc))
    output = completed.stdout + completed.stderr
    available = completed.returncode == 0 and "h264_nvenc" in output
    return _result(available, "h264_nvenc" if available else "NVENC encoder unavailable")


def _deep_chatterbox() -> dict[str, Any]:
    if importlib.util.find_spec("chatterbox") is None:
        return _result(False, "not installed")
    backend = None
    try:
        from app.narration.chatterbox import ChatterboxTTS

        backend = ChatterboxTTS()
        model = backend._load_model()
        return _result(model is not None, "model loaded and released")
    except Exception as exc:  # noqa: BLE001 - health probe must report rather than abort
        return _result(False, str(exc))
    finally:
        if backend is not None:
            backend.release()


def _deep_whisper() -> dict[str, Any]:
    if importlib.util.find_spec("faster_whisper") is None:
        return _result(False, "not installed")
    transcriber = None
    try:
        from app.captions.align import FasterWhisperTranscriber

        transcriber = FasterWhisperTranscriber()
        model = transcriber._load_model()
        detail = f"{transcriber.model_size} on {transcriber.device} loaded and released"
        return _result(model is not None, detail)
    except Exception as exc:  # noqa: BLE001 - health probe must report rather than abort
        return _result(False, str(exc))
    finally:
        if transcriber is not None:
            transcriber.release()


def _tiny_render() -> dict[str, Any]:
    node = shutil.which("node")
    npm = shutil.which("npm")
    npx = shutil.which("npx")
    if node is None or npm is None or npx is None:
        return _result(False, "node/npm/npx unavailable")
    video_dir = Path("video")
    fixture = video_dir / "media-smoke-props.json"
    if not fixture.is_file():
        return _result(False, f"missing fixture: {fixture}")
    try:
        with tempfile.TemporaryDirectory(prefix="autotube-media-smoke-") as tmp:
            target = Path(tmp) / "tiny.mp4"
            completed = _run(
                [
                    npx,
                    "remotion",
                    "render",
                    "src/index.ts",
                    "KernelRushLong",
                    str(target),
                    "--props=media-smoke-props.json",
                ],
                cwd=video_dir,
                timeout=300,
            )
            if completed.returncode != 0:
                return _result(False, (completed.stderr or completed.stdout).strip())
            return _result(target.is_file() and target.stat().st_size > 0, str(target))
    except (OSError, subprocess.SubprocessError) as exc:
        return _result(False, str(exc))


def run_media_smoke(*, deep: bool = False) -> dict[str, dict[str, Any]]:
    """Report local professional-media readiness without raising for missing optional tools."""

    report = {
        "ollama_model": _ollama_model(),
        "node": _command_version("node"),
        "npm": _command_version("npm"),
        "remotion": _remotion(),
        "ffmpeg": _tool("ffmpeg"),
        "ffprobe": _tool("ffprobe"),
        "nvenc": _nvenc(),
        "chatterbox": _module("chatterbox"),
        "kokoro": _module("kokoro"),
        "faster_whisper": _module("faster_whisper"),
        "tiny_render": _result(None, "skipped; use --deep"),
    }
    if deep:
        report["chatterbox"] = _deep_chatterbox()
        report["faster_whisper"] = _deep_whisper()
        report["tiny_render"] = _tiny_render()
    return report
