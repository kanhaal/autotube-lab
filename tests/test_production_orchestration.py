from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

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


def test_visual_review_skips_entirely_when_hard_qa_failed(tmp_path: Path):
    from app.orchestration.production import (
        ProductionResult,
        ProductionStages,
        apply_visual_review,
    )

    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")
    failed = QualityReport(
        ok=False,
        issues=(QualityIssue("missing_audio", "render has no audio", fatal=True),),
    )
    result = ProductionResult(state={"long_video": video}, quality_report=failed)

    def forbidden(*args, **kwargs):
        raise AssertionError("visual review must not run after failed hard QA")

    stages = ProductionStages(*(forbidden for _ in range(8)))
    reviewed = apply_visual_review(
        result,
        channel_id="kernelrush",
        output_dir=tmp_path,
        stages=stages,
        llm=object(),
        contact_sheet_builder=forbidden,
        critic=forbidden,
        visual_corrector=forbidden,
    )

    assert reviewed == result


def test_visual_review_allows_at_most_one_targeted_correction_rerender(tmp_path: Path):
    from app.orchestration.production import (
        ProductionResult,
        ProductionStages,
        apply_visual_review,
    )
    from app.quality.visual_critic import VisualCritique, VisualIssue

    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")
    thumbnail = tmp_path / "thumb.png"
    thumbnail.write_bytes(b"png")
    green = QualityReport(ok=True, issues=())
    result = ProductionResult(
        state={
            "long_video": video,
            "thumbnails": (thumbnail,),
            "scene_plan": "original",
        },
        quality_report=green,
    )
    seen: list[str] = []

    def noop(state):
        return {}

    def render(state):
        seen.append("render")
        return {"long_video": video}

    def thumbnails(state):
        seen.append("thumbnails")
        return {"thumbnails": (thumbnail,)}

    def qa(state):
        seen.append("qa")
        return {"quality_report": green}

    stages = ProductionStages(
        editorial=noop,
        assets=noop,
        narration=noop,
        captions=noop,
        audio=noop,
        render=render,
        thumbnails=thumbnails,
        qa=qa,
    )

    def build_contact_sheet(video_path, out):
        Path(out).write_bytes(b"contact")
        return Path(out)

    critique = VisualCritique(
        ok=False,
        issues=(VisualIssue("clutter", "Secondary copy competes with the headline"),),
        targeted_changes=("Reduce secondary copy",),
    )

    reviewed = apply_visual_review(
        result,
        channel_id="kernelrush",
        output_dir=tmp_path,
        stages=stages,
        llm=object(),
        contact_sheet_builder=build_contact_sheet,
        critic=lambda *args: critique,
        visual_corrector=lambda state, visual: {"scene_plan": "corrected"},
    )

    assert seen == ["render", "thumbnails", "qa"]
    assert reviewed.state["scene_plan"] == "corrected"
    assert reviewed.state["visual_correction_attempts"] == 1
    assert reviewed.state["visual_targeted_changes"] == ("Reduce secondary copy",)

    reviewed_again = apply_visual_review(
        reviewed,
        channel_id="kernelrush",
        output_dir=tmp_path,
        stages=stages,
        llm=object(),
        contact_sheet_builder=build_contact_sheet,
        critic=lambda *args: critique,
        visual_corrector=lambda state, visual: {"scene_plan": "corrected-again"},
    )

    assert seen == ["render", "thumbnails", "qa"]
    assert reviewed_again.state["visual_correction_attempts"] == 1


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
