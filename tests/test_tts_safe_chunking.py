from __future__ import annotations

from pathlib import Path

from app.narration.assemble import render_narration
from app.narration.backend import ConfiguredTTS


class _Backend:
    name = "fake"

    def __init__(self) -> None:
        self.texts: list[str] = []

    def synthesize(self, text: str, out: Path, voice_profile: str) -> Path:
        self.texts.append(text)
        Path(out).write_bytes(text.encode("utf-8"))
        return Path(out)


def _normalize(source: Path, dest: Path) -> Path:
    dest.write_bytes(source.read_bytes())
    return dest


def _duration_probe(path: Path) -> float:
    return 1.0


def _concat(paths: list[Path], out: Path) -> Path:
    out.write_bytes(b"|".join(path.read_bytes() for path in paths))
    return out


def test_configured_tts_defaults_to_chatterbox_safe_chunk_size():
    tts = ConfiguredTTS(_Backend(), "voice")

    assert tts.max_chars == 280


def test_render_narration_default_never_sends_more_than_280_chars_to_backend(tmp_path):
    backend = _Backend()
    script = (
        "This local benchmark note is synthetic and exists only to exercise the verified source layout. "
        "The fictional queue latency drops from forty two milliseconds to eighteen. "
        "A generated chart shows the made up latency trend moving downward across four test passes. "
        "The synthetic timeline moves from baseline to scheduler change to validation and final pass. "
        "The comparison keeps the distinction simple: a slower fictional baseline and a faster fictional tuned state. "
        "Finally the editorial fallback proves the renderer still has a safe visual when no verified image is available."
    )

    track = render_narration(
        script,
        backend,
        "voice",
        tmp_path,
        normalizer=_normalize,
        duration_probe=_duration_probe,
        concatenator=_concat,
    )

    assert len(track.segments) == 3
    assert [len(segment.text) for segment in track.segments] == [260, 201, 111]
    assert all(len(text) <= 280 for text in backend.texts)
