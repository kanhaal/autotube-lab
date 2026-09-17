from __future__ import annotations

import importlib.util
import shutil


def media_health() -> dict[str, bool]:
    return {
        "chatterbox": importlib.util.find_spec("chatterbox") is not None,
        "kokoro": importlib.util.find_spec("kokoro") is not None,
        "faster_whisper": importlib.util.find_spec("faster_whisper") is not None,
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "ffprobe": shutil.which("ffprobe") is not None,
    }
