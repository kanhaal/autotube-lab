from datetime import UTC, datetime
from pathlib import Path

from PIL import Image

from app.assets.models import AssetManifest, AssetRecord
from app.planning.scene_schema import ScenePlan, SceneSpec
from app.visuals.thumbnail_v2 import THUMBNAIL_LAYOUTS, render_thumbnail_variants, thumbnail_overlay


def _plan() -> ScenePlan:
    return ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(
            SceneSpec(
                id="s1",
                narration="The launch changed how local models run.",
                purpose="hook",
                scene_type="stat",
                headline="Local AI just changed",
                emphasis=("2x", "faster"),
                data={"value": 2, "suffix": "x", "label": "faster"},
            ),
        ),
    )


def _assets(tmp_path: Path) -> AssetManifest:
    image = tmp_path / "source.png"
    Image.new("RGB", (900, 600), "#26344A").save(image)
    return AssetManifest(
        records=(
            AssetRecord(
                id="hero",
                kind="image",
                local_path=str(image),
                source_url="https://example.com/source",
                source_name="Example",
                usage="thumbnail candidate",
                license_note="test fixture",
                sha256="abc",
                captured_at=datetime.now(UTC),
            ),
        )
    )


def test_thumbnail_overlay_is_mobile_short():
    assert len(thumbnail_overlay("This launch changes local AI forever today").split()) <= 5


def test_thumbnail_variants_are_unique_1280x720_images(tmp_path):
    cfg = {
        "id": "kernelrush",
        "name": "KernelRush",
        "brand": {
            "background": "#0A0D12",
            "foreground": "#F5F7FA",
            "accent": "#5EF2C2",
            "secondary": "#7AA2FF",
        },
    }
    outputs = render_thumbnail_variants(
        cfg,
        "This launch changes local AI forever today",
        _plan(),
        _assets(tmp_path),
        tmp_path / "thumbs",
        count=5,
    )

    assert len(outputs) == 5
    assert len({path.name for path in outputs}) == 5
    assert {path.stem.split("-")[-1] for path in outputs} == set(THUMBNAIL_LAYOUTS)
    for path in outputs:
        with Image.open(path) as image:
            assert image.size == (1280, 720)


def test_thumbnail_variant_count_is_bounded(tmp_path):
    cfg = {"id": "kernelrush", "name": "KernelRush", "brand": {}}
    assert len(render_thumbnail_variants(cfg, "A title", _plan(), AssetManifest(records=()), tmp_path, count=3)) == 3

    try:
        render_thumbnail_variants(cfg, "A title", _plan(), AssetManifest(records=()), tmp_path, count=2)
    except ValueError as exc:
        assert "3 and 5" in str(exc)
    else:
        raise AssertionError("expected ValueError")
