from __future__ import annotations

from datetime import datetime, timezone

from app.domain.models import StoryCandidate
from app.quality.models import QualityIssue, QualityReport


def test_produce_episode_runs_production_stages_in_exact_order():
    from app.orchestration.production import ProductionStages, produce_episode

    seen: list[str] = []

    def stage(name, **values):
        def run(state):
            seen.append(name)
            return values

        return run

    stages = ProductionStages(
        editorial=stage("editorial", script="script", scene_plan="plan"),
        assets=stage("assets", asset_manifest="assets"),
        narration=stage("narration", narration="narration.wav"),
        captions=stage("captions", captions=("cue",)),
        audio=stage("audio", audio="master.wav"),
        render=stage("render", long_video="video.mp4", short_video=None),
        thumbnails=stage("thumbnails", thumbnails=("thumb.png",)),
        qa=stage("qa", quality_report=QualityReport(ok=True, issues=())),
    )

    result = produce_episode({"channel_id": "kernelrush"}, stages)

    assert seen == [
        "editorial",
        "assets",
        "narration",
        "captions",
        "audio",
        "render",
        "thumbnails",
        "qa",
    ]
    assert result.quality_report.ok is True
    assert result.state["long_video"] == "video.mp4"


def test_produce_episode_marks_failed_hard_qa_as_not_publishable():
    from app.orchestration.production import ProductionStages, produce_episode

    def passthrough(state):
        return {}

    failed = QualityReport(
        ok=False,
        issues=(QualityIssue("missing_audio", "render has no audio", fatal=True),),
    )
    stages = ProductionStages(
        editorial=passthrough,
        assets=passthrough,
        narration=passthrough,
        captions=passthrough,
        audio=passthrough,
        render=passthrough,
        thumbnails=passthrough,
        qa=lambda state: {"quality_report": failed},
    )

    result = produce_episode({}, stages)

    assert result.quality_report == failed
    assert result.publishable is False


def test_run_channel_never_invokes_publisher_after_failed_professional_qa(
    monkeypatch, tmp_path
):
    from app.orchestration.daily import run_channel
    from app.orchestration.production import ProductionResult
    from app.storage.sqlite import Repository

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
    failed = QualityReport(
        ok=False,
        issues=(QualityIssue("missing_audio", "render has no audio", fatal=True),),
    )
    production = ProductionResult(state={}, quality_report=failed)

    monkeypatch.setattr("app.orchestration.daily.collect_for_niche", lambda niche: [candidate])
    monkeypatch.setattr("app.orchestration.daily.research_candidate", lambda item: packet)
    monkeypatch.setattr(
        "app.orchestration.production.produce_professional_episode",
        lambda **kwargs: production,
    )

    class Publisher:
        def stage(self, *args, **kwargs):
            raise AssertionError("publisher must not be called after failed QA")

        def stage_and_schedule(self, *args, **kwargs):
            raise AssertionError("publisher must not be called after failed QA")

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

    assert result["status"] == "blocked_quality"
    assert result["quality_issues"][0]["code"] == "missing_audio"
