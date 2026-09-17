# AutoTube Remotion Rendering + Shorts + Thumbnails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single-scene Pillow renderer with renderer-neutral packages consumed by distinct KernelRush/LobbySignal Remotion compositions, plus dedicated vertical Shorts and professional thumbnail variants.

**Architecture:** Python prepares a versioned render package containing scenes, captions, audio, assets, theme, and metadata. A separate `video/` Remotion project renders long-form and Short compositions. Python invokes the renderer via a narrow runner interface, then FFprobe validates outputs. The legacy renderer remains available until supervised approval.

**Tech Stack:** Python 3.11+, Node.js LTS, React, Remotion, TypeScript, SVG/CSS, FFmpeg/FFprobe, Pillow, pytest.

**Spec:** `docs/superpowers/specs/2026-09-17-autotube-professional-media-engine-design.md`

## Global Constraints

- Remotion-specific details stay inside `video/` and the Python runner adapter.
- Long-form output: 1920x1080, 30 fps, H.264/AAC.
- Short output: 1080x1920, 30–45 seconds, dedicated vertical composition.
- KernelRush and LobbySignal must look intentionally different.
- No arbitrary model-generated React code; model selects only registered scene types/presets.
- Visual assets must come from the prepared asset manifest.
- Legacy renderer remains callable until rollout is complete.

---

### Task 1: Define versioned render-package writer

**Files:**
- Create: `app/rendering/package.py`
- Test: `tests/test_render_package.py`

**Interfaces:**
- `build_render_package(channel_cfg, title, script, scene_plan, captions, asset_manifest, audio_path, out_dir, *, format='long') -> Path`.

- [ ] Write failing test asserting package contains `manifest.json`, `script.json`, `scenes.json`, `captions.json`, `asset-manifest.json`, and normalized relative asset/audio paths.
- [ ] Verify RED.
- [ ] Implement schema version `1`, width/height/fps metadata, channel theme, duration source, and format (`long`/`short`).
- [ ] Reject paths escaping package root.
- [ ] Run tests; commit `feat: build versioned renderer packages`.

---

### Task 2: Scaffold Remotion project and base composition contract

**Files:**
- Create: `video/package.json`
- Create: `video/tsconfig.json`
- Create: `video/src/index.ts`
- Create: `video/src/Root.tsx`
- Create: `video/src/types.ts`
- Create: `video/src/loadPackage.ts`
- Test: `video/src/loadPackage.test.ts`
- Modify: `.gitignore`

**Interfaces:**
- TypeScript `RenderPackageV1` mirrors Python package fields.
- Composition ids: `KernelRushLong`, `LobbySignalLong`, `KernelRushShort`, `LobbySignalShort`.

- [ ] Write failing package-loader test against a fixture JSON.
- [ ] Install pinned Remotion/React/TypeScript dev dependencies and lockfile.
- [ ] Implement loader and composition registration.
- [ ] Ignore `video/node_modules`, `.remotion`, render temp files.
- [ ] Run `npm test` and `npx tsc --noEmit`; commit `feat: scaffold Remotion render project`.

---

### Task 3: Build shared visual primitives and safe-layout system

**Files:**
- Create: `video/src/components/SafeFrame.tsx`
- Create: `video/src/components/Typography.tsx`
- Create: `video/src/components/SourceBadge.tsx`
- Create: `video/src/components/BrowserFrame.tsx`
- Create: `video/src/components/Stat.tsx`
- Create: `video/src/components/Chart.tsx`
- Create: `video/src/components/Timeline.tsx`
- Create: `video/src/components/CaptionTrack.tsx`
- Create: `video/src/motion.ts`
- Test: `video/src/components/components.test.tsx`

**Interfaces:**
- Components take only data from `RenderPackageV1`/scene payloads.

- [ ] Write tests for safe margins, deterministic text wrapping helpers, allowed transition lookup, and caption active-range calculation.
- [ ] Verify RED.
- [ ] Implement primitives using CSS/SVG and Remotion interpolation/springs with clamped ranges.
- [ ] No runtime web requests from components.
- [ ] Run TS tests/typecheck; commit `feat: add reusable motion design primitives`.

---

### Task 4: Implement registered scene renderer

**Files:**
- Create: `video/src/scenes/SceneRenderer.tsx`
- Create scene components for `HookScene`, `HeadlineScene`, `SourceBrowserScene`, `DeviceScene`, `GithubScene`, `GameStoreScene`, `StatScene`, `ChartScene`, `TimelineScene`, `ComparisonScene`, `QuoteScene`, `ListScene`, `ProcessScene`, `CodeScene`, `MapScene`, `SocialContextScene`, `ChapterScene`, `ConclusionScene`, `FallbackEditorialScene`.
- Test: `video/src/scenes/sceneRegistry.test.ts`

**Interfaces:**
- `SceneRenderer({scene, theme, assets})` maps every Python `SCENE_TYPES` value to exactly one registered component.

- [ ] Write registry parity test listing the exact Python scene vocabulary mirrored in TS; fail if any is missing.
- [ ] Verify RED.
- [ ] Implement each registered component with sensible fallback data behavior; no component may throw solely because optional subfields are absent.
- [ ] Unknown type still throws before render to expose schema drift.
- [ ] Run tests/typecheck; commit `feat: implement professional scene registry`.

---

### Task 5: Implement distinct KernelRush and LobbySignal themes/compositions

**Files:**
- Create: `video/src/themes/kernelrush.ts`
- Create: `video/src/themes/lobbysignal.ts`
- Create: `video/src/compositions/KernelRushLong.tsx`
- Create: `video/src/compositions/LobbySignalLong.tsx`
- Test: `video/src/themes/themes.test.ts`

**Interfaces:**
- Theme fields: background, foreground, accent, secondary, type scale, spacing, transition family, caption style, motion intensity.

- [ ] Write tests asserting theme ids/palettes/motion intensities differ and composition selects proper theme.
- [ ] Verify RED.
- [ ] Implement premium restrained KernelRush theme and faster energetic LobbySignal theme.
- [ ] Use scene durations derived from aligned narration/cue metadata; no fixed arbitrary total duration.
- [ ] Run tests/typecheck; commit `feat: add distinct long form channel compositions`.

---

### Task 6: Add Python Remotion runner and smoke render

**Files:**
- Create: `app/rendering/runner.py`
- Modify: `pyproject.toml`
- Modify: `scripts/setup_windows.ps1`
- Test: `tests/test_remotion_runner.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- `RemotionRunner.render(package_dir: Path, composition: str, out: Path) -> Path`.
- `RemotionRunner.command(...) -> list[str]` independently testable.

- [ ] Write command test asserting package path/composition/output are passed and shell=False semantics are preserved.
- [ ] Verify RED.
- [ ] Implement runner around `npx remotion render` with structured logs captured in episode dir on failure.
- [ ] Setup script checks/installs Node dependencies with `npm ci` inside `video/`.
- [ ] CI installs Node and runs `npm ci`, TypeScript tests/typecheck; include a minimal 1-second Remotion smoke render only if runtime stays practical.
- [ ] Run full Python + Node verification; commit `feat: render packages through Remotion`.

---

### Task 7: Build dedicated Short story/script/scene flow

**Files:**
- Create: `app/planning/shorts.py`
- Create: `app/shorts/__init__.py`
- Create: `app/shorts/pipeline.py`
- Test: `tests/test_shorts_pipeline.py`

**Interfaces:**
- `build_short_script(packet, long_script, llm) -> str`.
- `plan_short_scenes(channel_id, short_script, packet, llm) -> ScenePlan` where `format='short'`.

- [ ] Write tests that Short script uses only facts from packet, has bounded word count target, and scene plan format is `short` with 5–12 scenes.
- [ ] Verify RED.
- [ ] Implement dedicated prompts; do not crop/reuse long scene plan.
- [ ] Re-run `validate_script(short_script, packet)` before rendering.
- [ ] Commit `feat: create dedicated vertical Short stories`.

---

### Task 8: Implement vertical Remotion compositions

**Files:**
- Create: `video/src/compositions/KernelRushShort.tsx`
- Create: `video/src/compositions/LobbySignalShort.tsx`
- Create: `video/src/components/VerticalSafeFrame.tsx`
- Test: `video/src/compositions/shorts.test.ts`

**Interfaces:**
- Both render 1080x1920 using format-specific safe areas and caption sizes.

- [ ] Write tests for dimensions, safe margins, and correct channel theme.
- [ ] Verify RED.
- [ ] Implement vertical-specific layouts—not CSS-scaled long layouts.
- [ ] Assert output duration from package is within configured 30–45 sec bounds before render.
- [ ] Run tests/typecheck; commit `feat: add native vertical Short compositions`.

---

### Task 9: Replace text-only thumbnails with composition variants

**Files:**
- Create: `app/visuals/thumbnail_v2.py`
- Test: `tests/test_thumbnail_v2.py`

**Interfaces:**
- `render_thumbnail_variants(channel_cfg, title, scene_plan, assets, out_dir, count=5) -> tuple[Path, ...]`.

- [ ] Write tests asserting 3–5 unique 1280x720 images, text maximum roughly five words for generated overlay labels, and distinct layout ids.
- [ ] Verify RED.
- [ ] Implement Pillow compositing templates: `subject`, `stat`, `comparison`, `ui_focus`, `curiosity` using available source assets plus brand graphics.
- [ ] If no suitable source image exists, use strong original graphic layout rather than fabricate an image.
- [ ] Verify and commit `feat: add professional thumbnail variants`.

---

### Task 10: Integrate professional renderer behind a feature flag

**Files:**
- Modify: `app/orchestration/daily.py`
- Create: `app/rendering/pipeline.py`
- Modify: `app/cli.py`
- Test: `tests/test_renderer_selection.py`

**Interfaces:**
- Env/config: `AUTOTUBE_RENDERER=professional|legacy`, default `professional` only after smoke tests pass; during initial merge default may remain `legacy` until supervised approval.
- `render_professional_episode(...) -> ProductionOutputs(long_video, short_video, thumbnails, render_package)`.

- [ ] Write selection/fallback tests before code.
- [ ] Implement professional path without deleting `app/rendering/episode.py`.
- [ ] `--render` generates long + Short when professional renderer selected; optional Short failure is reported but does not invalidate a valid long render.
- [ ] Publisher continues receiving only validated long video + selected supervised thumbnail at this phase.
- [ ] Run Python + Node full suite; commit `feat: integrate professional Remotion renderer`.

## Phase Exit Criteria

- Both channels render genuinely multi-scene 1080p videos with distinct identities.
- Dedicated 9:16 Shorts render without cropping long-form output.
- Renderer consumes only versioned packages.
- 3–5 materially different thumbnails are produced.
- Legacy renderer is still available for rollback.
- Python and Node CI are green.
