from __future__ import annotations

from dataclasses import dataclass

from app.planning.scene_schema import ScenePlan


class AssetResolutionError(ValueError):
    pass


@dataclass(frozen=True)
class AssetRequest:
    id: str
    kind: str
    source_url: str
    source_name: str | None
    purpose: str
    required: bool = False


def _source_by_url(packet: dict) -> dict[str, dict]:
    return {
        str(source.get("url", "")).strip(): source
        for source in packet.get("sources", [])
        if str(source.get("url", "")).strip()
    }


def _source_from_id(source_id: str, sources: list[dict]) -> dict | None:
    normalized = source_id.strip().lower().replace("-", "_")
    if not normalized.startswith("source_"):
        return None
    try:
        index = int(normalized.split("_", 1)[1]) - 1
    except ValueError:
        return None
    if 0 <= index < len(sources):
        return sources[index]
    return None


def resolve_scene_assets(scene_plan: ScenePlan, packet: dict) -> tuple[AssetRequest, ...]:
    sources = list(packet.get("sources", []))
    verified = _source_by_url(packet)
    requests: list[AssetRequest] = []

    for scene in scene_plan.scenes:
        if scene.scene_type != "source_browser":
            continue

        source_url = str(scene.data.get("source_url", "")).strip()
        source: dict | None = None

        if source_url:
            source = verified.get(source_url)
            if source is None:
                raise AssetResolutionError(
                    f"scene {scene.id} requested URL that is not a verified research source"
                )
        elif scene.source_ids:
            source = _source_from_id(scene.source_ids[0], sources)
            if source is not None:
                source_url = str(source.get("url", "")).strip()
                source = verified.get(source_url)

        if source is None or not source_url:
            continue

        requests.append(
            AssetRequest(
                id=f"source-{len(requests) + 1}",
                kind="source_screenshot",
                source_url=source_url,
                source_name=source.get("source_name"),
                purpose=scene.purpose,
                required=bool(scene.data.get("asset_required", False)),
            )
        )

    return tuple(requests)
