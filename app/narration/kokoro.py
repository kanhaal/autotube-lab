from __future__ import annotations

from pathlib import Path


class KokoroTTS:
    name = "kokoro"

    def __init__(
        self,
        pipeline=None,
        lang_code: str = "a",
        writer=None,
        voice_profiles: dict[str, dict] | None = None,
    ):
        self._pipeline = pipeline
        self.lang_code = lang_code
        self.writer = writer
        self.voice_profiles = voice_profiles or {}

    def _load_pipeline(self):
        if self._pipeline is not None:
            return self._pipeline
        from kokoro import KPipeline

        self._pipeline = KPipeline(lang_code=self.lang_code)
        return self._pipeline

    @staticmethod
    def _default_writer(path: Path, chunks, sample_rate: int):
        import numpy as np
        import soundfile as sf

        arrays = []
        for chunk in chunks:
            if hasattr(chunk, "detach"):
                chunk = chunk.detach().cpu()
            if hasattr(chunk, "numpy"):
                chunk = chunk.numpy()
            arrays.append(np.asarray(chunk, dtype=np.float32).reshape(-1))
        audio = np.concatenate(arrays) if arrays else np.zeros(1, dtype=np.float32)
        sf.write(str(path), audio, sample_rate)

    def synthesize(self, text: str, out: Path, voice_profile: str) -> Path:
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        settings = dict(self.voice_profiles.get(voice_profile, {}))
        voice = settings.pop("voice", "af_heart")
        speed = float(settings.pop("speed", 1.0))
        pipeline = self._load_pipeline()
        chunks = []
        for result in pipeline(text, voice=voice, speed=speed):
            if isinstance(result, tuple):
                audio = result[2]
            else:
                audio = getattr(result, "audio", None)
            if audio is not None:
                chunks.append(audio)
        if not chunks:
            raise RuntimeError("Kokoro produced no audio")
        writer = self.writer or self._default_writer
        writer(out, chunks, 24000)
        return out
