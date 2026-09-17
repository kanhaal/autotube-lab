from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace


def test_caption_alignment_preserves_exact_word_timestamps(tmp_path: Path):
    from app.captions.align import align_narration

    words = [
        SimpleNamespace(start=0.0, end=0.22, word="Exact"),
        SimpleNamespace(start=0.29, end=0.61, word="timing."),
    ]
    segments = [SimpleNamespace(words=words, text="Exact timing.")]

    class FakeTranscriber:
        def transcribe(self, path, word_timestamps=False):
            assert word_timestamps is True
            return iter(segments), None

    cues = align_narration(
        tmp_path / "narration.wav",
        "Exact timing.",
        FakeTranscriber(),
    )

    assert [(word.text, word.start, word.end) for word in cues[0].word_timings] == [
        ("Exact", 0.0, 0.22),
        ("timing.", 0.29, 0.61),
    ]


def test_professional_pipeline_masters_audio_before_packaging(monkeypatch, tmp_path: Path):
    from app.assets.models import AssetManifest
    from app.planning.scene_schema import ScenePlan, SceneSpec
    from app.rendering.pipeline import render_professional_episode

    music = tmp_path / "music.wav"
    music.write_bytes(b"music")
    library = tmp_path / "audio-library.yml"
    library.write_text(
        "assets:\n"
        "  - id: bed\n"
        f"    path: {music.as_posix()}\n"
        "    kind: music\n"
        "    channels: [kernelrush]\n"
        "    moods: [analytical]\n"
        "    license_note: local-test\n"
        "    source_url: null\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("AUTOTUBE_AUDIO_LIBRARY", str(library))

    ffmpeg_commands: list[list[str]] = []

    def fake_run(command, **kwargs):
        ffmpeg_commands.append(list(command))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("app.audio.mix.subprocess.run", fake_run)

    class FakeTTS:
        def synthesize(self, text, out):
            path = Path(out)
            path.write_bytes(b"voice")
            return path

    class FakeRunner:
        def render(self, package_dir, composition, out):
            path = Path(out)
            path.write_bytes(b"video")
            return path

    packaged_audio: list[Path] = []

    def package_builder(
        channel_cfg,
        title,
        script,
        scene_plan,
        captions,
        asset_manifest,
        audio_path,
        out_dir,
        *,
        format="long",
    ):
        packaged_audio.append(Path(audio_path))
        path = Path(out_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def thumbnail_renderer(channel_cfg, title, scene_plan, asset_manifest, out_dir, count=5):
        thumb = Path(out_dir) / "thumb.png"
        thumb.parent.mkdir(parents=True, exist_ok=True)
        thumb.write_bytes(b"png")
        return (thumb,)

    def skip_short(*args, **kwargs):
        raise RuntimeError("skip short in long-form audio integration test")

    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(
            SceneSpec(
                id="s1",
                narration="Audio integration.",
                purpose="hook",
                scene_type="headline",
                headline="Audio integration",
            ),
        ),
    )
    out_dir = tmp_path / "episode"
    outputs = render_professional_episode(
        channel_cfg={
            "id": "kernelrush",
            "name": "KernelRush",
            "brand": {},
            "audio": {"mood": "analytical", "music_enabled": True},
        },
        title="Audio integration",
        script="Audio integration.",
        scene_plan=plan,
        packet={"sources": []},
        asset_manifest=AssetManifest(records=()),
        tts=FakeTTS(),
        out_dir=out_dir,
        runner=FakeRunner(),
        transcriber=object(),
        caption_aligner=lambda *args: (),
        package_builder=package_builder,
        thumbnail_renderer=thumbnail_renderer,
        short_builder=skip_short,
    )

    assert ffmpeg_commands, "professional production path must invoke the Phase 3 mixer"
    assert str(music) in ffmpeg_commands[0]
    assert packaged_audio[0] == out_dir / "master.wav"
    assert outputs.audio == out_dir / "master.wav"


def test_professional_pipeline_mixes_narration_only_when_library_is_missing(
    monkeypatch,
    tmp_path: Path,
):
    from app.assets.models import AssetManifest
    from app.planning.scene_schema import ScenePlan, SceneSpec
    from app.rendering.pipeline import render_professional_episode

    monkeypatch.setenv("AUTOTUBE_AUDIO_LIBRARY", str(tmp_path / "missing.yml"))
    commands: list[list[str]] = []

    def fake_run(command, **kwargs):
        commands.append(list(command))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("app.audio.mix.subprocess.run", fake_run)

    class FakeTTS:
        def synthesize(self, text, out):
            path = Path(out)
            path.write_bytes(b"voice")
            return path

    class FakeRunner:
        def render(self, package_dir, composition, out):
            path = Path(out)
            path.write_bytes(b"video")
            return path

    packaged_audio: list[Path] = []

    def package_builder(*args, **kwargs):
        audio_path = args[6]
        out_dir = args[7]
        packaged_audio.append(Path(audio_path))
        path = Path(out_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def thumbnail_renderer(channel_cfg, title, scene_plan, asset_manifest, out_dir, count=5):
        thumb = Path(out_dir) / "thumb.png"
        thumb.parent.mkdir(parents=True, exist_ok=True)
        thumb.write_bytes(b"png")
        return (thumb,)

    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(SceneSpec(id="s1", narration="Voice only.", purpose="hook", scene_type="headline"),),
    )
    out_dir = tmp_path / "episode"
    outputs = render_professional_episode(
        channel_cfg={
            "id": "kernelrush",
            "name": "KernelRush",
            "brand": {},
            "audio": {"mood": "analytical", "music_enabled": True},
        },
        title="Voice only",
        script="Voice only.",
        scene_plan=plan,
        packet={"sources": []},
        asset_manifest=AssetManifest(records=()),
        tts=FakeTTS(),
        out_dir=out_dir,
        runner=FakeRunner(),
        transcriber=object(),
        caption_aligner=lambda *args: (),
        package_builder=package_builder,
        thumbnail_renderer=thumbnail_renderer,
        short_builder=lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("skip")),
    )

    assert commands, "narration-only production must still run mastering/loudness normalization"
    assert commands[0].count("-i") == 1
    assert packaged_audio[0] == out_dir / "master.wav"
    assert outputs.audio == out_dir / "master.wav"
