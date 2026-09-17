from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MediaProbe:
    video_codec: str | None
    audio_codec: str | None
    width: int | None
    height: int | None
    frame_rate: float
    format_duration: float
    video_duration: float
    audio_duration: float
    file_size: int


def _as_float(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _frame_rate(stream: dict) -> float:
    value = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1"
    if isinstance(value, str) and "/" in value:
        numerator, denominator = value.split("/", 1)
        den = _as_float(denominator)
        return _as_float(numerator) / den if den else 0.0
    return _as_float(value)


def build_color_video(out: Path, seconds: int, title: str = "AUTOTUBE") -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    filt = (
        f"drawtext=text='{title.replace(':', ' ')}':fontcolor=white:fontsize=72:"
        "x=(w-text_w)/2:y=(h-text_h)/2"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x0A0D12:s=1920x1080:d={seconds}",
            "-vf",
            filt,
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(out),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out


def probe_media(path: Path) -> MediaProbe:
    target = Path(path)
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            (
                "stream=codec_type,codec_name,width,height,avg_frame_rate,"
                "r_frame_rate,duration:format=duration,size"
            ),
            "-of",
            "json",
            str(target),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    streams = payload.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), {})
    format_info = payload.get("format", {})
    format_duration = _as_float(format_info.get("duration"))

    return MediaProbe(
        video_codec=video.get("codec_name"),
        audio_codec=audio.get("codec_name"),
        width=int(video["width"]) if video.get("width") is not None else None,
        height=int(video["height"]) if video.get("height") is not None else None,
        frame_rate=_frame_rate(video),
        format_duration=format_duration,
        video_duration=(_as_float(video.get("duration")) or format_duration) if video else 0.0,
        audio_duration=(_as_float(audio.get("duration")) or format_duration) if audio else 0.0,
        file_size=int(format_info.get("size") or target.stat().st_size),
    )


def probe_video(path: Path) -> dict:
    media = probe_media(path)
    return {
        "width": media.width,
        "height": media.height,
        "duration": media.video_duration or media.format_duration,
    }
