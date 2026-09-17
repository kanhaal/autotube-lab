from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from app.assets.models import AssetManifest
from app.planning.scene_schema import ScenePlan

THUMBNAIL_LAYOUTS = ("subject", "stat", "comparison", "ui_focus", "curiosity")
SIZE = (1280, 720)


def _font(size: int, *, bold: bool = True):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def thumbnail_overlay(title: str) -> str:
    words = [word.strip() for word in title.upper().split() if word.strip()]
    return " ".join(words[:5])


def _brand(channel_cfg: dict) -> dict[str, str]:
    brand = channel_cfg.get("brand") or {}
    return {
        "background": brand.get("background", "#080B12"),
        "foreground": brand.get("foreground", "#F7FAFF"),
        "accent": brand.get("accent", "#66F2C1"),
        "secondary": brand.get("secondary", "#6B95FF"),
    }


def _hero_image(assets: AssetManifest | None) -> Image.Image | None:
    if assets is None:
        return None
    for record in assets.records:
        if record.kind not in {"image", "screenshot", "source_screenshot"}:
            continue
        path = Path(record.local_path)
        if not path.is_file():
            continue
        try:
            return Image.open(path).convert("RGB")
        except OSError:
            continue
    return None


def _scene_value(scene_plan: ScenePlan, key: str, default=""):
    for scene in scene_plan.scenes:
        if key in scene.data:
            return scene.data[key]
    return default


def _draw_channel(draw: ImageDraw.ImageDraw, channel_cfg: dict, colors: dict[str, str]) -> None:
    label = str(channel_cfg.get("name") or channel_cfg.get("id") or "AUTOTUBE").upper()
    draw.rounded_rectangle((56, 48, 330, 108), radius=22, fill=colors["accent"])
    draw.text((78, 62), label[:18], fill=colors["background"], font=_font(28))


def _fit_text(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], color: str) -> None:
    x1, y1, x2, y2 = box
    words = text.split()
    if not words:
        return
    for size in (94, 84, 74, 66, 58):
        font = _font(size)
        lines: list[str] = []
        current = ""
        for word in words:
            proposed = f"{current} {word}".strip()
            width = draw.textbbox((0, 0), proposed, font=font)[2]
            if current and width > x2 - x1:
                lines.append(current)
                current = word
            else:
                current = proposed
        if current:
            lines.append(current)
        line_height = int(size * 1.08)
        if len(lines) * line_height <= y2 - y1:
            for index, line in enumerate(lines[:3]):
                draw.text((x1, y1 + index * line_height), line, fill=color, font=font)
            return


def _base(colors: dict[str, str]) -> Image.Image:
    image = Image.new("RGB", SIZE, colors["background"])
    draw = ImageDraw.Draw(image)
    draw.ellipse((890, -240, 1450, 320), fill=colors["secondary"])
    glow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((760, -280, 1500, 450), fill=(255, 255, 255, 34))
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    image = Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB")
    return image


def _subject_layout(channel_cfg, title, scene_plan, assets, colors):
    image = _base(colors)
    draw = ImageDraw.Draw(image)
    hero = _hero_image(assets)
    if hero is not None:
        hero = ImageOps.fit(hero, (570, 600), method=Image.Resampling.LANCZOS)
        image.paste(hero, (680, 82))
        overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle((600, 0, 760, 720), fill=(8, 11, 18, 150))
        overlay = overlay.filter(ImageFilter.GaussianBlur(32))
        image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(image)
    else:
        draw.rounded_rectangle((720, 130, 1160, 610), radius=54, fill=colors["secondary"])
        draw.rounded_rectangle((780, 190, 1100, 550), radius=36, outline=colors["accent"], width=10)
        draw.text((840, 315), "SIGNAL", fill=colors["foreground"], font=_font(54))
    _draw_channel(draw, channel_cfg, colors)
    _fit_text(draw, thumbnail_overlay(title), (56, 190, 650, 610), colors["foreground"])
    return image


def _stat_layout(channel_cfg, title, scene_plan, assets, colors):
    image = _base(colors)
    draw = ImageDraw.Draw(image)
    value = _scene_value(scene_plan, "value", "")
    suffix = str(_scene_value(scene_plan, "suffix", ""))
    label = str(_scene_value(scene_plan, "label", "KEY CHANGE")).upper()
    stat = f"{value}{suffix}" if value != "" else "BIG"
    _draw_channel(draw, channel_cfg, colors)
    draw.text((70, 180), stat, fill=colors["accent"], font=_font(190))
    draw.text((82, 410), label[:28], fill=colors["foreground"], font=_font(42))
    _fit_text(draw, thumbnail_overlay(title), (640, 170, 1190, 610), colors["foreground"])
    return image


def _comparison_layout(channel_cfg, title, scene_plan, assets, colors):
    image = Image.new("RGB", SIZE, colors["background"])
    draw = ImageDraw.Draw(image)
    left = str(_scene_value(scene_plan, "before", _scene_value(scene_plan, "left", "BEFORE")))
    right = str(_scene_value(scene_plan, "after", _scene_value(scene_plan, "right", "AFTER")))
    draw.rectangle((0, 0, 628, 720), fill=colors["background"])
    draw.rectangle((652, 0, 1280, 720), fill=colors["secondary"])
    draw.rounded_rectangle((610, 0, 670, 720), radius=24, fill=colors["accent"])
    _draw_channel(draw, channel_cfg, colors)
    draw.text((72, 210), "BEFORE", fill=colors["accent"], font=_font(34))
    draw.text((720, 210), "AFTER", fill=colors["background"], font=_font(34))
    _fit_text(draw, left.upper()[:55], (72, 285, 560, 600), colors["foreground"])
    _fit_text(draw, right.upper()[:55], (720, 285, 1200, 600), colors["foreground"])
    return image


def _ui_focus_layout(channel_cfg, title, scene_plan, assets, colors):
    image = _base(colors)
    draw = ImageDraw.Draw(image)
    _draw_channel(draw, channel_cfg, colors)
    draw.rounded_rectangle((95, 160, 1185, 640), radius=34, fill="#F3F5F8")
    draw.rounded_rectangle((95, 160, 1185, 225), radius=34, fill="#D9DEE7")
    draw.ellipse((128, 184, 150, 206), fill="#FF6B6B")
    draw.ellipse((163, 184, 185, 206), fill="#FFD166")
    draw.ellipse((198, 184, 220, 206), fill="#06D6A0")
    hero = _hero_image(assets)
    if hero is not None:
        hero = ImageOps.fit(hero, (1000, 350), method=Image.Resampling.LANCZOS)
        image.paste(hero, (140, 250))
    else:
        draw.rounded_rectangle((150, 270, 1130, 590), radius=24, fill="#171D28")
        draw.text((205, 345), thumbnail_overlay(title), fill=colors["foreground"], font=_font(62))
        draw.rectangle((205, 470, 520, 485), fill=colors["accent"])
    return image


def _curiosity_layout(channel_cfg, title, scene_plan, assets, colors):
    image = _base(colors)
    draw = ImageDraw.Draw(image)
    _draw_channel(draw, channel_cfg, colors)
    draw.text((910, 120), "?", fill=colors["accent"], font=_font(380))
    _fit_text(draw, thumbnail_overlay(title), (72, 200, 850, 610), colors["foreground"])
    draw.rounded_rectangle((72, 620, 540, 650), radius=15, fill=colors["accent"])
    return image


_RENDERERS = {
    "subject": _subject_layout,
    "stat": _stat_layout,
    "comparison": _comparison_layout,
    "ui_focus": _ui_focus_layout,
    "curiosity": _curiosity_layout,
}


def render_thumbnail_variants(
    channel_cfg: dict,
    title: str,
    scene_plan: ScenePlan,
    assets: AssetManifest | None,
    out_dir: Path,
    count: int = 5,
) -> tuple[Path, ...]:
    if not 3 <= count <= 5:
        raise ValueError("thumbnail variant count must be between 3 and 5")
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    colors = _brand(channel_cfg)
    outputs: list[Path] = []
    for layout in THUMBNAIL_LAYOUTS[:count]:
        image = _RENDERERS[layout](channel_cfg, title, scene_plan, assets, colors)
        path = target / f"thumbnail-{layout}.png"
        image.save(path, format="PNG", optimize=True)
        outputs.append(path)
    return tuple(outputs)
