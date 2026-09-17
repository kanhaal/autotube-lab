from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from app.rendering.ffmpeg import MediaProbe


def test_contact_sheet_samples_evenly_spaced_video_times(monkeypatch, tmp_path: Path):
    from app.quality import contact_sheet

    video = tmp_path / "video.mp4"
    video.write_bytes(b"video")
    out = tmp_path / "contact.jpg"
    monkeypatch.setattr(
        contact_sheet,
        "probe_media",
        lambda path: MediaProbe("h264", "aac", 1920, 1080, 30.0, 8.0, 8.0, 8.0, 1000),
    )
    seen: list[float] = []

    def fake_run(command, **kwargs):
        timestamp = float(command[command.index("-ss") + 1])
        seen.append(timestamp)
        frame = Path(command[-1])
        Image.new("RGB", (160, 90), "black").save(frame)

    monkeypatch.setattr(contact_sheet.subprocess, "run", fake_run)

    assert contact_sheet.build_contact_sheet(video, out, sample_count=4) == out
    assert seen == pytest.approx([1.0, 3.0, 5.0, 7.0])
    assert out.is_file()


class _FakeLlm:
    def __init__(self, result: dict):
        self.result = result
        self.calls: list[tuple[str, dict]] = []

    def generate_json(self, system_prompt: str, payload: dict, **kwargs):
        self.calls.append((system_prompt, payload))
        return self.result


def test_visual_critic_accepts_only_structured_allowed_issue_codes(tmp_path: Path):
    from app.quality.visual_critic import critique_contact_sheet

    contact = tmp_path / "contact.jpg"
    contact.write_bytes(b"jpg")
    thumbnail = tmp_path / "thumb.png"
    thumbnail.write_bytes(b"png")
    llm = _FakeLlm(
        {
            "ok": False,
            "issues": [{"code": "clutter", "message": "Too much competing copy"}],
            "targeted_changes": ["Reduce secondary text in scene 4"],
        }
    )

    result = critique_contact_sheet("kernelrush", contact, (thumbnail,), llm)

    assert result.ok is False
    assert result.issues[0].code == "clutter"
    assert result.targeted_changes == ("Reduce secondary text in scene 4",)
    assert llm.calls


def test_visual_critic_rejects_unregistered_issue_code(tmp_path: Path):
    from app.quality.visual_critic import critique_contact_sheet

    contact = tmp_path / "contact.jpg"
    contact.write_bytes(b"jpg")
    llm = _FakeLlm(
        {
            "ok": False,
            "issues": [{"code": "invented_problem", "message": "Nope"}],
            "targeted_changes": [],
        }
    )

    with pytest.raises(ValueError, match="unsupported visual issue code"):
        critique_contact_sheet("lobbysignal", contact, (), llm)
