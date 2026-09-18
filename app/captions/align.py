from __future__ import annotations

import gc
import os
import re
from difflib import SequenceMatcher
from pathlib import Path

from app.captions.models import CaptionCue, CaptionWord


class CaptionAlignmentError(RuntimeError):
    pass


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]+", " ", text.lower())).strip()


def _similarity(expected: str, actual: str) -> float:
    return SequenceMatcher(\n        None,\n        _normalize_text(expected),\n        _normalize_text(actual),\n        autojunk=False,\n    ).ratio()


def _cuda_runtime_library_error(exc: RuntimeError) -> bool:
    message = str(exc).lower()
    library = any(marker in message for marker in ("cublas", "cudnn", "cuda"))
    unavailable = any(
        marker in message
        for marker in (
            "not found",
            "cannot be loaded",
            "could not locate",
            "unable to load",
        )
    )
    return library and unavailable


class FasterWhisperTranscriber:
    def __init__(
        self,
        model_size: str | None = None,
        *,
        device: str | None = None,
        compute_type: str | None = None,
        model=None,
    ):
        self.model_size = model_size or os.getenv("AUTOTUBE_CAPTION_MODEL", "small.en")
        self.device = device or os.getenv("AUTOTUBE_CAPTION_DEVICE", "cuda")
        self.compute_type = compute_type or os.getenv(
            "AUTOTUBE_CAPTION_COMPUTE_TYPE",
            "float16",
        )
        self.allow_cpu_fallback = os.getenv(
            "AUTOTUBE_CAPTION_CPU_FALLBACK",
            "1",
        ).strip().lower() not in {"0", "false", "no"}
        self.fallback_reason: str | None = None
        self._model = model

    def _load_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model

    def _transcribe_once(self, path, *, word_timestamps: bool, vad_filter: bool):
        return self._load_model().transcribe(
            str(path),
            word_timestamps=word_timestamps,
            vad_filter=vad_filter,
            condition_on_previous_text=False,
        )

    def _fallback_to_cpu(self, exc: RuntimeError) -> bool:
        if (
            not self.allow_cpu_fallback
            or not self.device.lower().startswith("cuda")
            or not _cuda_runtime_library_error(exc)
        ):
            return False

        self.fallback_reason = str(exc)
        self.release()
        self.device = "cpu"
        self.compute_type = os.getenv("AUTOTUBE_CAPTION_CPU_COMPUTE_TYPE", "int8")
        return True

    def transcribe(self, path, word_timestamps=True, vad_filter=True):
        try:
            segments, info = self._transcribe_once(
                path,
                word_timestamps=word_timestamps,
                vad_filter=vad_filter,
            )
        except RuntimeError as exc:
            if not self._fallback_to_cpu(exc):
                raise
            return self._transcribe_once(
                path,
                word_timestamps=word_timestamps,
                vad_filter=vad_filter,
            )

        def guarded_segments():
            try:
                buffered = list(segments)
            except RuntimeError as exc:
                if not self._fallback_to_cpu(exc):
                    raise
                retry_segments, _ = self._transcribe_once(
                    path,
                    word_timestamps=word_timestamps,
                    vad_filter=vad_filter,
                )
                buffered = list(retry_segments)
            yield from buffered

        return guarded_segments(), info

    def release(self) -> None:
        self._model = None
        gc.collect()


def _to_cues(words) -> tuple[CaptionCue, ...]:
    cues: list[CaptionCue] = []
    current: list[CaptionWord] = []
    start = None
    end = None
    for word in words:
        text = str(word.word).strip()
        if not text:
            continue
        timing = CaptionWord(text=text, start=float(word.start), end=float(word.end))
        if start is None:
            start = timing.start
        end = timing.end
        current.append(timing)
        punctuation_break = text.endswith((".", "?", "!", ";", ":")) and len(current) >= 2
        if len(current) >= 7 or punctuation_break:
            cues.append(
                CaptionCue(
                    start,
                    end,
                    " ".join(item.text for item in current),
                    tuple(item.text for item in current),
                    tuple(current),
                )
            )
            current = []
            start = None
            end = None
    if current and start is not None and end is not None:
        cues.append(
            CaptionCue(
                start,
                end,
                " ".join(item.text for item in current),
                tuple(item.text for item in current),
                tuple(current),
            )
        )
    return tuple(cues)


def align_narration(
    audio: Path,
    script: str,
    transcriber,
    *,
    similarity_threshold: float = 0.82,
) -> tuple[CaptionCue, ...]:
    segments_iter, _ = transcriber.transcribe(str(audio), word_timestamps=True)
    segments = list(segments_iter)
    recognized = " ".join(str(segment.text).strip() for segment in segments if segment.text)
    score = _similarity(script, recognized)
    if score < similarity_threshold:
        raise CaptionAlignmentError(
            f"Caption recognition mismatch: similarity {score:.3f} < {similarity_threshold:.3f}"
        )
    words = []
    for segment in segments:
        if getattr(segment, "words", None):
            words.extend(segment.words)
    if not words:
        raise CaptionAlignmentError("Transcriber returned no word timestamps")
    return _to_cues(words)
