import sys

import app.cli as cli


def _parse_renderer(monkeypatch, argv):
    seen = {}
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(cli, "cmd_run", lambda args: seen.update(renderer=args.renderer))
    cli.main()
    return seen["renderer"]


def test_run_daily_renderer_defaults_from_environment(monkeypatch):
    monkeypatch.setenv("AUTOTUBE_RENDERER", "professional")
    assert _parse_renderer(monkeypatch, ["autotube", "run-daily", "--channel", "kernelrush"]) == "professional"


def test_run_daily_renderer_flag_overrides_environment(monkeypatch):
    monkeypatch.setenv("AUTOTUBE_RENDERER", "professional")
    assert _parse_renderer(
        monkeypatch,
        ["autotube", "run-daily", "--channel", "kernelrush", "--renderer", "legacy"],
    ) == "legacy"
