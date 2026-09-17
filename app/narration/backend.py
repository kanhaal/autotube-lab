from __future__ import annotations

from pathlib import Path
from typing import Protocol


class TTSBackend(Protocol):
    name: str

    def synthesize(self, text: str, out: Path, voice_profile: str) -> Path:
        ...


class ConfiguredTTS:
    def __init__(
        self,
        backend: TTSBackend,
        voice_profile: str,
        *,
        segmented: bool = True,
        max_chars: int = 900,
    ):
        self.backend = backend
        self.voice_profile = voice_profile
        self.segmented = segmented
        self.max_chars = max_chars
        self.name = getattr(backend, "name", backend.__class__.__name__.lower())

    def synthesize(self, text: str, out: Path) -> Path:
        out = Path(out)
        if not self.segmented:
            return self.backend.synthesize(text, out, self.voice_profile)
        from app.narration.assemble import render_narration

        track = render_narration(
            text,
            self.backend,
            self.voice_profile,
            out.parent,
            output_path=out,
            max_chars=self.max_chars,
        )
        return track.path


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
