from pathlib import Path

from PIL import Image

from app.assets.fallbacks import render_fallback_card
from app.planning.scene_schema import SceneSpec


def test_fallback_card_is_1080p_uses_channel_background_and_is_local_only(tmp_path: Path):
    cfg = {
        "name": "KernelRush",
        "brand": {
            "background": "#0A0D12",
            "foreground": "#F5F7FA",
            "accent": "#5EF2C2",
            "secondary": "#7AA2FF",
        },
    }
    scene = SceneSpec(
        id="s7",
        narration="The release gives developers another option.",
        purpose="explain why the launch matters",
        scene_type="fallback_editorial",
        headline="WHY IT MATTERS",
    )

    record = render_fallback_card(cfg, scene, tmp_path / "fallback.png")

    with Image.open(record.local_path) as image:
        assert image.size == (1920, 1080)
        assert image.getpixel((0, 0))[:3] == (10, 13, 18)

    assert record.id == "fallback-s7"
    assert record.kind == "fallback_editorial"
    assert record.source_url is None
    assert record.source_name is None
    assert record.usage == scene.purpose
    assert len(record.sha256) == 64
