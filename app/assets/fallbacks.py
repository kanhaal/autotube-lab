from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont

from app.assets.manifest import sha256_file
from app.assets.models import AssetRecord


def _font(size: int, *, bold: bool = False):
    names = ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"] if bold else ["DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def render_fallback_card(channel_cfg: dict, scene, out: Path) -> AssetRecord:
    brand = channel_cfg["brand"]
    background = brand["background"]
    foreground = brand["foreground"]
    accent = brand["accent"]
    secondary = brand.get("secondary", accent)

    image = Image.new("RGB", (1920, 1080), background)
    draw = ImageDraw.Draw(image)

    safe_left = 150
    safe_right = 1770
    draw.rounded_rectangle((safe_left, 130, safe_left + 12, 950), radius=6, fill=accent)
    draw.text(
        (safe_left + 55, 155),
        str(channel_cfg.get("name", "AutoTube")).upper(),
        fill=accent,
        font=_font(34, bold=True),
    )

    headline = scene.headline.strip() or scene.purpose.strip() or "EDITORIAL CONTEXT"
    draw.multiline_text(
        (safe_left + 55, 300),
        _wrap(headline.upper(), 24),
        fill=foreground,
        font=_font(84, bold=True),
        spacing=18,
    )

    purpose = scene.purpose.strip() or "Supporting context"
    draw.multiline_text(
        (safe_left + 58, 710),
        _wrap(purpose, 64),
        fill=secondary,
        font=_font(38),
        spacing=10,
    )
    draw.line((safe_left + 55, 920, safe_right, 920), fill=secondary, width=2)
    draw.text(
        (safe_left + 55, 940),
        "ORIGINAL AUTOTUBE VISUAL",
        fill=foreground,
        font=_font(24, bold=True),
    )

    target = Path(out)
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, format="PNG")

    return AssetRecord(
        id=f"fallback-{scene.id}",
        kind="fallback_editorial",
        local_path=str(target),
        source_url=None,
        source_name=None,
        usage=scene.purpose,
        license_note="original AutoTube generated graphic",
        sha256=sha256_file(target),
        captured_at=datetime.now(timezone.utc),
        scene_id=scene.id,
    )
