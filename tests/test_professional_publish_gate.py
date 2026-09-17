from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from app.domain.models import StoryCandidate
from app.orchestration.production import ProductionResult
from app.quality.models import QualityReport
from app.storage.sqlite import Repository


def _candidate_and_packet():
    now = datetime.now(timezone.utc)
    candidate = StoryCandidate(
        "alpha",
        "ai_software",
        "Alpha launch",
        "https://primary.example/alpha",
        "Primary",
        "rss",
        now,
        now,
        ("Alpha",),
        "Alpha released a local developer tool.",
        {},
        0.9,
        "official source",
    )
    packet = {
        "topic": "Alpha launch",
        "candidate": {"title": candidate.title, "summary": candidate.summary},
        "sources": [
            {
                "source_name": "Primary",
                "url": "https://primary.example/alpha",
                "text": "Alpha released a local developer tool.",
            },
            {
                "source_name": "Secondary",
                "url": "https://secondary.example/alpha",
                "text": "Alpha released the tool for local execution.",
            },
        ],
    }
    return candidate, packet


def _valid_production(tmp_path: Path) -> ProductionResult:
    video = tmp_path / "video.mp4"
    thumb = tmp_path / "thumbnail.png"
    video.write_bytes(b"video")
    thumb.write_bytes(b"png")
    return ProductionResult(
        state={
            "long_video": video,
            "thumbnails": (thumb,),
            "script": "Alpha released a local developer tool.",
        },
        quality_report=QualityReport(ok=True, issues=()),
    )


def _patch_story(monkeypatch, candidate, packet, production):
    monkeypatch.setattr("app.orchestration.daily.collect_for_niche", lambda niche: [candidate])
    monkeypatch.setattr("app.orchestration.daily.research_candidate", lambda item: packet)
    monkeypatch.setattr(
        "app.orchestration.production.produce_professional_episode",
        lambda **kwargs: production,
    )


def test_unapproved_professional_output_never_reaches_publisher(monkeypatch, tmp_path: Path):
    from app.orchestration.daily import run_channel

    candidate, packet = _candidate_and_packet()
    production = _valid_production(tmp_path)
    _patch_story(monkeypatch, candidate, packet, production)

    class Publisher:
        def stage(self, *args, **kwargs):
            raise AssertionError("unapproved professional renderer must not publish")

        def stage_and_schedule(self, *args, **kwargs):
            raise AssertionError("unapproved professional renderer must not publish")

    repo = Repository(tmp_path / "state.db")
    repo.init()
    result = run_channel(
        "kernelrush",
        repo,
        day_index=0,
        output_dir=tmp_path / "output",
        dry_run=False,
        tts=object(),
        publisher=Publisher(),
        renderer="professional",
    )

    assert result["status"] == "blocked_publish"
    assert result["publish_blocked"] == "renderer_unapproved"


def test_approved_valid_professional_output_publishes_with_verified_source_urls(
    monkeypatch, tmp_path: Path
):
    from app.orchestration.daily import run_channel

    candidate, packet = _candidate_and_packet()
    production = _valid_production(tmp_path)
    _patch_story(monkeypatch, candidate, packet, production)

    seen = {}

    class Publisher:
        def stage(self, video, thumbnail, meta):
            seen.update(video=video, thumbnail=thumbnail, meta=meta)
            return SimpleNamespace(video_id="yt123", status="succeeded")

        def stage_and_schedule(self, *args, **kwargs):
            raise AssertionError("unscheduled test should use stage")

    repo = Repository(tmp_path / "state.db")
    repo.init()
    repo.set_renderer_approved("professional", True)
    result = run_channel(
        "kernelrush",
        repo,
        day_index=0,
        output_dir=tmp_path / "output",
        dry_run=False,
        tts=object(),
        publisher=Publisher(),
        renderer="professional",
    )

    description = seen["meta"]["description"]
    assert production.long_video == Path(seen["video"])
    assert "https://primary.example/alpha" in description
    assert "https://secondary.example/alpha" in description
    assert "Sources are listed in the research packet" not in description
    assert result["youtube_video_id"] == "yt123"
