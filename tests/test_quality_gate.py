from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import json

import pytest

from app.rendering.ffmpeg import MediaProbe


def _probe(
    *,
    width: int = 1920,
    height: int = 1080,
    duration: float = 60.0,
    audio: str | None = "aac",
    file_size: int = 1_000_000,
) -> MediaProbe:
    return MediaProbe(
        video_codec="h264",
        audio_codec=audio,
        width=width,
        height=height,
        frame_rate=30.0,
        format_duration=duration,
        video_duration=duration,
        audio_duration=duration if audio else 0.0,
        file_size=file_size,
    )


def _outputs(tmp_path: Path, *, thumbnails: int = 1, captions: bool = True):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")
    package = tmp_path / "render-package-long"
    package.mkdir()
    if captions:
        (package / "captions.json").write_text('{"schema_version":"1","cues":[]}', encoding="utf-8")
    thumbs = []
    for index in range(thumbnails):
        thumb = tmp_path / f"thumb-{index}.png"
        thumb.write_bytes(b"png")
        thumbs.append(thumb)
    return SimpleNamespace(
        long_video=video,
        short_video=None,
        thumbnails=tuple(thumbs),
        render_package=package,
        short_render_package=None,
    )


def _codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


def test_valid_longform_passes_hard_gate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from app.quality import validation

    outputs = _outputs(tmp_path)
    monkeypatch.setattr(validation, "probe_media", lambda path: _probe())

    report = validation.validate_longform(outputs, expected_duration=60.0)

    assert report.ok is True
    assert report.issues == ()


@pytest.mark.parametrize(
    ("probe", "expected_code"),
    [
        (_probe(width=1280, height=720), "wrong_resolution"),
        (_probe(audio=None), "missing_audio"),
        (_probe(duration=54.0), "duration_mismatch"),
        (_probe(file_size=100), "file_too_small"),
    ],
)
def test_longform_media_failures_are_fatal(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    probe: MediaProbe,
    expected_code: str,
):
    from app.quality import validation

    outputs = _outputs(tmp_path)
    monkeypatch.setattr(validation, "probe_media", lambda path: probe)

    report = validation.validate_longform(outputs, expected_duration=60.0)

    assert report.ok is False
    assert expected_code in _codes(report)
    assert all(issue.fatal for issue in report.issues)


def test_longform_requires_caption_artifact(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from app.quality import validation

    outputs = _outputs(tmp_path, captions=False)
    monkeypatch.setattr(validation, "probe_media", lambda path: _probe())

    report = validation.validate_longform(outputs, expected_duration=60.0)

    assert report.ok is False
    assert "missing_captions" in _codes(report)


def test_longform_requires_thumbnail(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from app.quality import validation

    outputs = _outputs(tmp_path, thumbnails=0)
    monkeypatch.setattr(validation, "probe_media", lambda path: _probe())

    report = validation.validate_longform(outputs, expected_duration=60.0)

    assert report.ok is False
    assert "missing_thumbnail" in _codes(report)


def test_longform_hard_fails_fact_gate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from app.quality import validation

    outputs = _outputs(tmp_path)
    monkeypatch.setattr(validation, "probe_media", lambda path: _probe())

    report = validation.validate_longform(outputs, expected_duration=60.0, fact_ok=False)

    assert report.ok is False
    assert "fact_gate_failed" in _codes(report)


def test_longform_hard_fails_missing_video_path(tmp_path: Path):
    from app.quality.validation import validate_longform

    outputs = _outputs(tmp_path)
    outputs.long_video.unlink()

    report = validate_longform(outputs, expected_duration=60.0)

    assert report.ok is False
    assert "missing_video" in _codes(report)


def test_valid_short_passes_and_enforces_native_vertical_duration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    from app.quality import validation

    outputs = _outputs(tmp_path)
    short = tmp_path / "short.mp4"
    short.write_bytes(b"video")
    short_package = tmp_path / "render-package-short"
    short_package.mkdir()
    (short_package / "captions.json").write_text('{"schema_version":"1","cues":[]}', encoding="utf-8")
    outputs.short_video = short
    outputs.short_render_package = short_package

    monkeypatch.setattr(
        validation,
        "probe_media",
        lambda path: _probe(width=1080, height=1920, duration=36.0),
    )
    assert validation.validate_short(outputs).ok is True

    monkeypatch.setattr(
        validation,
        "probe_media",
        lambda path: _probe(width=1920, height=1080, duration=20.0),
    )
    report = validation.validate_short(outputs)
    assert report.ok is False
    assert {"wrong_resolution", "short_duration"} <= _codes(report)


def _write_effect_scenes(package: Path, *, effects: list[dict], data: dict | None = None) -> None:
    payload = {
        "schema_version": "1",
        "channel_id": "kernelrush",
        "format": "longform",
        "scenes": [
            {
                "id": "scene-1",
                "narration": "Verified metric.",
                "purpose": "evidence",
                "scene_type": "stat",
                "headline": "VERIFIED",
                "subheadline": "",
                "source_ids": [],
                "asset_ids": [],
                "motion": "none",
                "emphasis": [],
                "transition": "cut",
                "fallback_scene_type": "fallback_editorial",
                "data": data or {},
                "effects": effects,
                "transition_out": None,
            }
        ],
    }
    (package / "scenes.json").write_text(json.dumps(payload), encoding="utf-8")


def test_v35_qa_rejects_meme_flash_request_over_hard_cap(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    from app.quality import validation

    outputs = _outputs(tmp_path)
    _write_effect_scenes(
        outputs.render_package,
        effects=[{"kind": "meme_flash", "duration_seconds": 2.0}],
    )
    monkeypatch.setattr(validation, "probe_media", lambda path: _probe())

    report = validation.validate_longform(outputs, expected_duration=60.0)

    assert report.ok is False
    assert "meme_flash_duration" in _codes(report)


def test_v35_qa_rejects_stat_count_up_that_does_not_match_verified_scene_value(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    from app.quality import validation

    outputs = _outputs(tmp_path)
    _write_effect_scenes(
        outputs.render_package,
        data={"value": 42000},
        effects=[{"kind": "stat_count_up", "verified_value": 41000}],
    )
    monkeypatch.setattr(validation, "probe_media", lambda path: _probe())

    report = validation.validate_longform(outputs, expected_duration=60.0)

    assert report.ok is False
    assert "stat_count_up_value_mismatch" in _codes(report)


def test_v35_qa_accepts_valid_effect_contracts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    from app.quality import validation

    outputs = _outputs(tmp_path)
    _write_effect_scenes(
        outputs.render_package,
        data={"value": 42000},
        effects=[
            {"kind": "meme_flash", "duration_seconds": 1.0},
            {"kind": "stat_count_up", "verified_value": 42000},
        ],
    )
    monkeypatch.setattr(validation, "probe_media", lambda path: _probe())

    report = validation.validate_longform(outputs, expected_duration=60.0)

    assert report.ok is True
