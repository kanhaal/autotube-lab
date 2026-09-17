from pathlib import Path

from app.assets.models import AssetManifest
from app.captions.models import CaptionCue
from app.planning.scene_schema import ScenePlan, SceneSpec
from app.rendering.pipeline import ProductionOutputs, renderer_mode, render_professional_episode


def _plan():
    return ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(SceneSpec(id="s1", narration="Verified narration.", purpose="hook", scene_type="headline", headline="Verified story"),),
    )


def test_renderer_mode_defaults_to_legacy(monkeypatch):
    monkeypatch.delenv("AUTOTUBE_RENDERER", raising=False)
    assert renderer_mode() == "legacy"


def test_renderer_mode_can_select_professional(monkeypatch):
    monkeypatch.setenv("AUTOTUBE_RENDERER", "professional")
    assert renderer_mode() == "professional"


def test_renderer_mode_rejects_unknown(monkeypatch):
    monkeypatch.setenv("AUTOTUBE_RENDERER", "other")
    try:
        renderer_mode()
    except ValueError as exc:
        assert "AUTOTUBE_RENDERER" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_optional_short_failure_keeps_valid_long_render(tmp_path):
    class FakeTTS:
        def synthesize(self, text, out):
            Path(out).write_bytes(b"wav")
            return Path(out)

    class FakeRunner:
        def render(self, package_dir, composition, out):
            Path(out).write_bytes(b"video")
            return Path(out)

    def align(audio, script, transcriber):
        return (CaptionCue(0.0, 1.0, script, tuple(script.split())),)

    def package(channel_cfg, title, script, scene_plan, captions, asset_manifest, audio_path, out_dir, **kwargs):
        path = Path(out_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def thumbnails(channel_cfg, title, scene_plan, assets, out_dir, count=5):
        result = []
        for index in range(count):
            path = Path(out_dir) / f"thumbnail-{index}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"png")
            result.append(path)
        return tuple(result)

    def short_failure(*args, **kwargs):
        raise RuntimeError("optional short render failed")

    outputs = render_professional_episode(
        channel_cfg={"id": "kernelrush", "name": "KernelRush", "brand": {}},
        title="Verified story",
        script="Verified narration.",
        scene_plan=_plan(),
        packet={"sources": []},
        asset_manifest=AssetManifest(records=()),
        tts=FakeTTS(),
        out_dir=tmp_path,
        llm=object(),
        runner=FakeRunner(),
        transcriber=object(),
        caption_aligner=align,
        package_builder=package,
        thumbnail_renderer=thumbnails,
        short_builder=short_failure,
    )

    assert isinstance(outputs, ProductionOutputs)
    assert outputs.long_video.is_file()
    assert outputs.short_video is None
    assert outputs.short_error == "optional short render failed"
    assert len(outputs.thumbnails) == 5
