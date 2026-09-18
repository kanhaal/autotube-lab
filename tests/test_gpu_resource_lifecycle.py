from __future__ import annotations

import json
from pathlib import Path


def test_ollama_client_can_explicitly_unload_model(monkeypatch):
    from app.editorial.ollama import OllamaJsonClient

    seen = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return json.dumps({"done": True, "done_reason": "unload", "response": ""}).encode()

    def fake_urlopen(req, timeout):
        seen.update(json.loads(req.data))
        return Response()

    monkeypatch.setattr("app.editorial.ollama.urllib.request.urlopen", fake_urlopen)
    OllamaJsonClient(model="qwen3.5:9b").unload()

    assert seen == {"model": "qwen3.5:9b", "keep_alive": 0}


def test_configured_tts_release_delegates_to_backend():
    from app.narration.backend import ConfiguredTTS

    class Backend:
        name = "fake"

        def __init__(self):
            self.released = 0

        def synthesize(self, text, out, voice_profile):
            return out

        def release(self):
            self.released += 1

    backend = Backend()
    tts = ConfiguredTTS(backend, "voice")

    tts.release()

    assert backend.released == 1


def test_production_narration_releases_tts_before_caption_stage(tmp_path):
    from app.orchestration.production import build_professional_stages

    class TTS:
        def __init__(self):
            self.released = 0

        def synthesize(self, text, out):
            Path(out).write_bytes(text.encode())
            return Path(out)

        def release(self):
            self.released += 1

    tts = TTS()
    stages = build_professional_stages(
        channel_id="kernelrush",
        channel_cfg={"id": "kernelrush"},
        packet={},
        title="title",
        output_dir=tmp_path,
        tts=tts,
    )
    state = {
        "fact_ok": True,
        "layout_issues": (),
        "script": "long",
        "short_script": "short",
        "short_asset_manifest": object(),
    }

    result = stages.narration(state)

    assert result["narration"].name == "narration.wav"
    assert result["short_narration"].name == "short-narration.wav"
    assert tts.released == 1


def test_production_captions_release_transcriber_after_alignment(tmp_path):
    from app.orchestration.production import build_professional_stages

    class Transcriber:
        def __init__(self):
            self.released = 0

        def release(self):
            self.released += 1

    transcriber = Transcriber()

    def align(audio, script, speech_transcriber):
        assert speech_transcriber is transcriber
        return (f"cue:{script}",)

    stages = build_professional_stages(
        channel_id="kernelrush",
        channel_cfg={"id": "kernelrush"},
        packet={},
        title="title",
        output_dir=tmp_path,
        tts=object(),
        caption_aligner=align,
        transcriber=transcriber,
    )
    state = {
        "fact_ok": True,
        "layout_issues": (),
        "narration": tmp_path / "narration.wav",
        "script": "long",
        "short_narration": tmp_path / "short-narration.wav",
        "short_script": "short",
    }

    result = stages.captions(state)

    assert result["captions"] == ("cue:long",)
    assert result["short_captions"] == ("cue:short",)
    assert transcriber.released == 1


def test_deep_media_smoke_loads_and_releases_caption_model(monkeypatch):
    from app.health import media

    monkeypatch.setattr(media, "_ollama_model", lambda: {"ok": True, "detail": "qwen"})
    monkeypatch.setattr(media, "_command_version", lambda name: {"ok": True, "detail": name})
    monkeypatch.setattr(media, "_remotion", lambda: {"ok": True, "detail": "remotion"})
    monkeypatch.setattr(media, "_tool", lambda name: {"ok": True, "detail": name})
    monkeypatch.setattr(media, "_nvenc", lambda: {"ok": True, "detail": "nvenc"})
    monkeypatch.setattr(media, "_module", lambda name: {"ok": True, "detail": name})
    monkeypatch.setattr(media, "_deep_chatterbox", lambda: {"ok": True, "detail": "loaded"})
    monkeypatch.setattr(media, "_deep_whisper", lambda: {"ok": True, "detail": "loaded"}, raising=False)
    monkeypatch.setattr(media, "_tiny_render", lambda: {"ok": True, "detail": "rendered"})

    report = media.run_media_smoke(deep=True)

    assert report["chatterbox"]["ok"] is True
    assert report["faster_whisper"]["ok"] is True
    assert report["faster_whisper"]["detail"] == "loaded"
    assert report["tiny_render"]["ok"] is True


def test_legacy_professional_renderer_releases_heavy_resources_between_stages(
    monkeypatch, tmp_path
):
    from app.assets.models import AssetManifest
    from app.captions.models import CaptionCue
    from app.planning.scene_schema import ScenePlan, SceneSpec
    from app.rendering.pipeline import render_professional_episode

    events: list[str] = []

    class TTS:
        def synthesize(self, text, out):
            events.append(f"tts:{text}")
            Path(out).write_bytes(b"voice")
            return Path(out)

        def release(self):
            events.append("tts:release")

    class Transcriber:
        def release(self):
            events.append("whisper:release")

    class Runner:
        def render(self, package_dir, composition, out):
            Path(out).write_bytes(b"video")
            return Path(out)

    def align(audio, script, transcriber):
        events.append(f"whisper:{script}")
        return (CaptionCue(0.0, 1.0, script, tuple(script.split())),)

    def package(*args, **kwargs):
        path = Path(args[7])
        path.mkdir(parents=True, exist_ok=True)
        return path

    def thumbnails(*args, **kwargs):
        out = Path(args[4]) / "thumb.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"png")
        return (out,)

    def fake_master(narration, cfg, out):
        Path(out).write_bytes(b"master")
        return Path(out)

    monkeypatch.setattr("app.rendering.pipeline._master_audio", fake_master)

    plan = ScenePlan(
        "kernelrush",
        "longform",
        (SceneSpec("s1", "Long narration.", "hook", "headline"),),
    )

    render_professional_episode(
        channel_cfg={"id": "kernelrush", "name": "KernelRush", "brand": {}},
        title="Title",
        script="Long narration.",
        scene_plan=plan,
        packet={"sources": []},
        asset_manifest=AssetManifest(records=()),
        tts=TTS(),
        out_dir=tmp_path,
        llm=object(),
        runner=Runner(),
        transcriber=Transcriber(),
        caption_aligner=align,
        package_builder=package,
        thumbnail_renderer=thumbnails,
        short_builder=lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("skip short")),
    )

    assert events.index("tts:release") < events.index("whisper:Long narration.")
    assert "whisper:release" in events
