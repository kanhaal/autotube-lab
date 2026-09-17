from __future__ import annotations

from pathlib import Path

from app.assets.fallbacks import render_fallback_card
from app.assets.manifest import write_asset_manifest
from app.assets.models import AssetManifest, AssetRecord
from app.assets.resolver import AssetRequest, resolve_scene_assets
from app.assets.screenshots import ScreenshotCapture


class AssetPreparationError(RuntimeError):
    pass


def _deduplicate_requests(requests: tuple[AssetRequest, ...]) -> tuple[AssetRequest, ...]:
    seen: set[tuple[str, str]] = set()
    result: list[AssetRequest] = []
    for request in requests:
        key = (request.source_url, request.purpose)
        if key in seen:
            continue
        seen.add(key)
        result.append(request)
    return tuple(result)


def prepare_assets(
    scene_plan,
    packet: dict,
    channel_cfg: dict,
    episode_dir: Path,
    capturer=None,
) -> AssetManifest:
    root = Path(episode_dir)
    asset_dir = root / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    capture = capturer or ScreenshotCapture()
    scene_by_id = {scene.id: scene for scene in scene_plan.scenes}

    records: list[AssetRecord] = []
    requested_scene_ids: set[str] = set()
    requests = _deduplicate_requests(resolve_scene_assets(scene_plan, packet))

    for request in requests:
        if request.scene_id:
            requested_scene_ids.add(request.scene_id)
        try:
            records.append(capture.capture(request, asset_dir))
        except Exception as exc:  # noqa: BLE001 - adapter boundary converts optional capture failure
            if request.required:
                raise AssetPreparationError(
                    f"required asset capture failed for {request.source_url}: {exc}"
                ) from exc
            scene = scene_by_id.get(request.scene_id or "")
            if scene is None:
                raise AssetPreparationError(
                    f"cannot build fallback for asset request {request.id} without a source scene"
                ) from exc
            records.append(
                render_fallback_card(
                    channel_cfg,
                    scene,
                    asset_dir / f"fallback-{scene.id}.png",
                )
            )

    for scene in scene_plan.scenes:
        if scene.scene_type == "fallback_editorial":
            records.append(
                render_fallback_card(
                    channel_cfg,
                    scene,
                    asset_dir / f"fallback-{scene.id}.png",
                )
            )
        elif scene.scene_type == "source_browser" and scene.id not in requested_scene_ids:
            if bool(scene.data.get("asset_required", False)):
                raise AssetPreparationError(
                    f"required asset for scene {scene.id} did not resolve to a verified source"
                )
            records.append(
                render_fallback_card(
                    channel_cfg,
                    scene,
                    asset_dir / f"fallback-{scene.id}.png",
                )
            )

    manifest = AssetManifest(records=tuple(records))
    write_asset_manifest(manifest.records, root / "asset-manifest.json")
    return manifest
