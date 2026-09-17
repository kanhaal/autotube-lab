from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from app.narration.backend import ConfiguredTTS
from app.narration.assemble import render_narration


class _Backend:
    name = "fake"

    def synthesize(self, text: str, out: Path, voice_profile: str) -> Path:
        Path(out).write_bytes(text.encode("utf-8"))
        return Path(out)


def test_configured_tts_honors_requested_output_path(monkeypatch, tmp_path):
    seen = {}

    def fake_render(script, backend, voice_profile, out_dir, *, output_path=None, **kwargs):
        seen["output_path"] = output_path
        target = Path(output_path or Path(out_dir) / "narration.wav")
        target.write_bytes(b"audio")
        return SimpleNamespace(path=target)

    monkeypatch.setattr("app.narration.assemble.render_narration", fake_render)
    tts = ConfiguredTTS(_Backend(), "voice")
    requested = tmp_path / "short-narration.wav"

    actual = tts.synthesize("short script", requested)

    assert actual == requested
    assert seen["output_path"] == requested
    assert requested.is_file()


def test_render_narration_keeps_long_and_short_segment_workspaces_separate(tmp_path):
    backend = _Backend()

    def normalize(source: Path, dest: Path) -> Path:
        dest.write_bytes(source.read_bytes())
        return dest

    def duration_probe(path: Path) -> float:
        return 1.0

    def concatenate(paths: list[Path], out: Path) -> Path:
        out.write_bytes(b"|".join(path.read_bytes() for path in paths))
        return out

    long_out = tmp_path / "narration.wav"
    short_out = tmp_path / "short-narration.wav"

    long_track = render_narration(
        "Long narration.",
        backend,
        "voice",
        tmp_path,
        output_path=long_out,
        normalizer=normalize,
        duration_probe=duration_probe,
        concatenator=concatenate,
    )
    short_track = render_narration(
        "Short narration.",
        backend,
        "voice",
        tmp_path,
        output_path=short_out,
        normalizer=normalize,
        duration_probe=duration_probe,
        concatenator=concatenate,
    )

    assert long_track.path == long_out
    assert short_track.path == short_out
    assert long_track.path.read_bytes() == b"Long narration."
    assert short_track.path.read_bytes() == b"Short narration."
    assert long_track.segments[0].raw_path.parent != short_track.segments[0].raw_path.parent
