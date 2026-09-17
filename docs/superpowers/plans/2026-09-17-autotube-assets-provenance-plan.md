# AutoTube Assets + Provenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a safe asset pipeline that resolves first-party/source visuals, controlled screenshots, and original fallback graphics while recording provenance for every external asset.

**Architecture:** Scene plans request abstract asset needs. Python resolves them through typed adapters and writes `asset-manifest.json`; Playwright captures source-page screenshots only when a scene references a research URL. Missing assets degrade to deterministic fallback scenes rather than blocking the whole episode unless the scene explicitly requires a source visual.

**Tech Stack:** Python 3.11+, Playwright, Pillow, hashlib, pytest.

**Spec:** `docs/superpowers/specs/2026-09-17-autotube-professional-media-engine-design.md`

## Global Constraints

- No automatic downloading of third-party creator footage from YouTube/TikTok/Instagram/Twitch.
- Every external visual must retain source URL and provenance metadata.
- Source screenshots must originate from URLs already present in the verified research packet.
- Missing noncritical assets fall back to branded original visuals.
- No secrets, browser profiles, downloaded media caches, or copyrighted bundled clips are committed.

---

### Task 1: Define asset records and manifest persistence

**Files:**
- Create: `app/assets/__init__.py`
- Create: `app/assets/models.py`
- Create: `app/assets/manifest.py`
- Test: `tests/test_asset_manifest.py`

**Interfaces:**
- Produces: `AssetRecord`, `AssetManifest`, `write_asset_manifest(records, out) -> Path`.

- [ ] Write failing tests proving ids are unique, SHA-256 is stored, source URL is preserved, and manifest JSON round-trips.
- [ ] Run `pytest tests/test_asset_manifest.py -v`; expect RED.
- [ ] Implement frozen dataclasses with fields: `id`, `kind`, `local_path`, `source_url`, `source_name`, `usage`, `license_note`, `sha256`, `captured_at`.
- [ ] Implement `sha256_file(path: Path) -> str` and JSON writer using UTF-8 + indent 2.
- [ ] Run focused tests and full suite; commit `feat: add asset provenance manifest`.

---

### Task 2: Resolve research source references into asset requests

**Files:**
- Create: `app/assets/resolver.py`
- Test: `tests/test_asset_resolver.py`

**Interfaces:**
- Produces: `resolve_scene_assets(scene_plan, packet) -> tuple[AssetRequest, ...]`.
- `AssetRequest` includes `id`, `kind`, `source_url`, `source_name`, `purpose`, `required`.

- [ ] Write tests that a `source_browser` scene can reference only URLs present in `packet['sources']` and an unknown URL raises `AssetResolutionError`.
- [ ] Add a test that scenes with no external asset need produce no requests.
- [ ] Verify RED.
- [ ] Implement URL index from research packet and deterministic ids `source-{n}`.
- [ ] Run tests + Ruff; commit `feat: resolve scene assets from verified sources`.

---

### Task 3: Add controlled Playwright screenshot capture

**Files:**
- Create: `app/assets/screenshots.py`
- Modify: `pyproject.toml`
- Modify: `scripts/setup_windows.ps1`
- Test: `tests/test_screenshot_capture.py`

**Interfaces:**
- Produces: `ScreenshotCapture.capture(request: AssetRequest, out_dir: Path) -> AssetRecord`.

- [ ] Write tests around a fake page/browser object proving the capture uses the exact request URL, fixed viewport `1440x900`, waits for DOM content, and writes one PNG.
- [ ] Verify RED.
- [ ] Add optional dependency group `media = ["playwright>=1.55"]` and setup command `python -m playwright install chromium`.
- [ ] Implement dependency-injectable browser factory so unit tests never need real Chromium.
- [ ] Capture full viewport only; do not attempt login-gated pages or cookie bypasses.
- [ ] Store capture timestamp and hash in `AssetRecord`.
- [ ] Run tests; commit `feat: add source screenshot capture`.

---

### Task 4: Add original fallback visual asset generation

**Files:**
- Create: `app/assets/fallbacks.py`
- Test: `tests/test_asset_fallbacks.py`

**Interfaces:**
- Produces: `render_fallback_card(channel_cfg: dict, scene, out: Path) -> AssetRecord`.

- [ ] Write tests for 1920x1080 dimensions, channel color use, and local-only provenance (`source_url=None`).
- [ ] Verify RED.
- [ ] Implement Pillow-based branded card with headline, purpose label, and safe margins.
- [ ] Verify GREEN and commit `feat: add branded fallback scene assets`.

---

### Task 5: Build the per-episode asset preparation service

**Files:**
- Create: `app/assets/service.py`
- Test: `tests/test_asset_service.py`

**Interfaces:**
- Produces: `prepare_assets(scene_plan, packet, channel_cfg, episode_dir, capturer) -> AssetManifest`.

- [ ] Write test with two source scenes and one fallback scene; fake capturer succeeds once and raises once. Assert failed optional capture becomes fallback and all final records exist.
- [ ] Add required-asset case where capture failure raises `AssetPreparationError`.
- [ ] Verify RED.
- [ ] Implement request resolution, capture/fallback logic, deduplication by URL+purpose, manifest write.
- [ ] Verify full suite and commit `feat: prepare episode assets with provenance`.

---

### Task 6: Wire assets into dry/render preparation artifacts

**Files:**
- Modify: `app/orchestration/editorial.py`
- Modify: `app/orchestration/daily.py`
- Test: `tests/test_professional_asset_flow.py`

**Interfaces:**
- `prepare_editorial(...)` or a new higher-level `prepare_episode_blueprint(...)` now returns editorial bundle, scene plan, and asset manifest path.

- [ ] Write failing integration test asserting episode directory contains `asset-manifest.json` and referenced local PNGs before rendering.
- [ ] Verify RED.
- [ ] Implement integration without touching publisher behavior.
- [ ] Run `pytest -q && python -m compileall -q app && ruff check app tests`.
- [ ] Commit `feat: attach verified assets to episode blueprints`.

## Phase Exit Criteria

- Every external visual is traceable to a verified research URL.
- Playwright capture is deterministic and testable without network in CI.
- Missing optional visuals fall back cleanly.
- No creator-video scraping exists.
- Dry/render preparation emits `asset-manifest.json`.
- Full CI is green.
