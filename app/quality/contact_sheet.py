from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

from app.rendering.ffmpeg import probe_media


def _sample_timestamps(duration: float, count: int) -> tuple[float, ...]:
    if count <= 0:
        raise ValueError("sample_count must be positive")
    if duration <= 0:
        raise ValueError("video duration must be positive")
    step = duration / count
    return tuple((index + 0.5) * step for index in range(count))


def build_contact_sheet(video: Path, out: Path, sample_count: int = 12) -> Path:
    source = Path(video)
    destination = Path(out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    probe = probe_media(source)
    duration = probe.format_duration or probe.video_duration
    timestamps = _sample_timestamps(duration, sample_count)

    frames: list[Image.Image] = []
    with tempfile.TemporaryDirectory(prefix="autotube-contact-") as temp:
        temp_dir = Path(temp)
        for index, timestamp in enumerate(timestamps):
            frame = temp_dir / f"frame-{index:03d}.jpg"
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-ss",
                    f"{timestamp:.6f}",
                    "-i",
                    str(source),
                    "-frames:v",
                    "1",
                    "-vf",
                    "scale=480:-2",
                    str(frame),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            with Image.open(frame) as image:
                frames.append(image.convert("RGB").copy())

    columns = min(4, sample_count)
    rows = math.ceil(sample_count / columns)
    tile_width = max(image.width for image in frames)
    tile_height = max(image.height for image in frames)
    sheet = Image.new("RGB", (tile_width * columns, tile_height * rows), "black")
    for index, frame in enumerate(frames):
        tile = ImageOps.pad(frame, (tile_width, tile_height), color="black")
        x = (index % columns) * tile_width
        y = (index // columns) * tile_height
        sheet.paste(tile, (x, y))
    sheet.save(destination, quality=90)
    return destination
