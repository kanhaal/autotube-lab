from __future__ import annotations

from pathlib import Path


class ChatterboxTTS:
    name = "chatterbox"

    def __init__(
        self,
        model=None,
        device: str | None = None,
        writer=None,
        voice_profiles: dict[str, dict] | None = None,
        reference_audio: Path | None = None,
    ):
        self._model = model
        self.device = device
        self.writer = writer
        self.voice_profiles = voice_profiles or {}
        self.reference_audio = Path(reference_audio) if reference_audio else None

    def _load_model(self):
        if self._model is not None:
            return self._model
        import torch
        from chatterbox.tts import ChatterboxTTS as Model

        device = self.device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._model = Model.from_pretrained(device=device)
        return self._model

    @staticmethod
    def _default_writer(path: Path, wav, sample_rate: int):
        import torch
        import torchaudio as ta

        tensor = wav if hasattr(wav, "dim") else torch.as_tensor(wav, dtype=torch.float32)
        if tensor.dim() == 1:
            tensor = tensor.unsqueeze(0)
        ta.save(str(path), tensor.detach().cpu(), sample_rate)

    def synthesize(self, text: str, out: Path, voice_profile: str) -> Path:
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        model = self._load_model()
        settings = dict(self.voice_profiles.get(voice_profile, {}))
        settings.pop("audio_prompt_path", None)
        if self.reference_audio is not None:
            if not self.reference_audio.exists():
                raise FileNotFoundError(self.reference_audio)
            settings["audio_prompt_path"] = str(self.reference_audio)
        wav = model.generate(text, **settings)
        writer = self.writer or self._default_writer
        writer(out, wav, int(model.sr))
        return out
