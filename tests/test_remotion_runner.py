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
    assert "--crf=14" in command
    assert "--pixel-format=yuv420p" in command
    assert "--audio-bitrate=192K" in command
    assert "--x264-preset=slow" in command
    assert "--color-space=bt709" in command
    assert "--gl=angle" in command
    assert "--concurrency=4" in command
    assert "--hardware-acceleration=required" not in command


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



def test_nvidia_profile_requires_hardware_acceleration_and_uses_bitrate(
    monkeypatch,
    tmp_path: Path,
):
    package_dir = tmp_path / "package"
    package_dir.mkdir()
    out = tmp_path / "episode.mp4"
    monkeypatch.setenv("AUTOTUBE_RENDER_ACCEL", "nvidia")
    monkeypatch.setenv("AUTOTUBE_GPU_VIDEO_BITRATE", "36M")

    runner = RemotionRunner(video_dir=Path("video"), npx="npx")
    command = runner.command(package_dir, "KernelRushLong", out)

    assert "--hardware-acceleration=required" in command
    assert "--video-bitrate=36M" in command
    assert "--gl=angle" in command
    assert "--crf=14" not in command
    assert "--x264-preset=slow" not in command


def test_auto_profile_uses_nvidia_when_gpu_is_detected(monkeypatch, tmp_path: Path):
    package_dir = tmp_path / "package"
    package_dir.mkdir()
    out = tmp_path / "episode.mp4"
    monkeypatch.setenv("AUTOTUBE_RENDER_ACCEL", "auto")
    monkeypatch.setattr("app.rendering.runner.nvidia_gpu_name", lambda: "NVIDIA GeForce RTX 4050 Laptop GPU")

    runner = RemotionRunner(video_dir=Path("video"), npx="npx")
    command = runner.command(package_dir, "KernelRushLong", out)

    assert "--hardware-acceleration=required" in command
    assert "--video-bitrate=35M" in command
    assert "--crf=14" not in command


def test_auto_profile_stays_cpu_when_nvidia_is_unavailable(monkeypatch, tmp_path: Path):
    package_dir = tmp_path / "package"
    package_dir.mkdir()
    out = tmp_path / "episode.mp4"
    monkeypatch.setenv("AUTOTUBE_RENDER_ACCEL", "auto")
    monkeypatch.setattr("app.rendering.runner.nvidia_gpu_name", lambda: None)

    runner = RemotionRunner(video_dir=Path("video"), npx="npx")
    command = runner.command(package_dir, "KernelRushLong", out)

    assert "--crf=14" in command
    assert "--x264-preset=slow" in command
    assert "--hardware-acceleration=required" not in command
