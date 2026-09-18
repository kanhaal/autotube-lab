from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from app.narration.models import NarrationSegment, NarrationTrack
from app.narration.segment import segment_script


def _normalize_wav(source: Path, dest: Path) -> Path:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-ar",
            "48000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(dest),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return dest


def _probe_duration(path: Path) -> float:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(json.loads(proc.stdout)["format"]["duration"])


def _concat_wavs(paths: list[Path], out: Path) -> Path:
    if not paths:
        raise ValueError("No narration segments to concatenate")
    if len(paths) == 1:
        shutil.copyfile(paths[0], out)
        return out
    concat_file = out.with_suffix(".concat.txt")
    lines = []
    for path in paths:
        escaped = str(path.resolve()).replace("'", "'\\''")
        lines.append(f"file '{escaped}'")
    concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c:a",
                "pcm_s16le",
                str(out),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    finally:
        concat_file.unlink(missing_ok=True)
    return out


def render_narration(
    script: str,
    backend,
    voice_profile: str,
    out_dir: Path,
    *,
    output_path: Path | None = None,
    max_chars: int = 280,
    normalizer=_normalize_wav,
    duration_probe=_probe_duration,
    concatenator=_concat_wavs,
) -> NarrationTrack:
    out_dir = Path(out_dir)
    final_path = Path(output_path) if output_path is not None else out_dir / "narration.wav"
    final_path.parent.mkdir(parents=True, exist_ok=True)
    segment_dir = out_dir / f"{final_path.stem}-segments"
    segment_dir.mkdir(parents=True, exist_ok=True)
    text_segments = segment_script(script, max_chars=max_chars)
    if not text_segments:
        raise ValueError("Narration script is empty")

    records: list[NarrationSegment] = []
    normalized_paths: list[Path] = []
    backend_name = getattr(backend, "name", backend.__class__.__name__.lower())
    for index, text in enumerate(text_segments, start=1):
        raw = segment_dir / f"segment-{index:03d}-raw.wav"
        normalized = segment_dir / f"segment-{index:03d}.wav"
        backend.synthesize(text, raw, voice_profile)
        normalizer(raw, normalized)
        duration = float(duration_probe(normalized))
        records.append(
            NarrationSegment(
                text=text,
                raw_path=raw,
                normalized_path=normalized,
                duration=duration,
                backend=backend_name,
                voice_profile=voice_profile,
            )
        )
        normalized_paths.append(normalized)

    concatenator(normalized_paths, final_path)
    return NarrationTrack(final_path, tuple(records), sum(record.duration for record in records))
