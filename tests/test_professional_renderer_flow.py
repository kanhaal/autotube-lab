from datetime import datetime, timezone
from pathlib import Path

from app.domain.models import StoryCandidate
from app.orchestration.daily import run_channel
from app.orchestration.production import ProductionResult
from app.quality.models import QualityReport
from app.storage.sqlite import Repository


def test_run_channel_routes_render_through_professional_production(monkeypatch, tmp_path: Path):
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

    monkeypatch.setattr("app.orchestration.daily.collect_for_niche", lambda niche: [candidate])
    monkeypatch.setattr("app.orchestration.daily.research_candidate", lambda item: packet)

    seen = {}

    def fake_production(**kwargs):
        seen.update(kwargs)
        directory = Path(kwargs["output_dir"])
        video = directory / "video.mp4"
        short = directory / "short.mp4"
        thumb = directory / "thumbnails" / "thumbnail-subject.png"
        video.write_bytes(b"video")
        short.write_bytes(b"short")
        thumb.parent.mkdir(parents=True, exist_ok=True)
        thumb.write_bytes(b"png")
        return ProductionResult(
            state={
                "long_video": video,
                "short_video": short,
                "thumbnails": (thumb,),
                "audio": directory / "master.wav",
            },
            quality_report=QualityReport(ok=True, issues=()),
        )

    monkeypatch.setattr(
        "app.orchestration.production.produce_professional_episode",
        fake_production,
    )

    repo = Repository(tmp_path / "state.db")
    repo.init()
    tts = object()
    result = run_channel(
        "kernelrush",
        repo,
        day_index=0,
        output_dir=tmp_path / "output",
        dry_run=True,
        editorial_llm=object(),
        tts=tts,
        renderer="professional",
    )

    assert seen["tts"] is tts
    assert seen["packet"] == packet
    assert seen["channel_id"] == "kernelrush"
    assert Path(seen["output_dir"]).parts[-3:-1] == ("kernelrush", "runs")
    assert result["video"].endswith("video.mp4")
    assert result["short_video"].endswith("short.mp4")
    assert result["renderer"] == "professional"
    assert result["quality_ok"] is True
