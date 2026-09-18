from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from pathlib import Path

from app.assets.models import AssetManifest
from app.rendering.ffmpeg import probe_media


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _ensure_within(path: Path, root: Path, *, label: str) -> Path:
    resolved = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"{label} must be within asset_root") from exc
    return resolved


def _dimensions(format_name: str) -> tuple[int, int]:
    if format_name == "long":
        return 1920, 1080
    if format_name == "short":
        return 1080, 1920
    raise ValueError(f"unsupported render format: {format_name}")


def build_render_package(
    channel_cfg: dict,
    title: str,
    script: str,
    scene_plan,
    captions,
    asset_manifest: AssetManifest,
    audio_path: Path,
    out_dir: Path,
    *,
    format: str = "long",
    asset_root: Path | None = None,
) -> Path:
    package_dir = Path(out_dir)
    package_dir.mkdir(parents=True, exist_ok=True)
    images_dir = package_dir / "images"
    audio_dir = package_dir / "audio"
    images_dir.mkdir(exist_ok=True)
    audio_dir.mkdir(exist_ok=True)

    width, height = _dimensions(format)
    audio_source = Path(audio_path).resolve()
    if not audio_source.is_file():
        raise FileNotFoundError(audio_source)
    try:
        audio_probe = probe_media(audio_source)
    except Exception as exc:  # noqa: BLE001 - package boundary converts probe failures to validation
        raise ValueError(f"render audio is unreadable: {audio_source}: {exc}") from exc
    audio_duration = audio_probe.audio_duration or audio_probe.format_duration
    if not audio_probe.audio_codec or audio_duration <= 0:
        raise ValueError(f"render audio has no usable audio stream: {audio_source}")
    audio_dest = audio_dir / audio_source.name
    shutil.copy2(audio_source, audio_dest)

    copied_records: list[dict] = []
    for record in asset_manifest.records:
        source = Path(record.local_path)
        if asset_root is not None:
            source = _ensure_within(source, Path(asset_root), label="asset path")
        else:
            source = source.resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        suffix = source.suffix or ".bin"
        dest = images_dir / f"{record.id}{suffix}"
        shutil.copy2(source, dest)
        payload = record.to_dict()
        payload["local_path"] = dest.relative_to(package_dir).as_posix()
        copied_records.append(payload)

    manifest_payload = {
        "schema_version": "1",
        "format": format,
        "channel_id": str(channel_cfg.get("id", scene_plan.channel_id)),
        "channel_name": str(channel_cfg.get("name", scene_plan.channel_id)),
        "title": title,
        "width": width,
        "height": height,
        "fps": 30,
        "duration_source": "audio",
        "duration_seconds": audio_duration,
        "audio_path": audio_dest.relative_to(package_dir).as_posix(),
        "theme": channel_cfg.get("brand", {}),
    }
    script_payload = {"title": title, "script": script}
    scene_payload = {
        "schema_version": scene_plan.schema_version,
        "channel_id": scene_plan.channel_id,
        "format": scene_plan.format,
        "scenes": [asdict(scene) for scene in scene_plan.scenes],
    }
    caption_payload = {
        "schema_version": "1",
        "cues": [asdict(cue) for cue in captions],
    }
    asset_payload = {
        "schema_version": asset_manifest.schema_version,
        "records": copied_records,
    }

    _write_json(package_dir / "manifest.json", manifest_payload)
    _write_json(package_dir / "script.json", script_payload)
    _write_json(package_dir / "scenes.json", scene_payload)
    _write_json(package_dir / "captions.json", caption_payload)
    _write_json(package_dir / "asset-manifest.json", asset_payload)
    return package_dir
