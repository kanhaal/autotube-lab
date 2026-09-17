# AutoTube Lab

AutoTube Lab is a local-first, fail-closed YouTube production engine for two faceless channels:

- **KernelRush** (`@KernelRushHQ`) — AI/software, open-source/GitHub radar, consumer tech/apps.
- **LobbySignal** — gaming news/player trends and internet-culture explainers.

The first 45 days rotate niches evenly. After videos mature for 7 days, the experiment engine can reallocate future uploads using mature analytics while preserving exploration floors.

For the complete start-to-live Windows procedure, use **[`docs/windows-runbook.md`](docs/windows-runbook.md)**.

## Safety and quality philosophy

A missed upload is better than a fabricated one. The production path builds multi-source research packets, applies the verified-fact gate, captures source-page visuals with Playwright, renders original graphics, runs deterministic media QA, and keeps YouTube publishing private-first. Failed hard QA never reaches the publisher.

The professional stack stays local/free where practical:

- Qwen 3.5 9B through Ollama for editorial/script/scene planning
- Chatterbox primary TTS with Kokoro fallback
- faster-whisper word-timestamp caption alignment
- Playwright verified-source screenshots/assets
- Remotion + React + TypeScript renderer
- FFmpeg/FFprobe media processing and inspection
- optional local Qwen contact-sheet visual critique
- legacy renderer retained as a fallback path

The professional renderer is **not automatically approved** by tests, CI, a successful render, or setup. Approval is persistent and explicit.

## Windows setup

Render-only requirements: Python 3.11+, FFmpeg + FFprobe, Ollama, and Node.js 22 + npm. A Google Cloud OAuth Desktop client with **YouTube Data API v3** + **YouTube Analytics API** is only required later for YouTube authorization/live publishing.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_windows.ps1
ollama pull qwen3.5:9b
```

`setup_windows.ps1` installs the Python/Node project dependencies and Playwright Chromium, but deliberately does **not** download all large model weights. The default local writing model is `qwen3.5:9b`; override it with `AUTOTUBE_LLM_MODEL` if needed. Chatterbox/faster-whisper may download/cache model data when first loaded locally.

Useful media configuration defaults are documented in `.env.example`:

```text
AUTOTUBE_RENDERER=professional
AUTOTUBE_TTS_BACKEND=chatterbox
AUTOTUBE_LLM_MODEL=qwen3.5:9b
AUTOTUBE_CAPTION_MODEL=small.en
AUTOTUBE_CAPTION_DEVICE=cuda
AUTOTUBE_CAPTION_COMPUTE_TYPE=float16
AUTOTUBE_AUDIO_LIBRARY=config/audio/library.yml
AUTOTUBE_VISUAL_CRITIC=0
```

`.env.example` is documentation only; AutoTube does **not** automatically load it. Set environment variables in PowerShell (for example `$env:AUTOTUBE_CAPTION_DEVICE="cuda"`) or use explicit CLI flags where available. The full recommended PowerShell block is in the Windows runbook.

`AUTOTUBE_VISUAL_CRITIC=0` keeps the optional local visual critic disabled by default. Set it to `1` only when you want the post-QA contact-sheet/thumbnail review; deterministic QA remains authoritative either way.

The local audio library is optional. Copy `config/audio/library.example.yml` to `config/audio/library.yml` and replace the example entries with owned/properly licensed local WAV files if you want music/SFX selection. Missing/nonexistent library assets safely fall back to narration-only audio.

Put the OAuth Desktop client JSON at `client_secret.json` only when you are ready for the publishing stage. It is gitignored.

### Google OAuth status matters

During initial publishing tests, add your Google account as a test user if the OAuth app is External + Testing. For long-running personal use, ensure the OAuth configuration is suitable for persistent authorization before relying on scheduled uploads. OAuth publishing/verification is separate from the YouTube Data API upload audit.

Authorize each YouTube channel independently:

```powershell
.\.venv\Scripts\autotube.exe youtube-auth kernelrush
.\.venv\Scripts\autotube.exe youtube-auth lobbysignal
```

The command checks the authorized YouTube channel title. If the wrong channel identity is selected, the token is deleted instead of silently publishing to the wrong account.

## Media workstation smoke test

Run the lightweight dependency report first:

```powershell
.\.venv\Scripts\autotube.exe media-smoke
```

It reports Ollama model availability, Node/npm, Remotion, FFmpeg, FFprobe, NVENC capability, Chatterbox, Kokoro, and faster-whisper availability.

After local model dependencies are installed, run the sequential deep smoke:

```powershell
.\.venv\Scripts\autotube.exe media-smoke --deep
```

The deep path loads/releases Chatterbox, then loads/releases faster-whisper, then performs a fixed tiny Remotion render. This sequencing reduces overlapping VRAM pressure on 6 GB-class GPUs. It uses local test media, not live sources.

## Supervised professional-renderer rollout

Do not jump from green CI directly to unattended publishing. Use these stages in order.

### Stage A — installation and deterministic checks

```powershell
.\.venv\Scripts\autotube.exe health
.\.venv\Scripts\autotube.exe media-smoke
.\.venv\Scripts\autotube.exe media-smoke --deep
.\.venv\Scripts\autotube.exe renderer-status
```

The expected professional renderer state is initially `approved: false`.

### Stage B — synthetic sample review

Render both fixed, non-current, local-only sample stories:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/render_samples.ps1
```

The sample script uses the project `.venv` directly and sequences TTS and faster-whisper rather than keeping both heavy model stacks resident together. Manually review `output/samples/kernelrush/` and `output/samples/lobbysignal/`, including long-form video, native 9:16 Short, distinct long/Short narration, source/fallback visuals, captions, audio, transitions, and all thumbnail variants. Do not approve the renderer if the output is not acceptable.

### Stage C — explicit renderer approval

Only after Stage B is acceptable:

```powershell
.\.venv\Scripts\autotube.exe approve-renderer professional
.\.venv\Scripts\autotube.exe renderer-status
```

Approval only unlocks the live-publish safety gate. It does not start publishing by itself.

### Stage D — real render-only review

Render one real KernelRush and one real LobbySignal production without upload:

```powershell
.\.venv\Scripts\autotube.exe run-daily --channel kernelrush --render --renderer professional
.\.venv\Scripts\autotube.exe run-daily --channel lobbysignal --render --renderer professional
```

Review the real source screenshots, claims, timing, captions, audio, thumbnails, and QA artifacts manually.

### Stage E — supervised daily operation

Run and inspect **3–7 supervised daily renders** before considering unattended live publishing. Keep the scheduled task render-only throughout this period.

The supplied scheduler explicitly runs:

```text
run-daily --render --renderer professional
```

It never auto-switches to `--live`. Changing that is a separate manual rollout decision after the supervised period.

## Deterministic QA and visual review

Professional production is staged as:

`editorial → assets → narration → captions → audio → render → thumbnails → QA`

Heavy local model ownership is released between stages where AutoTube owns the model instance: the internally created Ollama editorial model is unloaded before narration, TTS backends are released before faster-whisper, and faster-whisper is released before media rendering.

The hard QA gate checks media existence, dimensions, codecs/audio presence, duration consistency, minimum file size, caption artifacts, thumbnails, fact-gate state, and Short duration. Hard failures block publishing.

A contact sheet and optional local Qwen visual critic can flag clutter, hierarchy, repetition, branding, and thumbnail-legibility problems. This critic is advisory: it cannot override deterministic failures. Orchestration supports at most one targeted correction/rerender pass when a caller explicitly supplies a visual corrector; the normal CLI path does not silently auto-correct episodes.

## Publishing safety

`run-daily --live --renderer professional` is blocked until the professional renderer has explicit persistent approval. The same approval check is enforced again at the actual publisher boundary, so callers bypassing the CLI still cannot publish unapproved professional output.

For approved, QA-valid output, YouTube descriptions include the actual verified source URLs from the research packet. Publishing remains private-first: upload private, set the thumbnail, validate processing, and only then schedule when requested.

You can manually refresh learning at any time:

```powershell
.\.venv\Scripts\autotube.exe refresh-youtube-analytics kernelrush
.\.venv\Scripts\autotube.exe refresh-youtube-analytics lobbysignal
```

## Automation

Install the render-only Windows task with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_task.ps1
```

It runs at 18:00 with `StartWhenAvailable` and intentionally uses `run-daily --render --renderer professional`. Do not convert it to unattended `--live` until the supervised rollout above has been completed and the real outputs have been manually accepted.

## Experiment

### Phase 1 — first 45 days

KernelRush: `ai_software → open_source → consumer_tech` rotation.

LobbySignal: `gaming ↔ internet_culture`.

### Phase 2 — adaptive allocation

Videos mature for 7 days before scoring. The target weighting is:

- 30% audience retention
- 25% views relative to the channel's mature median
- 20% CTR when available
- 15% subscribers gained per 1,000 views
- 10% watch time per 1,000 impressions when available

The Analytics adapter safely renormalizes the score when reach metrics such as impressions/CTR are unavailable. Each niche retains an exploration floor and no niche can exceed 80% allocation during experimentation.

## Important

AutoTube Lab automates production and experimentation; it does **not** guarantee views, monetization, or income. Keep the renderer unapproved until the synthetic samples are manually reviewed, then review real KernelRush + LobbySignal renders and several supervised daily runs before enabling unattended live publishing.
