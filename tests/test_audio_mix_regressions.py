from pathlib import Path
from types import SimpleNamespace


def test_sfx_event_volume_reaches_ffmpeg_filter(monkeypatch, tmp_path: Path):
    from app.audio.mix import SfxEvent, mix_episode_audio

    narration = tmp_path / "narration.wav"
    sfx = tmp_path / "impact.wav"
    narration.write_bytes(b"voice")
    sfx.write_bytes(b"sfx")
    seen = {}

    def fake_run(command, **kwargs):
        seen["command"] = list(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("app.audio.mix.subprocess.run", fake_run)
    mix_episode_audio(
        narration,
        None,
        (SfxEvent(path=sfx, start_ms=180, volume=0.12),),
        tmp_path / "master.wav",
    )

    graph = seen["command"][seen["command"].index("-filter_complex") + 1]
    assert "adelay=180|180" in graph
    assert "volume=0.12" in graph


def test_wav_mastering_forces_production_sample_rate(monkeypatch, tmp_path: Path):
    from app.audio.mix import mix_episode_audio

    narration = tmp_path / "narration.wav"
    narration.write_bytes(b"voice")
    seen = {}

    def fake_run(command, **kwargs):
        seen["command"] = list(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("app.audio.mix.subprocess.run", fake_run)
    mix_episode_audio(narration, None, (), tmp_path / "master.wav")

    command = seen["command"]
    assert "-ar" in command
    assert command[command.index("-ar") + 1] == "48000"



def test_lowpass_reveal_is_applied_before_loudness_mastering(monkeypatch, tmp_path: Path):
    from app.audio.mix import mix_episode_audio

    narration = tmp_path / "narration.wav"
    narration.write_bytes(b"voice")
    seen = {}

    def fake_run(command, **kwargs):
        seen["command"] = list(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("app.audio.mix.subprocess.run", fake_run)
    mix_episode_audio(
        narration,
        None,
        (),
        tmp_path / "master.wav",
        lowpass_windows=((1200, 700),),
    )

    graph = seen["command"][seen["command"].index("-filter_complex") + 1]
    assert "lowpass=f=2600" in graph
    assert "lowpass=f=950" in graph
    assert "between(t,1.200" in graph
    assert graph.index("lowpass") < graph.index("loudnorm")
