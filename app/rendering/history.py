from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class RenderRun:
    channel_id: str
    run_id: str
    directory: Path
    latest_pointer: Path


def _channel_id(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "-")
    if not normalized:
        raise ValueError("channel_id is required")
    if any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for character in normalized):
        raise ValueError(f"unsupported channel_id: {value!r}")
    return normalized


def _run_id(now: datetime) -> str:
    instant = now.astimezone(timezone.utc)
    return instant.strftime("%Y%m%dT%H%M%S.%fZ")


def create_render_run(
    root: Path,
    channel_id: str,
    *,
    now: datetime | None = None,
    run_id: str | None = None,
) -> RenderRun:
    channel = _channel_id(channel_id)
    instant = now or datetime.now(timezone.utc)
    identifier = (run_id or _run_id(instant)).strip()
    if not identifier or any(character in identifier for character in "\\/:*?\"<>|"):
        raise ValueError(f"invalid render run id: {identifier!r}")

    channel_root = Path(root) / channel
    runs_root = channel_root / "runs"
    directory = runs_root / identifier
    if directory.exists():
        raise FileExistsError(f"render run already exists: {directory}")
    directory.mkdir(parents=True, exist_ok=False)

    latest_pointer = channel_root / "latest.json"
    latest_pointer.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "channel_id": channel,
                "run_id": identifier,
                "path": str(directory.resolve()),
                "created_at": instant.astimezone(timezone.utc).isoformat(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return RenderRun(
        channel_id=channel,
        run_id=identifier,
        directory=directory,
        latest_pointer=latest_pointer,
    )


def latest_render_run(root: Path, channel_id: str) -> Path | None:
    channel = _channel_id(channel_id)
    pointer = Path(root) / channel / "latest.json"
    if not pointer.is_file():
        return None
    payload = json.loads(pointer.read_text(encoding="utf-8"))
    path = Path(str(payload.get("path", "")))
    return path.resolve() if path else None
