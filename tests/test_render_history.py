from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.rendering.history import create_render_run, latest_render_run


def test_render_runs_are_versioned_and_never_overwrite(tmp_path: Path):
    root = tmp_path / "output"
    first = create_render_run(
        root,
        "kernelrush",
        now=datetime(2026, 9, 19, 0, 0, 0, 1000, tzinfo=timezone.utc),
    )
    second = create_render_run(
        root,
        "kernelrush",
        now=datetime(2026, 9, 19, 0, 0, 0, 2000, tzinfo=timezone.utc),
    )

    assert first.directory != second.directory
    assert first.directory.is_dir()
    assert second.directory.is_dir()
    assert first.directory.parent == root / "kernelrush" / "runs"
    assert second.directory.parent == root / "kernelrush" / "runs"

    pointer = json.loads((root / "kernelrush" / "latest.json").read_text(encoding="utf-8"))
    assert Path(pointer["path"]) == second.directory.resolve()
    assert pointer["run_id"] == second.run_id
    assert latest_render_run(root, "kernelrush") == second.directory.resolve()


def test_render_run_ids_are_filesystem_safe_and_channel_scoped(tmp_path: Path):
    run = create_render_run(
        tmp_path / "samples",
        "LobbySignal",
        now=datetime(2026, 9, 19, 1, 2, 3, 456789, tzinfo=timezone.utc),
    )

    assert run.channel_id == "lobbysignal"
    assert ":" not in run.run_id
    assert run.directory.name == run.run_id
    assert run.directory.parts[-3:] == ("lobbysignal", "runs", run.run_id)
