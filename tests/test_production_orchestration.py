from __future__ import annotations

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
