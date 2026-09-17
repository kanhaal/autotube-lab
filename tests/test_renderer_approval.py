from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest

from app.storage.sqlite import Repository


def test_fresh_repository_reports_professional_renderer_unapproved(tmp_path: Path):
    repo = Repository(tmp_path / "autotube.db")
    repo.init()

    assert repo.get_setting("renderer.professional.approved") is None
    assert repo.renderer_approved("professional") is False


def test_renderer_approval_persists(tmp_path: Path):
    database = tmp_path / "autotube.db"
    repo = Repository(database)
    repo.init()
    repo.set_renderer_approved("professional", True)

    reopened = Repository(database)
    reopened.init()
    assert reopened.renderer_approved("professional") is True


def test_live_professional_run_refuses_before_channel_or_publisher_work(monkeypatch, tmp_path: Path):
    from app import cli
    from app.orchestration import daily

    repo = Repository(tmp_path / "autotube.db")
    repo.init()
    called = {"run": False, "config": False}

    monkeypatch.setattr(cli, "_repo", lambda args: repo)

    def fail_config(channel_id):
        called["config"] = True
        raise AssertionError("channel setup must not run before approval gate")

    def fail_run(*args, **kwargs):
        called["run"] = True
        raise AssertionError("production must not run before approval gate")

    monkeypatch.setattr(cli, "channel_config", fail_config)
    monkeypatch.setattr(daily, "run_channel", fail_run)
    args = Namespace(
        db=str(repo.path),
        output=str(tmp_path / "output"),
        channel="kernelrush",
        render=False,
        live=True,
        renderer="professional",
        client_secrets="client_secret.json",
    )

    with pytest.raises(SystemExit, match="professional renderer is not approved"):
        cli.cmd_run(args)

    assert called == {"run": False, "config": False}
