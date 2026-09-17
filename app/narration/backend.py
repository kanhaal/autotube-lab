from __future__ import annotations

from pathlib import Path
from typing import Protocol


class TTSBackend(Protocol):
    name: str

    def synthesize(self, text: str, out: Path, voice_profile: str) -> Path:
        ...


class ConfiguredTTS:
    def __init__(self, backend: TTSBackend, voice_profile: str):
        self.backend = backend
        self.voice_profile = voice_profile
        self.name = getattr(backend, "name", backend.__class__.__name__.lower())

    def synthesize(self, text: str, out: Path) -> Path:
        return self.backend.synthesize(text, out, self.voice_profile)


def select_tts_backend(name: str, **deps):
    normalized = name.strip().lower()
    if normalized == "chatterbox":
        from app.narration.chatterbox import ChatterboxTTS

        return ChatterboxTTS(**deps)
    if normalized == "kokoro":
        from app.narration.kokoro import KokoroTTS

        return KokoroTTS(**deps)
    if normalized == "sapi":
        from app.narration.tts import WindowsSapiTTS

        return WindowsSapiTTS()
    raise ValueError(f"Unknown TTS backend: {name}")
