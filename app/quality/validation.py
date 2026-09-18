from __future__ import annotations

import json
import os
from pathlib import Path

from app.quality.models import QualityIssue, QualityReport
from app.rendering.ffmpeg import MediaProbe, probe_media

DURATION_TOLERANCE_SECONDS=1.0
DURATION_TOLERANCE_RATIO=0.015
MIN_MEDIA_FILE_SIZE_BYTES=1024
SHORT_MIN_SECONDS=30.0
SHORT_MAX_SECONDS=45.0

def _minimum_file_size() -> int:
    raw=os.getenv("AUTOTUBE_MIN_MEDIA_BYTES",str(MIN_MEDIA_FILE_SIZE_BYTES))
    try: return max(0,int(raw))
    except ValueError: return MIN_MEDIA_FILE_SIZE_BYTES

def _report(issues:list[QualityIssue])->QualityReport:
    frozen=tuple(issues); return QualityReport(ok=not any(issue.fatal for issue in frozen),issues=frozen)

def _existing_file(value:object)->Path|None:
    if not value: return None
    path=Path(value); return path if path.is_file() else None

def _probe_video(path:Path,issues:list[QualityIssue])->MediaProbe|None:
    try: return probe_media(path)
    except Exception as exc:
        issues.append(QualityIssue("unreadable_media",f"FFprobe failed for {path}: {exc}")); return None

def _validate_probe(probe:MediaProbe,*,expected_resolution:tuple[int,int],issues:list[QualityIssue])->None:
    if (probe.width,probe.height)!=expected_resolution:
        issues.append(QualityIssue("wrong_resolution",f"expected {expected_resolution[0]}x{expected_resolution[1]}, got {probe.width}x{probe.height}"))
    if not probe.video_codec: issues.append(QualityIssue("missing_video_stream","render has no video stream"))
    if not probe.audio_codec or probe.audio_duration<=0: issues.append(QualityIssue("missing_audio","render has no usable audio stream"))
    if probe.file_size<_minimum_file_size():
        issues.append(QualityIssue("file_too_small",f"render is {probe.file_size} bytes, below minimum {_minimum_file_size()} bytes"))

def _require_captions(package:object,issues:list[QualityIssue])->None:
    package_path=Path(package) if package else None; captions=package_path/"captions.json" if package_path else None
    if captions is None or not captions.is_file(): issues.append(QualityIssue("missing_captions","render package has no captions.json"))

def validate_effect_contracts(package:Path|str|None)->tuple[QualityIssue,...]:
    if not package: return ()
    path=Path(package)/"scenes.json"
    if not path.is_file(): return ()
    try: payload=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError): return (QualityIssue("effect_contract_unreadable","scenes.json could not be validated"),)
    issues=[]
    for scene in payload.get("scenes",[]):
        for effect in scene.get("effects",[]) or []:
            kind=effect.get("kind")
            if kind=="meme_flash":
                duration=float(effect.get("duration_seconds",1.0))
                if duration<0.5 or duration>1.5:
                    issues.append(QualityIssue("meme_flash_duration",f"meme_flash actual duration must be 0.5-1.5s; got {duration:.3f}s"))
            if kind=="stat_count_up":
                final=effect.get("final_value"); verified=effect.get("verified_value")
                if verified is None or final!=verified:
                    issues.append(QualityIssue("stat_count_up_unverified",f"stat_count_up final value {final!r} does not match verified value {verified!r}"))
    return tuple(issues)

def validate_longform(outputs,expected_duration:float,fact_ok:bool=True)->QualityReport:
    issues=[]
    video=_existing_file(getattr(outputs,"long_video",None))
    if video is None:
        issues.append(QualityIssue("missing_video","long-form video path is missing or invalid")); return _report(issues)
    probe=_probe_video(video,issues)
    if probe is not None:
        _validate_probe(probe,expected_resolution=(1920,1080),issues=issues)
        allowed=max(DURATION_TOLERANCE_SECONDS,abs(expected_duration)*DURATION_TOLERANCE_RATIO)
        actual=probe.format_duration or probe.video_duration
        if abs(actual-expected_duration)>allowed:
            issues.append(QualityIssue("duration_mismatch",f"expected about {expected_duration:.3f}s, got {actual:.3f}s (tolerance {allowed:.3f}s)"))
    package=getattr(outputs,"render_package",None); _require_captions(package,issues); issues.extend(validate_effect_contracts(package))
    thumbnails=tuple(getattr(outputs,"thumbnails",()) or ())
    if not any(_existing_file(path) is not None for path in thumbnails): issues.append(QualityIssue("missing_thumbnail","no rendered thumbnail artifact exists"))
    if not fact_ok: issues.append(QualityIssue("fact_gate_failed","verified-fact gate did not pass"))
    return _report(issues)

def validate_short(outputs)->QualityReport:
    issues=[]; video=_existing_file(getattr(outputs,"short_video",None))
    if video is None:
        issues.append(QualityIssue("missing_short_video","Short video path is missing or invalid")); return _report(issues)
    probe=_probe_video(video,issues)
    if probe is not None:
        _validate_probe(probe,expected_resolution=(1080,1920),issues=issues)
        duration=probe.format_duration or probe.video_duration
        if duration<SHORT_MIN_SECONDS or duration>SHORT_MAX_SECONDS:
            issues.append(QualityIssue("short_duration",f"Short duration must be {SHORT_MIN_SECONDS:.0f}-{SHORT_MAX_SECONDS:.0f}s; got {duration:.3f}s"))
    package=getattr(outputs,"short_render_package",None); _require_captions(package,issues); issues.extend(validate_effect_contracts(package))
    return _report(issues)
