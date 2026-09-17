# AutoTube QA + Orchestration + Rollout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add deterministic production QA, optional local visual critique, hardware smoke checks, and safe orchestration so only validated professional outputs can reach YouTube private staging.

**Architecture:** Media production returns typed outputs plus validation evidence. A hard deterministic gate validates files, dimensions, duration, audio, captions, assets, and thumbnails. An optional Qwen contact-sheet critic may request at most one targeted correction pass but cannot override hard failures. Live publishing remains blocked until the professional renderer is explicitly approved for supervised rollout.

**Tech Stack:** Python 3.11+, FFprobe, Pillow, Ollama/Qwen 3.5 9B, pytest, existing YouTube publisher.

**Spec:** `docs/superpowers/specs/2026-09-17-autotube-professional-media-engine-design.md`

## Global Constraints

- Failed hard QA never uploads.
- Visual critic is advisory; deterministic checks are authoritative.
- At most one automatic visual correction/rerender pass.
- Long-form may pass if an optional Short fails, but Short failure must be recorded.
- `run-daily --live` must not silently enable a newly built renderer before supervised approval.
- Existing private-first publisher behavior remains intact.

---

### Task 1: Expand FFprobe media inspection

**Files:**
- Modify: `app/rendering/ffmpeg.py`
- Test: `tests/test_media_probe.py`

**Interfaces:**
- Produces: `probe_media(path: Path) -> MediaProbe` with video/audio codec, width, height, frame rate, format duration, video duration, audio duration, file size.

- [ ] Write failing tests against generated 1-second synthetic MP4 with audio.
- [ ] Verify RED.
- [ ] Implement a single FFprobe JSON call and typed parser.
- [ ] Preserve `probe_video` compatibility by delegating to `probe_media`.
- [ ] Verify and commit `feat: inspect complete rendered media`.

---

### Task 2: Implement deterministic hard quality gate

**Files:**
- Create: `app/quality/__init__.py`
- Create: `app/quality/models.py`
- Create: `app/quality/validation.py`
- Test: `tests/test_quality_gate.py`

**Interfaces:**
- `QualityIssue(code, message, fatal)`.
- `QualityReport(ok, issues)`.
- `validate_longform(outputs, expected_duration, fact_ok=True) -> QualityReport`.
- `validate_short(outputs) -> QualityReport`.

- [ ] Write failing tests for wrong resolution, missing audio, duration mismatch, too-small file, absent caption artifact, missing thumbnails, and failed fact flag.
- [ ] Write passing test for valid 1920x1080 media with audio.
- [ ] Verify RED.
- [ ] Implement tolerances as named constants: duration mismatch max `1.0s` or `1.5%`, whichever is greater; minimum file size configurable; Short duration 30–45 sec.
- [ ] Hard-fail placeholder/missing paths.
- [ ] Verify and commit `feat: add deterministic production quality gate`.

---

### Task 3: Validate layout metadata before render

**Files:**
- Create: `app/quality/layout.py`
- Test: `tests/test_layout_quality.py`

**Interfaces:**
- `validate_scene_layout_metadata(scene_plan, channel_id) -> tuple[QualityIssue, ...]`.

- [ ] Write tests rejecting empty headlines on scene types that require them, repeated identical layout type beyond configurable threshold, invalid asset ids, and captions outside normalized safe coordinates when explicit positions exist.
- [ ] Verify RED.
- [ ] Implement metadata-level checks independent of rendered pixels.
- [ ] Verify and commit `feat: validate scene layout plans`.

---

### Task 4: Add contact-sheet generation and optional visual critic

**Files:**
- Create: `app/quality/contact_sheet.py`
- Create: `app/quality/visual_critic.py`
- Test: `tests/test_visual_critic.py`

**Interfaces:**
- `build_contact_sheet(video, out, sample_count=12) -> Path`.
- `VisualCritique(ok, issues, targeted_changes)`.
- `critique_contact_sheet(channel_id, contact_sheet, thumbnails, llm) -> VisualCritique`.

- [ ] Write contact-sheet command test proving evenly spaced timestamps are generated from probed duration.
- [ ] Write fake-LLM critic test requiring structured JSON and allowed issue codes only (`clutter`, `hierarchy`, `repetition`, `branding`, `thumbnail_legibility`).
- [ ] Verify RED.
- [ ] Implement FFmpeg frame extraction + Pillow grid.
- [ ] Implement optional critic; failure to run critic is nonfatal during supervised rendering, but logged.
- [ ] Ensure critic can request at most one rerender through orchestration state.
- [ ] Verify and commit `feat: add visual contact sheet review`.

---

### Task 5: Add renderer approval state and live safety lock

**Files:**
- Modify: `app/storage/sqlite.py`
- Modify: `app/cli.py`
- Test: `tests/test_renderer_approval.py`

**Interfaces:**
- Repository settings table/key-value helpers.
- CLI commands: `autotube renderer-status`, `autotube approve-renderer professional`.

- [ ] Write tests that fresh repo reports professional renderer unapproved.
- [ ] Write test `run-daily --live` with professional renderer selected refuses before publisher calls if approval is false.
- [ ] Verify RED.
- [ ] Add `settings(key TEXT PRIMARY KEY, value TEXT, updated_at TEXT)`.
- [ ] Implement explicit approval command; no automatic approval from successful tests.
- [ ] Verify and commit `feat: gate live publishing on renderer approval`.

---

### Task 6: Add workstation media smoke command

**Files:**
- Create: `app/health/media.py`
- Modify: `app/cli.py`
- Test: `tests/test_media_smoke.py`

**Interfaces:**
- CLI: `autotube media-smoke`.
- Output includes: Ollama model availability, Node/npm, Remotion install, FFmpeg, FFprobe, NVENC capability, Chatterbox import/load probe, Kokoro fallback availability, faster-whisper availability, tiny render status.

- [ ] Write dependency-check tests using monkeypatched `shutil.which`/subprocess.
- [ ] Verify RED.
- [ ] Implement lightweight checks first; actual CUDA model load/render is performed sequentially and reports each stage clearly.
- [ ] Tiny render uses a fixed 5–10 second fixture package, not live sources.
- [ ] Verify and commit `feat: add professional media workstation smoke test`.

---

### Task 7: Build fixed internal sample stories/fixtures

**Files:**
- Create: `tests/fixtures/media/kernelrush_story.json`
- Create: `tests/fixtures/media/lobbysignal_story.json`
- Create: `scripts/render_samples.ps1`
- Test: `tests/test_media_fixtures.py`

**Interfaces:**
- Sample stories contain only synthetic/non-current facts and locally generated visual data, designed to exercise stat, chart, timeline, source-like card, comparison, captions, music hooks, and fallback scene paths.

- [ ] Write tests that fixture scene plans cover the required scene families and contain no remote URLs.
- [ ] Verify RED until fixtures exist.
- [ ] Add fixtures + script that renders both long and Short outputs into `output/samples/`.
- [ ] Commit `test: add professional media sample stories`.

---

### Task 8: Refactor daily orchestration into production stages

**Files:**
- Create: `app/orchestration/production.py`
- Modify: `app/orchestration/daily.py`
- Test: `tests/test_production_orchestration.py`

**Interfaces:**
- `produce_episode(...) -> ProductionResult` executes editorial → assets → narration → captions → audio → render → thumbnails → QA.
- `run_channel` retains selection/research/job/publishing responsibility and delegates production.

- [ ] Write failing stage-order test using fake stage functions; expected exact order is `editorial, assets, narration, captions, audio, render, thumbnails, qa`.
- [ ] Write failure test proving a QA failure stops before publisher invocation.
- [ ] Verify RED.
- [ ] Move production responsibilities out of `daily.py` without changing candidate selection, job locks, analytics refresh, or publication recording.
- [ ] Keep legacy production adapter available.
- [ ] Verify full suite; commit `refactor: isolate professional production orchestration`.

---

### Task 9: Wire validated professional output into private-first publisher

**Files:**
- Modify: `app/orchestration/daily.py`
- Modify: `app/publishing/youtube.py` only if needed for explicit metadata/source description support.
- Test: `tests/test_professional_publish_gate.py`

**Interfaces:**
- Publisher receives only `ProductionResult.long_video` and chosen thumbnail after `quality_report.ok is True` and renderer approval is true.

- [ ] Write fake publisher test proving valid approved output stages; failed QA never stages.
- [ ] Add metadata description with source URLs from the research packet instead of saying merely “sources are listed in research packet.”
- [ ] Verify tests.
- [ ] Commit `feat: publish only validated professional outputs`.

---

### Task 10: Update setup/docs and supervised rollout controls

**Files:**
- Modify: `scripts/setup_windows.ps1`
- Modify: `scripts/install_task.ps1`
- Modify: `README.md`
- Modify: `.env.example`
- Test: `tests/test_config_defaults.py`

**Interfaces:**
- New documented envs: `AUTOTUBE_RENDERER`, `AUTOTUBE_TTS_BACKEND`, `AUTOTUBE_LLM_MODEL`, caption model/config, audio library path.

- [ ] Write config-default tests first.
- [ ] Setup verifies Python, FFmpeg/FFprobe, Ollama, Node/npm and installs Python media extras + `npm ci`; it does not download large model weights without explicit user-facing command/output.
- [ ] Keep scheduled task as `run-daily --render` through supervised rollout; never auto-switch scheduler to `--live`.
- [ ] README documents Stage A–E rollout and renderer approval command.
- [ ] Run all Python/Node checks and commit `docs: document professional media rollout`.

---

### Task 11: Final branch verification before supervised sample rendering

**Files:**
- No production changes unless verification reveals a defect.

- [ ] Run `pytest -q`.
- [ ] Run `python -m compileall -q app`.
- [ ] Run `ruff check app tests`.
- [ ] Run `cd video && npm test`.
- [ ] Run `cd video && npx tsc --noEmit`.
- [ ] Run CI-safe renderer smoke test.
- [ ] On the Windows workstation run `autotube media-smoke`.
- [ ] Run `scripts/render_samples.ps1` and manually review KernelRush + LobbySignal long/Short/thumbnail outputs.
- [ ] Do **not** approve renderer until that supervised review is acceptable.
- [ ] After approval, run one real KernelRush + LobbySignal render without upload; then 3–7 supervised daily renders before enabling live publishing.

## Phase Exit Criteria

- Hard QA blocks malformed media before upload.
- Professional renderer has explicit persistent approval state.
- Contact-sheet critique exists but cannot override hard validation.
- Daily orchestrator is decomposed and testable.
- Source URLs are included in publish metadata.
- Workstation smoke command exercises the local stack sequentially.
- Scheduler remains render-only until supervised rollout is complete.
- Full Python + Node CI passes.
