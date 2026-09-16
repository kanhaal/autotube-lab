# AutoTube Lab

Autonomous, fail-closed YouTube production engine for two faceless channels:

- **KernelRush** (`@KernelRushHQ`) — AI/software, open-source/GitHub radar, consumer tech/apps.
- **LobbySignal** — gaming news/player trends and internet-culture explainers.

The first 45 days rotate niches evenly. After videos mature for 7 days, the experiment engine reallocates future uploads using robust niche scores while preserving exploration floors.

## Safety/quality philosophy

A missed upload is better than a fabricated one. Live generation uses multiple-source research packets, blocks unsupported numeric claims, stages uploads **private first**, and only schedules a video after YouTube processing succeeds. No copyrighted clip harvesting is used.

## Windows setup

Requirements: Python 3.11+, FFmpeg, Ollama, and a Google Cloud OAuth Desktop client with YouTube Data API v3 + YouTube Analytics API enabled.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_windows.ps1
ollama pull qwen2.5:7b-instruct
```

Put your downloaded OAuth Desktop client JSON at `client_secret.json`. It is gitignored.

Authorize **each channel separately**. When Google asks which YouTube identity/channel to use, select the matching channel:

```powershell
.\.venv\Scripts\autotube.exe youtube-auth kernelrush
.\.venv\Scripts\autotube.exe youtube-auth lobbysignal
```

The command verifies the authorized channel title and deletes the token if you accidentally select the wrong identity.

## Test before publishing

```powershell
.\.venv\Scripts\autotube.exe run-daily
.\.venv\Scripts\autotube.exe run-daily --render
.\.venv\Scripts\autotube.exe health
```

## Live mode

Only after reviewing dry-run output:

```powershell
.\.venv\Scripts\autotube.exe run-daily --live
```

Live mode uploads **private first**, checks processing, then schedules only a successful processed upload. New/unverified YouTube API projects can have API uploads restricted to private until Google's API compliance audit is completed.

## Automation

After the first week of supervised output:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_task.ps1
```

The task runs daily at 18:00 and uses `StartWhenAvailable` so a sleeping/off laptop can catch up when it comes back online.

## Experiment

Phase 1: 45 days controlled exploration.

KernelRush: `ai_software → open_source → consumer_tech` rotation.
LobbySignal: `gaming ↔ internet_culture`.

Phase 2 uses 7-day mature-video analytics: 30% retention, 25% views, 20% CTR when available, 15% subscribers/1k views, 10% watch time/1k impressions when available. Missing metrics are renormalized rather than treated as zero. Each niche retains an exploration floor and no niche can exceed 80% allocation.

## Important

This system automates production, not guaranteed revenue. During days 1–7, inspect every generated video before enabling unattended live publishing. YouTube monetization still depends on originality, viewer value, and compliance with current YouTube Partner Program policies.
