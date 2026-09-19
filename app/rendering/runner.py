from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


_PACKAGE_FILES = {
    "manifest": "manifest.json",
    "script": "script.json",
    "scenes": "scenes.json",
    "captions": "captions.json",
    "assets": "asset-manifest.json",
}


@dataclass(frozen=True)
class RenderProfile:
    acceleration: str
    gpu_name: str | None
    video_bitrate: str | None


def nvidia_gpu_name() -> str | None:
    executable = shutil.which("nvidia-smi")
    if executable is None:
        return None
    try:
        result = subprocess.run(
            [executable, "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=4,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    name = (result.stdout or "").strip().splitlines()
    return name[0].strip() if name and name[0].strip() else None


def render_profile() -> RenderProfile:
    requested = os.getenv("AUTOTUBE_RENDER_ACCEL", "auto").strip().lower()
    if requested not in {"auto", "cpu", "nvidia"}:
        raise ValueError("AUTOTUBE_RENDER_ACCEL must be 'auto', 'cpu', or 'nvidia'")

    gpu = nvidia_gpu_name() if requested in {"auto", "nvidia"} else None
    if requested == "nvidia" and gpu is None:
        # Explicit NVIDIA mode is still emitted as required. Remotion then fails loudly
        # instead of silently falling back to x264, which is safer for performance testing.
        gpu = os.getenv("AUTOTUBE_NVIDIA_GPU_NAME", "").strip() or None
        return RenderProfile(
            acceleration="nvidia",
            gpu_name=gpu,
            video_bitrate=os.getenv("AUTOTUBE_GPU_VIDEO_BITRATE", "35M").strip() or "35M",
        )
    if requested == "auto" and gpu is not None:
        return RenderProfile(
            acceleration="nvidia",
            gpu_name=gpu,
            video_bitrate=os.getenv("AUTOTUBE_GPU_VIDEO_BITRATE", "35M").strip() or "35M",
        )
    return RenderProfile(acceleration="cpu", gpu_name=None, video_bitrate=None)


class RemotionRunner:
    def __init__(
        self,
        *,
        video_dir: Path = Path("video"),
        npx: str | None = None,
    ) -> None:
        self.video_dir = Path(video_dir)
        self.npx = npx or shutil.which("npx") or "npx"

    def command(self, package_dir: Path, composition: str, out: Path) -> list[str]:
        package_root = Path(package_dir).resolve()
        output = Path(out).resolve()
        props_path = package_root / "remotion-props.json"
        concurrency = max(1, int(os.getenv("AUTOTUBE_RENDER_CONCURRENCY", "4")))
        profile = render_profile()

        command = [
            self.npx,
            "remotion",
            "render",
            "src/index.ts",
            composition,
            str(output),
            f"--public-dir={package_root}",
            f"--props={props_path}",
            "--codec=h264",
            "--audio-codec=aac",
            "--pixel-format=yuv420p",
            "--audio-bitrate=192K",
            "--color-space=bt709",
            "--gl=angle",
            f"--concurrency={concurrency}",
        ]
        if profile.acceleration == "nvidia":
            command += [
                "--hardware-acceleration=required",
                f"--video-bitrate={profile.video_bitrate}",
            ]
        else:
            command += [
                "--crf=14",
                "--x264-preset=slow",
            ]
        return command

    def _write_props(self, package_dir: Path) -> Path:
        root = Path(package_dir).resolve()
        props_path = root / "remotion-props.json"
        if all((root / name).is_file() for name in _PACKAGE_FILES.values()):
            payload = {
                "pkg": {
                    "root": str(root),
                    **{
                        key: json.loads((root / name).read_text(encoding="utf-8"))
                        for key, name in _PACKAGE_FILES.items()
                    },
                }
            }
        else:
            payload = {"packageDir": str(root)}
        props_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return props_path

    def _write_render_profile(self, output: Path, command: list[str]) -> None:
        profile = render_profile()
        output.with_suffix(output.suffix + ".render.json").write_text(
            json.dumps(
                {
                    "schema_version": "1",
                    "acceleration": profile.acceleration,
                    "gpu_name": profile.gpu_name,
                    "video_bitrate": profile.video_bitrate,
                    "chromium_gl": "angle",
                    "command": command,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def render(self, package_dir: Path, composition: str, out: Path) -> Path:
        package_root = Path(package_dir).resolve()
        if not package_root.is_dir():
            raise FileNotFoundError(f"Render package directory not found: {package_root}")

        output = Path(out).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        self._write_props(package_root)
        command = self.command(package_root, composition, output)
        result = subprocess.run(
            command,
            cwd=self.video_dir.resolve(),
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode != 0:
            log_path = output.parent / "remotion-render.log"
            log_path.write_text(
                "COMMAND\n"
                + " ".join(command)
                + "\n\nSTDOUT\n"
                + (result.stdout or "")
                + "\n\nSTDERR\n"
                + (result.stderr or ""),
                encoding="utf-8",
            )
            stdout_tail = (result.stdout or "").strip()[-2000:]
            stderr_tail = (result.stderr or "").strip()[-4000:]
            details = "\n".join(
                part
                for part in (
                    f"STDERR:\n{stderr_tail}" if stderr_tail else "",
                    f"STDOUT:\n{stdout_tail}" if stdout_tail else "",
                )
                if part
            )
            suffix = f"\n{details}" if details else ""
            raise RuntimeError(
                f"Remotion render failed with exit code {result.returncode}; "
                f"see {log_path}{suffix}"
            )
        if not output.is_file():
            raise RuntimeError(f"Remotion reported success but did not create {output}")
        self._write_render_profile(output, command)
        return output
