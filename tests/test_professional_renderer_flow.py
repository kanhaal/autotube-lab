from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.assets.models import AssetManifest
from app.domain.models import StoryCandidate
from app.planning.scene_schema import ScenePlan, SceneSpec
from app.rendering.pipeline import ProductionOutputs
from app.orchestration.daily import run_channel
from app.storage.sqlite import Repository


@dataclass(frozen=True)
class FakeBundle:
    script: str


def test_run_channel_routes_render_through_professional_pipeline(monkeypatch, tmp_path: Path):
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
            {"source_name": "Primary", "url": "https://primary.example/alpha", "text": "Alpha released a local developer tool."},
            {"source_name": "Secondary", "url": "https://secondary.example/alpha", "text": "Alpha released the tool for local execution."},
        ],
    }
    script = "Alpha released a local developer tool. The tool supports local execution."
    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(SceneSpec(id="s1", narration=script, purpose="hook", scene_type="headline", headline="Alpha launch"),),
    )

    monkeypatch.setattr("app.orchestration.daily.collect_for_niche", lambda niche: [candidate])
    monkeypatch.setattr("app.orchestration.daily.research_candidate", lambda item: packet)
    monkeypatch.setattr("app.orchestration.editorial.prepare_editorial", lambda *args: (FakeBundle(script), plan))
    monkeypatch.setattr("app.orchestration.editorial.prepare_episode_assets", lambda *args: AssetManifest(records=()))

    seen = {}

    def fake_render(**kwargs):
        seen.update(kwargs)
        directory = Path(kwargs["out_dir"])
        video = directory / "video.mp4"
        short = directory / "short.mp4"
        thumb = directory / "thumbnails" / "thumbnail-subject.png"
        video.write_bytes(b"video")
        short.write_bytes(b"short")
        thumb.parent.mkdir(parents=True, exist_ok=True)
        thumb.write_bytes(b"png")
        return ProductionOutputs(
            long_video=video,
            short_video=short,
            thumbnails=(thumb,),
            render_package=directory / "render-package-long",
            short_render_package=directory / "render-package-short",
            audio=directory / "narration.wav",
        )

    monkeypatch.setattr("app.rendering.pipeline.render_professional_episode", fake_render)

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
    assert seen["scene_plan"] == plan
    assert result["video"].endswith("video.mp4")
    assert result["short_video"].endswith("short.mp4")
    assert result["renderer"] == "professional"
