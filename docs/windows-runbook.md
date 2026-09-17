# AutoTube Lab — Windows Runbook

This is the end-to-end operator path for the professional renderer on a Windows NVIDIA workstation. Keep publishing supervised until the final rollout stage.

## 1. Prerequisites

Install and put these on `PATH` before running project setup:

- Python 3.11+ (Python 3.12 is the CI-tested version)
- Node.js 22 + npm
- FFmpeg + FFprobe
- Ollama
- Git
- A current NVIDIA driver for the local CUDA-capable GPU

A Google OAuth Desktop client is **not needed for render-only setup or testing**. It is only needed later for YouTube authorization/live publishing.

From PowerShell, verify the core commands:

```powershell
python --version
node --version
npm --version
ffmpeg -version
ffprobe -version
ollama --version
git --version
```

## 2. Get the latest main branch

Fresh clone:

```powershell
git clone https://github.com/kanhaal/autotube-lab.git
cd autotube-lab
git checkout main
git pull
```

Existing clone:

```powershell
cd C:\path\to\autotube-lab
git checkout main
git pull
```

All commands below assume PowerShell is open at the repository root.

## 3. Install the project

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1
ollama pull qwen3.5:9b
```

The setup script:

- creates `.venv`
- installs the Python project with the YouTube, media, and voice extras
- installs Playwright Chromium
- installs the locked Remotion/Node dependencies with `npm ci`
- initializes the local SQLite database

The setup script intentionally does not download all large local model weights. Chatterbox/faster-whisper may download/cache model data the first time their deep checks or render path loads them.

## 4. Configure the current PowerShell session

`.env.example` is a reference file; AutoTube does **not** automatically load it as a dotenv file. Set environment variables in the shell you will use, or pass explicit CLI flags where available.

Recommended professional defaults:

```powershell
$env:AUTOTUBE_RENDERER="professional"
$env:AUTOTUBE_TTS_BACKEND="chatterbox"
$env:AUTOTUBE_LLM_MODEL="qwen3.5:9b"
$env:AUTOTUBE_CAPTION_MODEL="small.en"
$env:AUTOTUBE_CAPTION_DEVICE="cuda"
$env:AUTOTUBE_CAPTION_COMPUTE_TYPE="float16"
$env:AUTOTUBE_AUDIO_LIBRARY="config/audio/library.yml"
$env:AUTOTUBE_VISUAL_CRITIC="0"
```

For important render commands, still pass `--renderer professional` explicitly. That makes the intended renderer unambiguous even in a new shell.

## 5. Optional local music/SFX library

The core pipeline works without a music library and safely falls back to narration-only audio if no matching local asset exists.

To configure local, owned/properly licensed audio:

```powershell
Copy-Item config\audio\library.example.yml config\audio\library.yml
notepad config\audio\library.yml
```

Replace the example file paths with real local WAV files and keep accurate license/source metadata. Do not use tracks you do not have permission to use.

## 6. Run health checks before rendering

Start Ollama if it is not already running, then verify the model:

```powershell
ollama list
```

Run AutoTube health checks:

```powershell
.\.venv\Scripts\autotube.exe health
.\.venv\Scripts\autotube.exe media-smoke
.\.venv\Scripts\autotube.exe media-smoke --deep
.\.venv\Scripts\autotube.exe renderer-status
```

Expected before approval:

- Ollama model is available
- FFmpeg/FFprobe are available
- Node/npm/Remotion are available
- Chatterbox, Kokoro, and faster-whisper are importable
- deep smoke can load/release Chatterbox, then load/release faster-whisper, then complete the fixed tiny Remotion render
- `professional` renderer reports `approved: false`

The model-heavy checks are deliberately sequential to fit a 6 GB-class GPU more safely.

## 7. Render the two synthetic acceptance samples

```powershell
powershell -ExecutionPolicy Bypass -File scripts\render_samples.ps1
```

The script uses `.venv\Scripts\python.exe` directly, so activating the venv first is not required.

Review both:

```text
output\samples\kernelrush\
output\samples\lobbysignal\
```

For each channel inspect:

- `long.mp4` — 1920x1080 long-form render
- `short.mp4` — native 1080x1920 Short
- `thumbnails\` — all five thumbnail variants
- `long-narration.wav` and `short-narration.wav` — confirm they are distinct and correct
- `long-master.wav` and `short-master.wav`
- source/fallback cards and render packages
- captions and timing
- `sample-result.json`

Acceptance checklist:

- no blank/black source scenes
- source-browser/fallback scenes show the correct visual
- captions are readable, synchronized, and inside safe areas
- Short framing is genuinely vertical rather than a cropped long-form layout
- long and Short narration are not overwritten or mixed up
- transitions/motion do not obscure text
- audio is clean and speech is intelligible
- five thumbnails are legible at small size
- no hard QA issue is being bypassed

Do **not** approve the professional renderer if these outputs are not acceptable.

## 8. Approve the professional renderer only after sample acceptance

```powershell
.\.venv\Scripts\autotube.exe approve-renderer professional
.\.venv\Scripts\autotube.exe renderer-status
```

Expected afterward:

```text
professional: approved = true
```

Approval only unlocks the live-publish safety gate. It does not upload anything and does not change the scheduler to live mode.

## 9. Render one real episode for each channel — no upload

```powershell
.\.venv\Scripts\autotube.exe run-daily --channel kernelrush --render --renderer professional
.\.venv\Scripts\autotube.exe run-daily --channel lobbysignal --render --renderer professional
```

Inspect the newly created dated episode folders under `output\`. Review:

- `research.json` and the actual verified source URLs
- `script.txt`
- `editorial.json` / `scenes.json`
- `asset-manifest.json` and captured source screenshots
- long video
- native Short when generated
- long/Short narration and mastered audio
- caption artifacts/render packages
- five thumbnail variants
- any recorded optional Short/visual-critic issue

A hard fact/layout/media QA failure is supposed to block publication. Fix the cause rather than bypassing the gate.

### Same-day `duplicate` result

Daily executions are idempotent by date/channel/mode. If you intentionally need a clean test rerun on the same day, use a separate database. The global `--db` option goes **before** the subcommand:

```powershell
.\.venv\Scripts\autotube.exe --db data\autotube-test.db run-daily --channel kernelrush --render --renderer professional
```

Renderer approval is stored per database. An alternate test DB therefore has its own approval state, which is useful for isolated testing.

## 10. Run 3–7 supervised render-only days

After the real one-off renders look correct, install the supplied Windows scheduled task:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_task.ps1
```

The task runs daily at 18:00 with `StartWhenAvailable` and explicitly executes:

```text
run-daily --render --renderer professional
```

It does **not** use `--live`. Inspect the generated KernelRush and LobbySignal outputs each day for 3–7 days before considering unattended publishing.

## 11. Optional advisory visual critic

The visual critic is off by default:

```powershell
$env:AUTOTUBE_VISUAL_CRITIC="0"
```

To enable the local contact-sheet/thumbnail critique for a supervised render:

```powershell
$env:AUTOTUBE_VISUAL_CRITIC="1"
.\.venv\Scripts\autotube.exe run-daily --channel kernelrush --render --renderer professional
```

It is advisory. Deterministic QA remains authoritative. The normal CLI path does not supply an automatic visual corrector, so critique findings do not silently rewrite/rerender the episode by default.

Turn it back off with:

```powershell
$env:AUTOTUBE_VISUAL_CRITIC="0"
```

## 12. Set up YouTube OAuth only when render quality is accepted

Place your Google OAuth Desktop client file at:

```text
client_secret.json
```

Then authorize each channel separately:

```powershell
.\.venv\Scripts\autotube.exe youtube-auth kernelrush
.\.venv\Scripts\autotube.exe youtube-auth lobbysignal
```

The authorization command validates the selected YouTube channel identity. If the wrong channel is selected, AutoTube deletes that token instead of silently retaining it.

## 13. Supervised live run — manual command only

Only after the sample review, real render review, explicit renderer approval, and several supervised render-only days:

```powershell
.\.venv\Scripts\autotube.exe run-daily --channel kernelrush --live --renderer professional
.\.venv\Scripts\autotube.exe run-daily --channel lobbysignal --live --renderer professional
```

The publishing path remains private-first and is still protected by the renderer-approval and deterministic-QA gates.

Do not change the scheduled task to `--live` as part of initial setup. Treat unattended publishing as a separate rollout decision after real outputs have proven stable.

## 14. Common problems

### `renderer_unapproved`

Expected before explicit approval. Review the synthetic samples first, then run:

```powershell
.\.venv\Scripts\autotube.exe approve-renderer professional
```

### `duplicate`

The same date/channel/mode has already been claimed in that SQLite database. Use a separate test DB for deliberate same-day testing instead of deleting production history.

### Ollama/model missing

```powershell
ollama list
ollama pull qwen3.5:9b
```

Make sure the Ollama service/application is running.

### CUDA/VRAM problem during faster-whisper

First run the deep smoke. For a slower diagnostic/fallback path, move caption transcription to CPU:

```powershell
$env:AUTOTUBE_CAPTION_DEVICE="cpu"
$env:AUTOTUBE_CAPTION_COMPUTE_TYPE="int8"
.\.venv\Scripts\autotube.exe media-smoke --deep
```

Restore CUDA later with:

```powershell
$env:AUTOTUBE_CAPTION_DEVICE="cuda"
$env:AUTOTUBE_CAPTION_COMPUTE_TYPE="float16"
```

### Chatterbox synthesis failure

The configured production TTS path has Kokoro as its fallback. Use `media-smoke --deep` to distinguish installation/model-load problems from episode-specific generation problems.

### Playwright/Chromium missing

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

### Node/Remotion dependencies broken

```powershell
Push-Location video
npm ci
Pop-Location
```

### No background music

This is not necessarily a render failure. If `config\audio\library.yml` is absent or contains no existing matching local audio asset, the production mixer safely uses narration-only audio.

### `blocked_factcheck` or `blocked_quality`

These are fail-closed safety results. Inspect the recorded reason/artifacts and correct the research, scene, asset, caption, audio, or render issue. Do not bypass the gate for live publishing.
