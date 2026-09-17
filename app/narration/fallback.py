from __future__ import annotations

from pathlib import Path


class NarrationError(RuntimeError):
    pass


class FallbackTTS:
    def __init__(self, primary, fallback):
        self.primary = primary
        self.fallback = fallback
        self.name = f"{getattr(primary, 'name', 'primary')}->{getattr(fallback, 'name', 'fallback')}"

    def synthesize(self, text: str, out: Path, voice_profile: str) -> Path:
        try:
            return self.primary.synthesize(text, out, voice_profile)
        except Exception as primary_exc:  # noqa: BLE001 - backend boundary must fail over
            try:
                return self.fallback.synthesize(text, out, voice_profile)
            except Exception as fallback_exc:  # noqa: BLE001 - preserve both backend failures
                primary_name = getattr(self.primary, "name", self.primary.__class__.__name__)
                fallback_name = getattr(self.fallback, "name", self.fallback.__class__.__name__)
                raise NarrationError(
                    f"TTS failed for {primary_name} ({primary_exc}) and "
                    f"{fallback_name} ({fallback_exc})"
                ) from fallback_exc

    def release(self) -> None:
        for backend in (self.primary, self.fallback):
            release = getattr(backend, "release", None)
            if callable(release):
                release()
