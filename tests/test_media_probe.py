from __future__ import annotations

import subprocess
from pathlib import Path


def _make_synthetic_mp4(path: Path) -> Path:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=320x180:r=30:d=1",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=48000:duration=1",
            "-shortest",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return path


def test_probe_media_reports_complete_video_and_audio_metadata(tmp_path: Path):
    from app.rendering.ffmpeg import probe_media

    video = _make_synthetic_mp4(tmp_path / "probe.mp4")
    probe = probe_media(video)

    assert probe.video_codec == "h264"
    assert probe.audio_codec == "aac"
    assert probe.width == 320
    assert probe.height == 180
    assert abs(probe.frame_rate - 30.0) < 0.01
    assert 0.9 <= probe.format_duration <= 1.1
    assert 0.9 <= probe.video_duration <= 1.1
    assert 0.9 <= probe.audio_duration <= 1.1
    assert probe.file_size == video.stat().st_size


def test_probe_video_delegates_to_complete_probe(tmp_path: Path):
    from app.rendering.ffmpeg import probe_video

    video = _make_synthetic_mp4(tmp_path / "compat.mp4")
    legacy = probe_video(video)

    assert legacy["width"] == 320
    assert legacy["height"] == 180
    assert 0.9 <= legacy["duration"] <= 1.1
