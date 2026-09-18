from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import wave

import pytest


def test_narration_segment_round_trip(tmp_path):
    from app.narration.models import NarrationSegment

    seg = NarrationSegment(
        text="Hello world.",
        raw_path=tmp_path / "raw.wav",
        normalized_path=tmp_path / "norm.wav",
        duration=1.25,
        backend="chatterbox",
        voice_profile="kernelrush",
    )
    restored = NarrationSegment.from_dict(seg.to_dict())
    assert restored == seg


def test_backend_selection_keeps_sapi_legacy():
    from app.narration.backend import select_tts_backend
    from app.narration.tts import WindowsSapiTTS

    assert isinstance(select_tts_backend("sapi"), WindowsSapiTTS)
    with pytest.raises(ValueError):
        select_tts_backend("unknown")


def test_chatterbox_adapter_passes_profile_settings(tmp_path):
    from app.narration.chatterbox import ChatterboxTTS

    class FakeModel:
        sr = 24000

        def __init__(self):
            self.kwargs = None

        def generate(self, text, **kwargs):
            assert text == "A concise technology update."
            self.kwargs = kwargs
            return [0.0, 0.1, -0.1]

    captured = {}

    def writer(path, wav, sample_rate):
        captured.update(path=Path(path), wav=wav, sample_rate=sample_rate)
        Path(path).write_bytes(b"wav")

    model = FakeModel()
    tts = ChatterboxTTS(
        model=model,
        writer=writer,
        voice_profiles={"kernelrush": {"exaggeration": 0.35, "cfg_weight": 0.55}},
    )
    out = tts.synthesize(
        "A concise technology update.", tmp_path / "voice.wav", "kernelrush"
    )

    assert out.exists()
    assert model.kwargs == {"exaggeration": 0.35, "cfg_weight": 0.55}
    assert captured["sample_rate"] == 24000
    assert "audio_prompt_path" not in model.kwargs


def test_fallback_tts_uses_secondary_once(tmp_path):
    from app.narration.fallback import FallbackTTS, NarrationError

    class Broken:
        name = "primary"

        def synthesize(self, *args, **kwargs):
            raise RuntimeError("boom")

    class Working:
        name = "fallback"

        def __init__(self):
            self.calls = 0

        def synthesize(self, text, out, voice_profile):
            self.calls += 1
            Path(out).write_bytes(b"ok")
            return Path(out)

    fallback = Working()
    result = FallbackTTS(Broken(), fallback).synthesize(
        "hello", tmp_path / "ok.wav", "profile"
    )
    assert result.exists()
    assert fallback.calls == 1

    with pytest.raises(NarrationError) as exc:
        FallbackTTS(Broken(), Broken()).synthesize(
            "hello", tmp_path / "bad.wav", "profile"
        )
    assert "primary" in str(exc.value)


def test_segment_script_prefers_paragraphs_and_splits_long_text():
    from app.narration.segment import segment_script

    script = "First paragraph.\n\nSecond paragraph has two sentences. It should stay readable."
    parts = segment_script(script, max_chars=45)
    assert parts
    assert all(parts)
    assert all(len(part) <= 45 for part in parts)
    assert parts[0] == "First paragraph."


def test_render_narration_tracks_segment_metadata(tmp_path):
    from app.narration.assemble import render_narration

    class FakeBackend:
        name = "fake"

        def synthesize(self, text, out, voice_profile):
            Path(out).write_bytes(text.encode())
            return Path(out)

    def normalizer(source, dest):
        Path(dest).write_bytes(Path(source).read_bytes())
        return Path(dest)

    def duration(_):
        return 1.5

    def concatenator(paths, out):
        Path(out).write_bytes(b"joined")
        return Path(out)

    track = render_narration(
        "One sentence.\n\nTwo sentence.",
        FakeBackend(),
        "kernelrush",
        tmp_path,
        max_chars=20,
        normalizer=normalizer,
        duration_probe=duration,
        concatenator=concatenator,
    )
    assert track.path.exists()
    assert [s.text for s in track.segments] == ["One sentence.", "Two sentence."]
    assert track.duration == 3.0


def test_caption_alignment_uses_actual_word_timestamps(tmp_path):
    from app.captions.align import align_narration

    words = [
        SimpleNamespace(start=0.0, end=0.3, word="Hello"),
        SimpleNamespace(start=0.31, end=0.7, word="world."),
        SimpleNamespace(start=0.8, end=1.1, word="Next"),
        SimpleNamespace(start=1.11, end=1.5, word="line."),
    ]
    segments = [SimpleNamespace(words=words, text="Hello world. Next line.")]

    class FakeTranscriber:
        def transcribe(self, path, word_timestamps=False):
            assert path.endswith("audio.wav")
            assert word_timestamps is True
            return iter(segments), SimpleNamespace(language="en")

    cues = align_narration(tmp_path / "audio.wav", "Hello world. Next line.", FakeTranscriber())
    assert cues[0].start == 0.0
    assert cues[-1].end == 1.5
    assert "Hello" in cues[0].text


def test_caption_alignment_blocks_large_mismatch(tmp_path):
    from app.captions.align import CaptionAlignmentError, align_narration

    words = [SimpleNamespace(start=0.0, end=1.0, word="unrelated")]
    segments = [SimpleNamespace(words=words, text="completely unrelated")]

    class FakeTranscriber:
        def transcribe(self, path, word_timestamps=False):
            return iter(segments), None

    with pytest.raises(CaptionAlignmentError):
        align_narration(
            tmp_path / "audio.wav",
            "This script is about a verified technology launch with several details.",
            FakeTranscriber(),
        )


def test_audio_library_selects_only_declared_existing_assets(tmp_path):
    from app.audio.library import AudioLibrary

    music = tmp_path / "bed.wav"
    music.write_bytes(b"music")
    cfg = tmp_path / "audio.yml"
    cfg.write_text(
        f"""assets:\n  - id: calm-bed\n    path: {music.as_posix()}\n    kind: music\n    channels: [kernelrush]\n    moods: [analytical]\n    license_note: CC0\n    source_url: https://example.com/music\n  - id: missing\n    path: {str(tmp_path / 'missing.wav').replace(chr(92), '/')}\n    kind: music\n    channels: [kernelrush]\n    moods: [analytical]\n    license_note: local\n    source_url: null\n""",
        encoding="utf-8",
    )
    asset = AudioLibrary.from_yaml(cfg).select("music", "kernelrush", "analytical")
    assert asset is not None
    assert asset.id == "calm-bed"


def _write_silence(path: Path, seconds: float = 0.25):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(b"\x00\x00" * int(24000 * seconds))


def test_audio_mix_builds_ducking_and_loudness_graph(tmp_path):
    from app.audio.mix import build_audio_filter_graph, mix_episode_audio

    graph = build_audio_filter_graph(has_music=True, sfx_count=0, target_lufs=-14.0, true_peak=-1.5)
    assert "sidechaincompress" in graph
    assert "loudnorm=I=-14.0" in graph

    narration = tmp_path / "narration.wav"
    _write_silence(narration)
    out = mix_episode_audio(narration, None, (), tmp_path / "master.wav")
    assert out.exists()


def test_channel_configs_define_distinct_professional_voice_profiles():
    from app.config import channel_config

    kernel = channel_config("kernelrush")
    lobby = channel_config("lobbysignal")
    assert kernel["voice"]["backend"] == "chatterbox"
    assert lobby["voice"]["backend"] == "chatterbox"
    assert kernel["voice"]["profile"] != lobby["voice"]["profile"]
    assert kernel["audio"]["mood"] != lobby["audio"]["mood"]


def test_media_health_does_not_load_gpu_models(monkeypatch):
    from app.narration.health import media_health

    monkeypatch.setattr("app.narration.health.importlib.util.find_spec", lambda name: object())
    monkeypatch.setattr("app.narration.health.shutil.which", lambda name: f"/bin/{name}")
    result = media_health()
    assert result["chatterbox"] is True
    assert result["kokoro"] is True
    assert result["faster_whisper"] is True
    assert result["ffmpeg"] is True


def test_caption_alignment_keeps_kinetic_caption_phrases_compact(tmp_path):
    from app.captions.align import align_narration

    words = [
        SimpleNamespace(start=index * 0.25, end=(index + 1) * 0.25, word=word)
        for index, word in enumerate(
            "This source card now moves like a premium editorial sequence with clean timing.".split()
        )
    ]
    segments = [
        SimpleNamespace(
            words=words,
            text="This source card now moves like a premium editorial sequence with clean timing.",
        )
    ]

    class FakeTranscriber:
        def transcribe(self, path, word_timestamps=False):
            return iter(segments), None

    cues = align_narration(
        tmp_path / "audio.wav",
        "This source card now moves like a premium editorial sequence with clean timing.",
        FakeTranscriber(),
    )

    assert cues
    assert max(len(cue.words) for cue in cues) <= 5
