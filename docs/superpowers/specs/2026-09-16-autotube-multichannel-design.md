# AutoTube Lab — Multichannel Autonomous YouTube System

Date: 2026-09-16
Status: Approved architecture

## Objective

Build a professional, zero/near-zero-cost autonomous YouTube publishing system that operates two coherent faceless channels, tests five adjacent content niches, learns from performance, and reallocates future uploads toward the strongest niches while preserving channel identity.

Primary V1 goal: publish one long-form video per channel per day, optionally derive one Short per long-form video, and collect enough analytics to score niches after each video's 7-day maturation window.

## Channel strategy

### KernelRush — Tech Intelligence
- AI / software launches
- Open-source / GitHub radar
- Consumer tech / apps / platform updates

Audience: developers, students, power users, AI/software enthusiasts.

### LobbySignal — Gaming + Internet Culture
- Gaming news / player trends / releases
- Meme and internet-culture explainers

Audience: gamers and online-culture viewers.

## Experiment design

### Phase 1 — Controlled exploration
Duration: 45 days.

- KernelRush: one 4–7 minute long-form video daily, three niches rotated evenly.
- LobbySignal: one 4–7 minute long-form video daily, two niches alternated evenly.
- Optional: one 30–45 second Short extracted from each long-form video when quality passes.

### Phase 2 — Adaptive allocation
After each video is at least 7 days old, calculate a normalized score:
- 30% retention
- 25% views normalized against channel median for the same age
- 20% CTR when available
- 15% subscribers gained per 1,000 views
- 10% watch time per 1,000 impressions or closest supported equivalent

Each niche keeps a 10–15% exploration floor until sufficient mature samples exist. No niche exceeds 80% allocation during experimentation.

## Architecture

Modules:
1. collectors
2. normalizer / canonical story model
3. deduplication
4. trend scoring
5. research packet builder
6. script engine
7. fact validator
8. visual planner
9. narration engine
10. renderer
11. thumbnail engine
12. metadata engine
13. YouTube publisher
14. analytics ingestor
15. experiment engine
16. orchestrator
17. operator health report

## Data sources

KernelRush uses GitHub, Hacker News, Hugging Face Hub, and primary vendor/RSS feeds.

LobbySignal uses Steam/game publisher feeds and public trend/community discovery sources, with secondary corroboration before a story can ship.

No automated copyrighted clip harvesting is part of V1.

## Story selection

Hard filters:
- not recently covered
- not a semantic duplicate
- primary claim verifiable
- enough source material for an original 4–7 minute treatment
- no prohibited/unsafe topic category
- can be visualized without unlicensed third-party footage

Ranking combines freshness, velocity, source credibility, niche relevance, novelty, visual quality, and—once sample size is sufficient—historical performance.

## Script standard

Target: roughly 650–1,000 spoken words.

Structure:
1. 5–15 second hook grounded in the strongest factual signal
2. immediate context
3. 3–5 structured sections
4. “Why it matters” interpretation based on sourced facts
5. concise close

Publication is blocked when dates materially disagree, numbers cannot be traced, named entities are ambiguous, source confidence is too low, or causal claims are unsupported.

## Visual identity

Shared production:
- 1920×1080 long-form
- clean motion graphics
- typography-driven cards
- animated charts/counters
- restrained transitions
- consistent sonic branding

KernelRush uses a premium tech-intelligence-terminal visual language. LobbySignal uses a higher-energy gaming/editorial language.

## Narration and rendering

Use local/free TTS first. Rendering is deterministic and FFmpeg-based. Generated video is validated before publishing.

## Publishing

Each channel has independent OAuth token storage.

Sequence:
1. upload private
2. attach metadata
3. set custom thumbnail
4. verify processing state
5. schedule/publish only if all checks pass

Idempotency prevents duplicate uploads on retries.

## Analytics and learning

Track views, average percentage viewed, estimated watch minutes, subscriber changes, and reach metrics where available. Store snapshots by video age for fair comparisons.

Never reallocate based on one breakout video; use robust rolling medians and minimum sample requirements.

## Storage

V1 uses SQLite behind a repository layer so PostgreSQL/Supabase can be substituted later.

Core persisted entities include publications, analytics snapshots, niche weights, and job runs.

## Scheduling

Local workstation mode uses Windows Task Scheduler. Lightweight cloud scheduling can be added later, but video rendering remains local for the zero-cost path.

## Reliability principles

- database-backed job locks
- retry only transient failures
- source caching/rate limits
- output validation
- factual confidence threshold
- fail closed on uncertainty
- no stage silently continues after a critical failure

## Cost constraint

Target starting cash cost: ₹0.

Use Python, FFmpeg, SQLite, local/free TTS, free/public APIs, and a local model such as Ollama. Paid services remain optional adapters.

## V1 scope

Included: two channels, five niches, daily autonomous long-form production, optional Shorts, source ingestion, trend selection, script generation, fact/quality gates, TTS, rendering, thumbnails, YouTube staging/upload, analytics ingestion, adaptive allocation, and health reporting.

Deferred: paid generative video, full web dashboard, sponsorship sales, multi-language channels, more than two channels, paywall scraping, copyrighted clip harvesting, and autonomous comment engagement.

## Definition of done

V1 is complete when both channel configs load, at least one collector per niche works, the selector chooses candidates, a branded 1080p test video renders, thumbnail/metadata packages are created, OAuth can stage uploads, analytics can be imported, niche weights update from mature data, failed fact checks prevent publishing, tests pass, and no secrets are committed.

## Rollout

- Week 0: build, dry runs, branding, channel setup, API authorization
- Days 1–7: supervised output review
- Days 8–45: daily autonomous controlled experiment with twice-weekly health checks
- Day 46+: analytics-driven allocation with exploration floors

## Principles

1. Originality beats volume.
2. A missed upload is better than a bad upload.
3. Structured evidence enters before prose generation.
4. Analytics may change allocation, never factual standards.
5. Channel coherence matters more than short-term virality.
6. The zero-cost path is first-class.
7. The reusable asset is the content engine, not a single niche.
