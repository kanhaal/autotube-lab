from pathlib import Path

from app.rendering.runner import RemotionRunner


def test_remotion_command_is_argument_safe(tmp_path: Path):
    package_dir = tmp_path / "episode package"
    package_dir.mkdir()
    out = tmp_path / "renders" / "episode.mp4"

    runner = RemotionRunner(video_dir=Path("video"), npx="npx")
    command = runner.command(package_dir, "KernelRushLong", out)

    assert command[:4] == ["npx", "remotion", "render", "src/index.ts"]
    assert "KernelRushLong" in command
    assert str(out.resolve()) in command
    assert f"--public-dir={package_dir.resolve()}" in command
    assert f"--props={package_dir.resolve() / 'remotion-props.json'}" in command
    assert "--crf=15" in command
    assert "--pixel-format=yuv420p" in command
    assert "--audio-bitrate=192K" in command
    assert "--x264-preset=slow" in command
    assert "--concurrency=50%" in command
    assert "--image-format=png" in command
    assert "--color-space=bt709" in command
    assert "--sample-rate=48000" in command


def test_remotion_runner_resolves_default_npx_shim(monkeypatch):
    resolved = r"C:\\Program Files\\nodejs\\npx.cmd"
    monkeypatch.setattr("app.rendering.runner.shutil.which", lambda name: resolved if name == "npx" else None)

    runner = RemotionRunner(video_dir=Path("video"))

    assert runner.npx == resolved


def test_remotion_runner_uses_shell_false_and_utf8_decoding(monkeypatch, tmp_path: Path):
    package_dir = tmp_path / "package"
    package_dir.mkdir()
    out = tmp_path / "episode.mp4"
    calls = []

    class Result:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        out.write_bytes(b"video")
        return Result()

    monkeypatch.setattr("app.rendering.runner.subprocess.run", fake_run)
    runner = RemotionRunner(video_dir=Path("video"), npx="npx")
    result = runner.render(package_dir, "KernelRushLong", out)

    assert result == out.resolve()
    kwargs = calls[0][1]
    assert kwargs["shell"] is False
    assert kwargs["cwd"] == Path("video").resolve()
    assert kwargs["encoding"] == "utf-8"
    assert kwargs["errors"] == "replace"


def test_remotion_runner_failure_surfaces_render_output(monkeypatch, tmp_path: Path):
    package_dir = tmp_path / "package"
    package_dir.mkdir()
    out = tmp_path / "episode.mp4"

    class Result:
        returncode = 1
        stdout = "Bundled code successfully\nRendering frames"
        stderr = "Error: Failed to decode audio asset"

    monkeypatch.setattr("app.rendering.runner.subprocess.run", lambda *args, **kwargs: Result())
    runner = RemotionRunner(video_dir=Path("video"), npx="npx")

    try:
        runner.render(package_dir, "KernelRushLong", out)
    except RuntimeError as exc:
        message = str(exc)
    else:
        raise AssertionError("runner should raise when Remotion exits non-zero")

    assert "Failed to decode audio asset" in message
    assert "Rendering frames" in message
    assert "remotion-render.log" in message
