# AutoTube Lab

Autonomous, fail-closed YouTube production engine for two faceless channels:

- **KernelRush** (`@KernelRushHQ`) — AI/software, open-source/GitHub radar, consumer tech/apps.
- **LobbySignal** — gaming news/player trends and internet-culture explainers.

The first 45 days rotate niches evenly. After videos mature for 7 days, the experiment engine reallocates future uploads using mature analytics while preserving exploration floors.

## Safety / quality philosophy

A missed upload is better than a fabricated one. The live pipeline builds multi-source research packets, blocks unsupported numeric claims, renders original graphics rather than harvesting copyrighted clips, uploads **private first**, waits for YouTube processing, and schedules only a successfully processed video.

## Windows setup

Requirements: Python 3.11+, FFmpeg, Ollama, and a Google Cloud OAuth Desktop client with **YouTube Data API v3** + **YouTube Analytics API** enabled.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_windows.ps1
ollama pull qwen3.5:9b
```

`qwen3.5:9b` is the default local writing model. Override it at any time with the `AUTOTUBE_LLM_MODEL` environment variable; `qwen3:8b` is the recommended lower-VRAM fallback.

Put the OAuth Desktop client JSON at `client_secret.json`. It is gitignored.

### Google OAuth status matters

During initial testing, add your Google account as a test user if the OAuth app is External + Testing. Google currently limits test-user authorizations (including refresh tokens for these YouTube scopes) to 7 days. For this personal-use project, move the OAuth app to **In Production** after the setup works so unattended authorization does not expire every week. OAuth publishing/verification is separate from the YouTube Data API upload audit.

Authorize each YouTube channel independently:

```powershell
.\.venv\Scripts\autotube.exe youtube-auth kernelrush
.\.venv\Scripts\autotube.exe youtube-auth lobbysignal
```

The command checks the authorized YouTube channel title. If you select the wrong channel identity, its token is deleted instead of silently publishing to the wrong account.

## Test before publishing

```powershell
.\.venv\Scripts\autotube.exe run-daily
.\.venv\Scripts\autotube.exe run-daily --render
.\.venv\Scripts\autotube.exe health
```

Dry, render and live executions use separate daily idempotency keys, so you can safely do all three during supervised setup without duplicate runs inside the same mode.

## Live mode

Only after reviewing rendered output:

```powershell
.\.venv\Scripts\autotube.exe run-daily --live
```

A live run first refreshes mature YouTube analytics and niche weights, then chooses that day's niche. It uploads the new video private, sets the thumbnail, polls YouTube processing, and schedules it only if processing succeeds.

You can manually refresh learning at any time:

```powershell
.\.venv\Scripts\autotube.exe refresh-youtube-analytics kernelrush
.\.venv\Scripts\autotube.exe refresh-youtube-analytics lobbysignal
```

## YouTube API upload restriction

YouTube currently restricts videos uploaded by unverified API projects created after July 28, 2020 to **private** until the API project passes its YouTube API Services compliance audit. This is separate from OAuth consent-screen publishing. AutoTube deliberately remains private-first either way.

## Automation

After the first supervised week:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_task.ps1
```

The supplied task currently runs **`run-daily --render`**, not `--live`, at 18:00 with `StartWhenAvailable`. That is deliberate for the supervised rollout. After you trust seven days of outputs, edit the Task Scheduler action to `run-daily --live` for unattended publishing.

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

The direct Analytics adapter currently collects the supported watch/view/subscriber metrics and safely renormalizes the score when reach metrics such as impressions/CTR are unavailable. Each niche retains an exploration floor and no niche can exceed 80% allocation during experimentation.

## Important

This system automates production and experimentation; it does **not** guarantee views, monetization, or income. During days 1–7, inspect every rendered video before enabling unattended live publishing. YouTube monetization still depends on originality, viewer value, and current YouTube Partner Program policies.
