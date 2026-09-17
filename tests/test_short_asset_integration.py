from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def test_professional_pipeline_prepares_assets_for_short_scene_plan(monkeypatch, tmp_path: Path):
    from app.assets.models import AssetManifest, AssetRecord
    from app.planning.scene_schema import ScenePlan, SceneSpec
    from app.rendering.pipeline import render_professional_episode
    from app.shorts.pipeline import ShortStory

    long_plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(
            SceneSpec(
                id="long-1",
                narration="Long headline.",
                purpose="hook",
                scene_type="headline",
                headline="Long headline",
            ),
        ),
    )
    short_plan = ScenePlan(
        channel_id="kernelrush",
        format="short",
        scenes=(
            SceneSpec(
                id="short-1",
                narration="Short verified source.",
                purpose="evidence",
                scene_type="source_browser",
                headline="Short source",
                source_ids=("source_1",),
            ),
        ),
    )
    packet = {
        "sources": [
            {
                "source_name": "Short Official",
                "url": "https://example.com/short-only",
                "text": "Short verified source.",
            }
        ]
    }

    short_image = tmp_path / "short-source.png"
    short_image.write_bytes(b"png")
    short_assets = AssetManifest(
        records=(
            AssetRecord(
                id="short-source",
                kind="source_screenshot",
                local_path=str(short_image),
                source_url="https://example.com/short-only",
                source_name="Short Official",
                usage="evidence",
                license_note="source screenshot",
                sha256="abc",
                captured_at=datetime.now(timezone.utc),
            ),
        )
    )

    prepared: list[ScenePlan] = []

    def asset_preparer(scene_plan, research_packet, channel_cfg, episode_dir):
        prepared.append(scene_plan)
        assert research_packet is packet
        assert Path(episode_dir) == tmp_path / "episode" / "short-assets"
        return short_assets

    packaged_assets: list[AssetManifest] = []

    def package_builder(
        channel_cfg,
        title,
        script,
        scene_plan,
        captions,
        asset_manifest,
        audio_path,
        out_dir,
        *,
        format="long",
    ):
        packaged_assets.append(asset_manifest)
        path = Path(out_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    class FakeTTS:
        def synthesize(self, text, out):
            path = Path(out)
            path.write_bytes(b"audio")
            return path

    class FakeRunner:
        def render(self, package_dir, composition, out):
            path = Path(out)
            path.write_bytes(b"video")
            return path

    def fake_mix(narration, music, sfx_events, out, **kwargs):
        path = Path(out)
        path.write_bytes(b"master")
        return path

    def thumbnails(channel_cfg, title, scene_plan, assets, out_dir, count=5):
        path = Path(out_dir) / "thumb.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"png")
        return (path,)

    monkeypatch.setattr("app.rendering.pipeline.mix_episode_audio", fake_mix)

    outputs = render_professional_episode(
        channel_cfg={"id": "kernelrush", "name": "KernelRush", "brand": {}},
        title="Asset integration",
        script="Long headline.",
        scene_plan=long_plan,
        packet=packet,
        asset_manifest=AssetManifest(records=()),
        tts=FakeTTS(),
        out_dir=tmp_path / "episode",
        llm=object(),
        runner=FakeRunner(),
        transcriber=object(),
        caption_aligner=lambda *args: (),
        package_builder=package_builder,
        thumbnail_renderer=thumbnails,
        short_builder=lambda *args: ShortStory(
            script="Short verified source.",
            scene_plan=short_plan,
        ),
        asset_preparer=asset_preparer,
    )

    assert prepared == [short_plan]
    assert packaged_assets == [AssetManifest(records=()), short_assets]
    assert outputs.short_video is not None
