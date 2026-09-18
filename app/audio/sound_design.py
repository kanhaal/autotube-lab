from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path

from app.audio.mix import SfxEvent

_SAMPLE_RATE = 48000
_DURATIONS = {
    "whoosh": 0.34,
    "impact": 0.26,
    "click": 0.08,
    "riser": 0.82,
    "braam": 0.72,
    "ding": 0.48,
    "glitch": 0.20,
    "static": 0.28,
}
_DEFAULT_VOLUMES = {
    "kernelrush": {
        "whoosh": 0.13,
        "impact": 0.10,
        "click": 0.09,
        "riser": 0.09,
        "braam": 0.08,
        "ding": 0.10,
        "glitch": 0.07,
        "static": 0.05,
    },
    "lobbysignal": {
        "whoosh": 0.17,
        "impact": 0.14,
        "click": 0.10,
        "riser": 0.12,
        "braam": 0.11,
        "ding": 0.12,
        "glitch": 0.12,
        "static": 0.08,
    },
}
_TRANSITION_CUES = {
    "whoosh_zoom": "whoosh",
    "whip_pan": "whoosh",
    "glitch_rgb_split": "glitch",
    "liquid_displacement": "glitch",
    "smash_cut": "impact",
    "match_cut": "click",
}
_EFFECT_CUES = {
    "stat_count_up": "ding",
    "particle_burst": "impact",
    "icon_morph": "click",
}


def _clamp_sample(value: float) -> int:
    return int(max(-1.0, min(1.0, value)) * 32767)


def _envelope(index: int, count: int, attack: float = 0.08, release: float = 0.62) -> float:
    if count <= 1:
        return 0.0
    p = index / (count - 1)
    attack_gain = min(1.0, p / max(0.001, attack))
    release_start = max(attack, release)
    if p <= release_start:
        release_gain = 1.0
    else:
        release_gain = max(0.0, 1.0 - (p - release_start) / max(0.001, 1.0 - release_start))
    return attack_gain * release_gain


def _sample(kind: str, index: int, count: int, rng: random.Random) -> float:
    t = index / _SAMPLE_RATE
    p = index / max(1, count - 1)
    env = _envelope(index, count)

    if kind == "whoosh":
        noise = rng.uniform(-1.0, 1.0)
        sweep = math.sin(2 * math.pi * (180 + 900 * p * p) * t)
        return (noise * 0.28 + sweep * 0.14) * math.sin(math.pi * p) * 0.9
    if kind == "impact":
        low = math.sin(2 * math.pi * (78 - 28 * p) * t)
        click = rng.uniform(-1.0, 1.0) * math.exp(-p * 34)
        return (low * 0.82 + click * 0.42) * math.exp(-p * 5.4) * 0.92
    if kind == "click":
        tone = math.sin(2 * math.pi * 1900 * t) + 0.45 * math.sin(2 * math.pi * 3100 * t)
        return tone * math.exp(-p * 12) * 0.42
    if kind == "riser":
        frequency = 150 + 1900 * p * p
        tone = math.sin(2 * math.pi * frequency * t)
        noise = rng.uniform(-1.0, 1.0) * 0.12
        return (tone * 0.32 + noise) * (p**1.45) * 0.8
    if kind == "braam":
        low = math.sin(2 * math.pi * 52 * t)
        mid = math.sin(2 * math.pi * 79 * t + 0.8)
        upper = math.sin(2 * math.pi * 111 * t + 1.7)
        return (low * 0.55 + mid * 0.28 + upper * 0.17) * env * 0.78
    if kind == "ding":
        tone = math.sin(2 * math.pi * 880 * t) + 0.42 * math.sin(2 * math.pi * 1320 * t)
        return tone * math.exp(-p * 4.8) * 0.48
    if kind == "glitch":
        gate = 1.0 if int(p * 18) % 3 != 1 else 0.12
        noise = rng.uniform(-1.0, 1.0)
        carrier = math.sin(2 * math.pi * (280 + (index % 97) * 9) * t)
        return (noise * 0.42 + carrier * 0.18) * gate * math.sin(math.pi * p) * 0.84
    if kind == "static":
        noise = rng.uniform(-1.0, 1.0)
        gate = 0.45 + 0.55 * (1.0 if int(p * 12) % 2 == 0 else 0.35)
        return noise * gate * env * 0.38
    return 0.0


def synthesize_edit_sfx(kind: str, out_dir: Path) -> Path:
    if kind not in _DURATIONS:
        raise ValueError(f"unsupported sound-design cue: {kind}")
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"v4-{kind}.wav"
    if path.is_file():
        return path

    count = max(1, int(_DURATIONS[kind] * _SAMPLE_RATE))
    rng = random.Random(f"autotube-v4:{kind}")
    frames = bytearray()
    for index in range(count):
        frames.extend(struct.pack("<h", _clamp_sample(_sample(kind, index, count, rng))))

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(_SAMPLE_RATE)
        wav.writeframes(bytes(frames))
    return path


def _scene_windows(scene_plan, duration_seconds: float) -> list[tuple[float, float]]:
    scenes = tuple(scene_plan.scenes)
    if not scenes:
        return []
    weights = [max(1, len(scene.narration.split())) for scene in scenes]
    total = max(1, sum(weights))
    cursor = 0.0
    windows: list[tuple[float, float]] = []
    for weight in weights:
        start = cursor
        cursor += duration_seconds * (weight / total)
        windows.append((start, min(duration_seconds, cursor)))
    if windows:
        windows[-1] = (windows[-1][0], duration_seconds)
    return windows


def _volume(channel_id: str, kind: str, requested: object = None) -> float:
    defaults = _DEFAULT_VOLUMES.get(channel_id, _DEFAULT_VOLUMES["kernelrush"])
    if requested is None:
        return defaults.get(kind, 0.1)
    try:
        return max(0.0, min(0.35, float(requested)))
    except (TypeError, ValueError):
        return defaults.get(kind, 0.1)


def build_sound_design_events(
    scene_plan,
    *,
    duration_seconds: float,
    out_dir: Path,
    channel_id: str,
) -> tuple[SfxEvent, ...]:
    duration = max(0.001, float(duration_seconds))
    windows = _scene_windows(scene_plan, duration)
    requested: list[tuple[int, str, float]] = []

    for scene, (start, end) in zip(scene_plan.scenes, windows):
        scene_duration = max(0.001, end - start)
        for cue in scene.audio_cues:
            kind = str(cue.get("kind", "")).strip()
            if kind not in _DURATIONS:
                continue
            local = max(0.0, min(scene_duration, float(cue.get("at", 0.0))))
            requested.append(
                (
                    int(round((start + local) * 1000)),
                    kind,
                    _volume(channel_id, kind, cue.get("volume")),
                )
            )

        transition_kind = _TRANSITION_CUES.get(scene.transition_out or "")
        if transition_kind:
            requested.append(
                (
                    int(round(max(start, end - 0.16) * 1000)),
                    transition_kind,
                    _volume(channel_id, transition_kind),
                )
            )

        effect_kinds = {str(effect.get("kind", "")) for effect in scene.effects}
        for effect_kind, sound_kind in _EFFECT_CUES.items():
            if effect_kind in effect_kinds:
                moment = start + min(scene_duration * 0.38, 0.9)
                requested.append(
                    (
                        int(round(moment * 1000)),
                        sound_kind,
                        _volume(channel_id, sound_kind),
                    )
                )

    requested.sort(key=lambda item: (item[0], item[1]))
    deduped: list[tuple[int, str, float]] = []
    for item in requested:
        if deduped and item[1] == deduped[-1][1] and abs(item[0] - deduped[-1][0]) < 140:
            continue
        deduped.append(item)

    max_events = 18 if getattr(scene_plan, "format", "longform") == "short" else 32
    events = tuple(
        SfxEvent(
            path=synthesize_edit_sfx(kind, out_dir),
            start_ms=max(0, start_ms),
            volume=volume,
        )
        for start_ms, kind, volume in deduped[:max_events]
    )
    return events
