from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class SfxEvent:
    path: Path
    start_ms: int = 0
    volume: float = 0.35


def build_audio_filter_graph(
    *,
    has_music: bool,
    sfx_count: int,
    target_lufs: float = -14.0,
    true_peak: float = -1.5,
    sfx_delays: tuple[int, ...] | None = None,
    sfx_volumes: tuple[float, ...] | None = None,
    lowpass_windows: tuple[tuple[int, int], ...] | None = None,
) -> str:
    loudnorm = f"loudnorm=I={target_lufs}:TP={true_peak}:LRA=11"
    parts: list[str] = []
    inputs = ["[0:a]"]
    next_index = 1

    if has_music:
        parts.append("[1:a]volume=0.18[bg]")
        parts.append(
            "[bg][0:a]sidechaincompress="
            "threshold=0.02:ratio=8:attack=20:release=250[ducked]"
        )
        inputs.append("[ducked]")
        next_index = 2

    delays = sfx_delays or tuple(0 for _ in range(sfx_count))
    volumes = sfx_volumes or tuple(0.35 for _ in range(sfx_count))
    for index in range(sfx_count):
        delay = delays[index] if index < len(delays) else 0
        volume = max(0.0, volumes[index] if index < len(volumes) else 0.35)
        parts.append(
            f"[{next_index + index}:a]adelay={delay}|{delay},volume={volume:g}[sfx{index}]"
        )
        inputs.append(f"[sfx{index}]")

    if len(inputs) > 1:
        parts.append(
            "".join(inputs)
            + f"amix=inputs={len(inputs)}:duration=first:dropout_transition=0[mix]"
        )
        current = "[mix]"
    else:
        current = "[0:a]"

    for index, window in enumerate(lowpass_windows or ()):
        start_ms = max(0, int(window[0]))
        duration_ms = max(1, int(window[1]))
        start = start_ms / 1000
        end = (start_ms + duration_ms) / 1000
        midpoint = start + (end - start) * 0.55
        label = f"lp{index}"
        # Two short enabled filters create a deliberate down-sweep before returning to full range.
        parts.append(
            f"{current}"
            f"lowpass=f=2600:enable='between(t,{start:.3f},{midpoint:.3f})',"
            f"lowpass=f=950:enable='between(t,{midpoint:.3f},{end:.3f})'"
            f"[{label}]"
        )
        current = f"[{label}]"

    parts.append(f"{current}{loudnorm}[out]")
    return ";".join(parts)


def mix_episode_audio(
    narration: Path,
    music: Path | None,
    sfx_events,
    out: Path,
    *,
    target_lufs: float = -14.0,
    true_peak: float = -1.5,
    lowpass_windows: tuple[tuple[int, int], ...] = (),
) -> Path:
    narration = Path(narration)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    events = tuple(sfx_events or ())

    command = ["ffmpeg", "-y", "-i", str(narration)]
    if music is not None:
        command += ["-stream_loop", "-1", "-i", str(music)]
    normalized_events: list[SfxEvent] = []
    for event in events:
        if isinstance(event, SfxEvent):
            normalized = event
        elif isinstance(event, dict):
            normalized = SfxEvent(
                path=Path(event["path"]),
                start_ms=int(event.get("start_ms", 0)),
                volume=float(event.get("volume", 0.35)),
            )
        else:
            normalized = SfxEvent(path=Path(event[0]), start_ms=int(event[1]))
        normalized_events.append(normalized)
        command += ["-i", str(normalized.path)]

    graph = build_audio_filter_graph(
        has_music=music is not None,
        sfx_count=len(normalized_events),
        target_lufs=target_lufs,
        true_peak=true_peak,
        sfx_delays=tuple(event.start_ms for event in normalized_events),
        sfx_volumes=tuple(event.volume for event in normalized_events),
        lowpass_windows=tuple(lowpass_windows),
    )
    command += ["-filter_complex", graph, "-map", "[out]"]
    if out.suffix.lower() == ".wav":
        command += ["-c:a", "pcm_s16le"]
    else:
        command += ["-c:a", "aac", "-b:a", "192k"]
    command += ["-ar", "48000"]
    command.append(str(out))
    subprocess.run(
        command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out
