# AutoTube Narration + Captions + Audio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Windows SAPI with production-grade local narration, exact speech-aligned captions, and mastered music/SFX while keeping a lightweight fallback path.

**Architecture:** A backend interface exposes segmented TTS. Chatterbox is primary, Kokoro is fallback. Narration is generated in bounded chunks, concatenated deterministically, then faster-whisper aligns the final audio to the known script. A separate audio mixer handles background music, ducking, fades, and loudness normalization through FFmpeg.

**Tech Stack:** Python 3.11+, Chatterbox TTS, Kokoro, faster-whisper, FFmpeg/FFprobe, pytest.

**Spec:** `docs/superpowers/specs/2026-09-17-autotube-professional-media-engine-design.md`

## Global Constraints

- Chatterbox is primary; Kokoro is fallback.
- No unauthorized third-party voice cloning.
- TTS operates on bounded script segments, not one multi-minute request.
- Caption timing comes from actual speech alignment, not estimated word counts.
- Caption mismatch above threshold blocks production captions.
- Narration must remain clearly dominant over music/SFX.
- GPU-heavy models are loaded sequentially where practical.

---

### Task 1: Define TTS backend and narration segment models

**Files:**
- Create: `app/narration/models.py`
- Create: `app/narration/backend.py`
- Test: `tests/test_narration_backend.py`

**Interfaces:**
- `NarrationSegment(text, raw_path, normalized_path, duration, backend, voice_profile)`.
- Protocol: `synthesize(text: str, out: Path, voice_profile: str) -> Path`.

- [ ] Write failing tests for segment serialization and backend selection config.
- [ ] Verify RED.
- [ ] Implement typed model + `select_tts_backend(name: str, **deps)` supporting `chatterbox`, `kokoro`, `sapi` legacy.
- [ ] Verify and commit `feat: define narration backend interface`.

---

### Task 2: Add Chatterbox primary adapter

**Files:**
- Create: `app/narration/chatterbox.py`
- Modify: `pyproject.toml`
- Test: `tests/test_chatterbox_adapter.py`

**Interfaces:**
- Produces: `ChatterboxTTS.synthesize(text, out, voice_profile) -> Path`.

- [ ] Write tests using injected model object; assert output path, sample data write, and voice profile settings are passed.
- [ ] Verify RED.
- [ ] Add optional media dependency for Chatterbox without importing it at module import time; lazy-load inside backend.
- [ ] Implement adapter with configurable device (`cuda` default when available) and deterministic settings where supported.
- [ ] Add explicit guard that reference audio is optional and never auto-loaded from arbitrary paths.
- [ ] Verify and commit `feat: add Chatterbox production TTS`.

---

### Task 3: Add Kokoro fallback adapter and failover wrapper

**Files:**
- Create: `app/narration/kokoro.py`
- Create: `app/narration/fallback.py`
- Test: `tests/test_tts_fallback.py`

**Interfaces:**
- `FallbackTTS(primary, fallback).synthesize(...) -> Path`.

- [ ] Write test where primary raises and fallback succeeds; assert fallback called once.
- [ ] Write test where both fail; assert `NarrationError` includes both backend names.
- [ ] Verify RED.
- [ ] Implement lazy Kokoro adapter and single-attempt fallback wrapper.
- [ ] Verify and commit `feat: add resilient local TTS fallback`.

---

### Task 4: Segment scripts and assemble narration

**Files:**
- Create: `app/narration/segment.py`
- Create: `app/narration/assemble.py`
- Test: `tests/test_narration_segments.py`

**Interfaces:**
- `segment_script(script: str, max_chars=900) -> tuple[str, ...]`.
- `render_narration(script, backend, voice_profile, out_dir) -> NarrationTrack`.

- [ ] Write tests ensuring paragraph boundaries are preferred, no empty segment is emitted, and a long paragraph is sentence-split under max length.
- [ ] Write assembly test with fake WAV segment durations; assert ordered segment metadata and final path.
- [ ] Verify RED.
- [ ] Implement segmentation and FFmpeg concat through a generated concat file.
- [ ] Normalize each segment to consistent sample rate/channels before join.
- [ ] Verify and commit `feat: render segmented narration tracks`.

---

### Task 5: Add faster-whisper alignment and script mismatch gate

**Files:**
- Create: `app/captions/__init__.py`
- Create: `app/captions/align.py`
- Create: `app/captions/models.py`
- Test: `tests/test_caption_alignment.py`

**Interfaces:**
- `CaptionCue(start, end, text, words)`.
- `align_narration(audio: Path, script: str, transcriber) -> tuple[CaptionCue, ...]`.

- [ ] Write fake-transcriber test producing known timestamps and assert cue order/times.
- [ ] Write mismatch test: recognition differs substantially from normalized known script and raises `CaptionAlignmentError`.
- [ ] Verify RED.
- [ ] Implement text normalization and similarity threshold using `difflib.SequenceMatcher`; default threshold 0.82, configurable.
- [ ] Convert word timestamps into phrase cues bounded by roughly 2–7 words / punctuation breaks.
- [ ] Verify and commit `feat: align captions to generated narration`.

---

### Task 6: Add licensed local music/SFX library metadata

**Files:**
- Create: `app/audio/__init__.py`
- Create: `app/audio/library.py`
- Create: `config/audio/library.example.yml`
- Test: `tests/test_audio_library.py`

**Interfaces:**
- `AudioAsset(id, path, kind, channels, moods, license_note, source_url)`.
- `AudioLibrary.select(kind, channel_id, mood) -> AudioAsset | None`.

- [ ] Write tests proving only declared local assets are selectable and missing files are ignored/rejected.
- [ ] Verify RED.
- [ ] Implement YAML loader and deterministic selection (stable sorted candidate choice unless seed supplied).
- [ ] Add example config containing metadata only, no media files.
- [ ] Verify and commit `feat: add licensed local audio library`.

---

### Task 7: Mix and master narration/music/SFX

**Files:**
- Create: `app/audio/mix.py`
- Modify: `app/rendering/ffmpeg.py`
- Test: `tests/test_audio_mix.py`

**Interfaces:**
- `mix_episode_audio(narration, music, sfx_events, out, target_lufs=-14.0, true_peak=-1.5) -> Path`.

- [ ] Write command-construction tests asserting sidechain/volume ducking is present when music exists and `loudnorm` target is included.
- [ ] Add test for narration-only path.
- [ ] Verify RED.
- [ ] Implement FFmpeg filter graph builder separately from subprocess runner so it is unit testable.
- [ ] Use fade-in/out and music looping only when configured; never clip narration duration.
- [ ] Verify with a generated 2-second integration WAV using FFmpeg in CI.
- [ ] Commit `feat: mix and master episode audio`.

---

### Task 8: Add channel voice/audio profiles and hardware-safe health checks

**Files:**
- Modify: `config/channels/kernelrush.yml`
- Modify: `config/channels/lobbysignal.yml`
- Create: `app/narration/health.py`
- Modify: `app/cli.py`
- Test: `tests/test_media_health.py`

**Interfaces:**
- Channel config adds `voice.profile`, `voice.backend`, `audio.mood`, `audio.music_enabled`.
- `autotube health` adds TTS/ASR availability without loading all GPU models simultaneously.

- [ ] Write failing config/health tests.
- [ ] Verify RED.
- [ ] Add distinct KernelRush and LobbySignal voice profiles.
- [ ] Health checks dependencies/files/importability only; add separate `autotube media-smoke` later for actual GPU load.
- [ ] Verify and commit `feat: configure professional narration profiles`.

## Phase Exit Criteria

- Production render path can synthesize with Chatterbox and fall back to Kokoro.
- Narration is segmented and independently regenerable.
- Captions are aligned to actual TTS speech and mismatch-gated.
- Music/SFX are provenance-configured local assets only.
- FFmpeg mastering has deterministic loudness/ducking configuration.
- SAPI remains legacy-only.
- CI remains green without requiring GPU models to download in CI.
