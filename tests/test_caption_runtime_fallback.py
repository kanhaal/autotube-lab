from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.captions.align import FasterWhisperTranscriber


class _FakeModel:
    def __init__(self, *, error: Exception | None = None) -> None:
        self.error = error
        self.calls = 0

    def transcribe(self, *args, **kwargs):
        self.calls += 1

        def segments():
            if self.error is not None:
                raise self.error
            yield SimpleNamespace(text="caption ok", words=[])

        return segments(), SimpleNamespace(language="en")


def test_faster_whisper_retries_missing_cuda_runtime_on_cpu(monkeypatch):
    cuda_model = _FakeModel(
        error=RuntimeError("Library cublas64_12.dll is not found or cannot be loaded")
    )
    cpu_model = _FakeModel()
    transcriber = FasterWhisperTranscriber(
        model_size="small.en",
        device="cuda",
        compute_type="float16",
    )

    monkeypatch.setattr(
        transcriber,
        "_load_model",
        lambda: cuda_model if transcriber.device == "cuda" else cpu_model,
    )

    segments, _ = transcriber.transcribe(Path("narration.wav"), word_timestamps=True)

    assert [segment.text for segment in segments] == ["caption ok"]
    assert cuda_model.calls == 1
    assert cpu_model.calls == 1
    assert transcriber.device == "cpu"
    assert transcriber.compute_type == "int8"
    assert "cublas64_12.dll" in transcriber.fallback_reason


def test_faster_whisper_does_not_hide_unrelated_runtime_error(monkeypatch):
    broken_model = _FakeModel(error=RuntimeError("decoder exploded"))
    transcriber = FasterWhisperTranscriber(
        model_size="small.en",
        device="cuda",
        compute_type="float16",
    )
    monkeypatch.setattr(transcriber, "_load_model", lambda: broken_model)

    segments, _ = transcriber.transcribe(Path("narration.wav"), word_timestamps=True)

    with pytest.raises(RuntimeError, match="decoder exploded"):
        list(segments)
