# AutoTube Lab — Professional Media Engine Design

Date: 2026-09-17
Status: Approved design for implementation planning

## Objective

Replace the current proof-of-concept single-scene renderer with a professional, fully automated media-production system for KernelRush and LobbySignal. The production goal is not merely to output a valid MP4; it is to produce videos whose storytelling, pacing, motion design, narration, audio mix, captions, thumbnails, and Shorts feel deliberately edited rather than mechanically assembled.

The system must remain local-first, near-zero-cost, reproducible, auditable, and realistic for a Windows laptop with an RTX 4050 6 GB GPU and 24 GB system RAM. It must preserve the existing fail-closed research/fact-check/publishing philosophy.

## Non-negotiable quality bar

The system is designed toward professional editor standards, while recognizing that fully automatic output cannot be guaranteed to equal an experienced human editor on every story. Quality is created through structured editorial passes, deterministic motion templates, factual visual sourcing, audio mastering, and automated QA rather than one-shot generation.

Every public-ready episode must satisfy all of the following:

- clear factual hook in the opening seconds
- coherent story progression rather than a list of facts
- channel-specific visual identity
- repeated visual changes without chaotic editing
- narration that sounds natural and intentional
- captions synchronized to actual speech
- music/SFX mixed under narration
- meaningful source visuals where relevant
- original charts, timelines, comparisons, counters, cards, and diagrams
- no long stretches of static imagery
- no unsupported AI-generated facts or visual claims
- no automatic harvesting of third-party creator footage
- deterministic render validation before publishing

## Long-term licensing policy

Production models must be usable locally without metered APIs or subscription requirements. Exact model/version identifiers are pinned in configuration, and dependency metadata records the license and upstream source used at the time of adoption.

### Primary editorial model

**Qwen 3.5 9B**

- Role: scriptwriting, hook generation, editorial critique, scene planning, Short scripting, metadata assistance, and optional multimodal visual review.
- Runtime: Ollama.
- Default model identifier: `qwen3.5:9b`.
- License: Apache-2.0 on the official Qwen model release.
- Context target for AutoTube: 4K–8K unless a research packet genuinely requires more. AutoTube does not use the advertised maximum context by default because unnecessary context increases memory pressure.
- Fallback: configurable through `AUTOTUBE_LLM_MODEL`, with `qwen3:8b` documented as a practical lighter fallback.

The editorial model is used in multiple focused passes instead of asking one prompt to research, write, edit, and design simultaneously.

### Primary narration model

**Chatterbox TTS (English production path, with Turbo where validated)**

- Role: production narration.
- License: MIT.
- Model family size: approximately 0.5B.
- Strengths: naturalness, expressive delivery, optional voice conditioning, and paralinguistic controls in the Turbo path.
- Production rule: narration is generated in bounded segments rather than one multi-minute request.
- Voice cloning is optional and must only use audio the operator is authorized to use. The default production path does not require cloning a third party.

### Narration fallback

**Kokoro 82M**

- Role: fast, lightweight fallback when Chatterbox is unavailable or fails quality/reliability checks.
- License: Apache-2.0.
- Benefit: very low resource cost and simple local inference.

### Caption alignment model

**Whisper / faster-whisper**

- Role: align generated narration to word/segment timestamps after TTS so captions follow the spoken audio rather than estimated text timing.
- License: Whisper code and model weights are MIT; faster-whisper is MIT.
- Initial model target: a small English model adequate for clean synthetic narration, configurable later.

### Model lifecycle policy

Models are not automatically upgraded merely because a newer model appears. An upgrade requires:

1. compatible/permissive commercial-use licensing,
2. successful local hardware benchmark,
3. script or voice quality comparison on representative AutoTube samples,
4. regression tests,
5. explicit config/version change.

This prevents a future upstream model or license change from silently changing production behavior.

## Rendering framework policy

### Primary motion engine

**Remotion** is the initial motion-design/compositing layer because it provides a mature programmable video model using React/CSS/SVG and supports real MP4 rendering. Its current free license covers individuals and organizations up to three people with commercial use and automation.

AutoTube must not couple editorial logic directly to Remotion. Python emits a renderer-neutral render package. Remotion consumes that package through a stable interface. This allows a future swap to Motion Canvas or a pure FFmpeg renderer if licensing, team size, or technical needs change.

### Final media tool

**FFmpeg / FFprobe** remain mandatory for:

- final muxing
- audio normalization
- codec inspection
- duration/resolution validation
- loudness measurement
- subtitles where appropriate
- optional GPU encoding
- final file integrity checks

On supported hardware, AutoTube may use NVIDIA NVENC for final H.264 encoding, with `libx264` as the deterministic fallback.

## High-level production flow

```text
candidate + research packet
        ↓
editorial outline
        ↓
3 hook candidates
        ↓
hook selection
        ↓
script draft
        ↓
editorial critic
        ↓
one bounded rewrite
        ↓
fact validation
        ↓
scene planner
        ↓
asset resolver
        ↓
Chatterbox narration
        ↓
Whisper timestamp alignment
        ↓
render package
        ↓
Remotion long-form render
        ↓
FFmpeg audio mastering/finalization
        ↓
Short script + dedicated vertical scene plan
        ↓
Remotion vertical render
        ↓
thumbnail variants
        ↓
deterministic QA + optional visual critic
        ↓
private YouTube staging
```

## Editorial workflow

The editorial brain uses Qwen 3.5 in specialized passes.

### 1. Story architect

Transforms verified research into a story spine containing:

- strongest factual signal
- what changed
- why it is happening now
- necessary context
- evidence order
- tension/question to resolve
- practical implication
- what remains uncertain
- closing takeaway

### 2. Hook lab

Generate exactly three hook candidates using the same facts. Hooks are scored by deterministic criteria and a constrained model critique for:

- factual support
- specificity
- curiosity gap
- clarity
- brevity
- absence of dishonest clickbait

The chosen hook must be traceable to the research packet.

### 3. Scriptwriter

Long-form target remains approximately 4–7 minutes, usually 650–1,000 spoken words depending on pace and topic complexity.

The script should sound spoken rather than essay-like. It should avoid generic intros, repeated summaries, filler, unexplained jargon, and fake suspense.

### 4. Editorial critic

A separate pass critiques the draft against a fixed rubric:

- opening strength
- information density
- logical flow
- redundancy
- unsupported inference
- pacing
- clarity
- emotional rhythm
- payoff

Only one automatic rewrite is permitted. This prevents endless self-revision loops and keeps output reproducible.

### 5. Fact gate

Existing factual validation remains authoritative. Editing quality can never override failed sourcing.

## Scene planning model

The scene planner receives the approved script plus source references and emits structured JSON validated against a schema. It may choose only registered scene types.

Each scene contains at minimum:

- scene id
- narration span
- visual purpose
- scene type
- headline/subheadline if needed
- source references
- approved assets
- motion preset
- emphasis tokens
- transition type
- fallback scene type

Unsupported or invalid scene definitions are rejected before rendering.

## Scene vocabulary

Initial registered scene families:

- hook/title opener
- editorial headline card
- source/browser frame
- app/device frame
- GitHub/repository card
- game/store card
- stat counter
- bar/line/progress chart
- timeline
- before/after comparison
- two-column comparison
- quote/source card
- ranked/list card
- process/flow diagram
- code/terminal card
- map/location card when source data supports it
- social/context card where permitted
- chapter transition
- conclusion/what-to-watch card
- branded fallback editorial scene

Scene templates are deterministic React/SVG/CSS components rather than arbitrary AI-generated code.

## Visual rhythm

A scene is a semantic section; a visual beat is a visible change inside or between scenes.

### KernelRush

- Premium technology/editorial tone.
- Dark navy/black foundation with controlled mint/cyan/blue accents.
- Clean typography and generous spacing.
- Smooth camera motion and restrained transitions.
- Browser, GitHub, product UI, charts, source cards, timelines, and diagrams are preferred over generic stock footage.
- Typical long-form episode: approximately 15–25 semantic scenes with 30–60 visual beats.
- Normal beat length: approximately 4–10 seconds, with faster opening cuts.

### LobbySignal

- Gaming/internet-culture editorial tone.
- Dark violet/black foundation with pink/green accents.
- Faster kinetic typography, punchier transitions, reaction/context cards, game art/store frames, timelines, counters, and meme-context layouts.
- Energy comes from pacing and typography rather than random glitch effects.
- Typical long-form episode: approximately 20–35 semantic scenes with 45–80 visual beats.
- Normal beat length: approximately 2.5–7 seconds.

## Motion-design rules

- animation must support the sentence being spoken
- no motion solely because a template can animate
- typography never leaves safe areas
- important statistics get visual emphasis once, not repeatedly
- transitions are selected from a small branded library
- repeated templates use layout variants so consecutive scenes do not look identical
- camera zooms/pans are subtle unless LobbySignal deliberately uses a punch-in for emphasis
- no full-screen static title card should remain unchanged for an extended narration segment

## Asset resolver

The asset engine resolves visuals in priority order:

1. AutoTube-generated original visuals: charts, cards, diagrams, timelines, counters, typography.
2. Relevant first-party/source visuals: official announcements, product/app pages, GitHub repositories, Steam/game publisher pages, documentation, and other source-linked visuals where appropriate.
3. Explicitly licensed local assets.
4. Branded original fallback scene.

No automatic scraping/downloading of creator videos from YouTube, TikTok, Instagram, Twitch, or similar sources is part of the production engine.

### Source screenshots

A Playwright-based capture adapter may produce controlled screenshots of source pages. Captures store:

- source URL
- timestamp
- crop description
- story/source id
- local file hash

The system avoids capturing unnecessary page chrome and prefers the exact section relevant to the narration.

### Asset manifest

Every external visual and audio asset used by a render is recorded in `asset-manifest.json` with source and license/usage metadata when available.

## Narration architecture

Narration is generated paragraph-by-paragraph or scene-group-by-scene-group.

Each segment stores:

- text
- model
- voice profile
- seed/settings where supported
- raw WAV path
- duration
- normalized WAV path

Channel voice profiles are separate:

- KernelRush: calm, confident, clear, slightly analytical.
- LobbySignal: conversational, faster, more expressive, without sounding exaggerated or synthetic.

Narration segments are joined with controlled pauses. Awkward TTS segments can be regenerated independently instead of rerendering an entire episode.

## Exact caption timing

After narration is assembled, faster-whisper aligns speech to timestamps. AutoTube compares recognized text against the known script and rejects unexpectedly large mismatches.

Caption styling:

### KernelRush

- compact phrase-level captions
- lower-third safe placement
- one emphasized keyword/number where useful
- restrained animation

### LobbySignal

- larger phrase chunks
- more kinetic entry/exit
- selective keyword emphasis
- still avoids covering primary visuals

## Audio design

The audio system contains three independent layers:

1. narration
2. background music
3. SFX/stingers

### Music

Music comes from a curated local library whose licensing metadata is stored with the asset. AutoTube does not automatically scrape music from the web.

Music selection uses channel, topic energy, and duration tags. It may loop/crossfade but must avoid audible repetitive seams.

### SFX

Simple UI ticks, sweeps, and transition sounds can be generated programmatically or sourced from explicitly licensed local assets. SFX are sparse and tied to visual events.

### Mastering targets

Initial mastering target:

- narration consistently dominant
- music automatically ducked under speech
- final integrated loudness approximately YouTube-friendly, targeting around -14 LUFS as a starting reference
- peaks controlled below clipping, with a conservative true-peak ceiling

Exact mastering constants remain configurable and will be validated against first renders.

## Long-form renderer

Default output:

- 1920×1080
- 30 fps initially
- H.264 + AAC
- high-quality bitrate/CRF preset
- optional NVENC acceleration when available

The renderer consumes a self-contained render package and never reaches back into research or database logic during frame rendering.

## Shorts pipeline

Shorts are not center crops of the long-form episode.

The same verified research packet and approved long-form story are used to create a separate 30–45 second script with its own hook and payoff.

Output:

- 1080×1920
- mobile-safe typography
- approximately 5–12 semantic scenes depending on pacing
- aggressive first-second hook
- faster captions
- same channel identity
- no unsupported new factual claims

The Short can reuse source assets but receives a vertical-specific composition.

## Thumbnail engine

Each episode produces 3–5 meaningfully different thumbnail candidates.

Template families include:

- subject/product dominant
- huge statistic/number
- before/after
- comparison
- UI/screenshot focus
- minimal curiosity headline

Rules:

- 1280×720
- typically 2–5 words maximum
- mobile legibility test
- no fake UI or fabricated product imagery
- no misleading expressions or claims
- separate KernelRush and LobbySignal composition systems

The system initially outputs candidates for supervised review. Historical CTR may later inform template selection, but AutoTube never claims that an AI-estimated thumbnail score predicts actual CTR.

## Quality assurance

QA has three layers.

### Layer 1 — deterministic media validation

Hard failures include:

- wrong/missing resolution
- invalid codec/container
- missing audio
- audio/video duration mismatch beyond tolerance
- unexpectedly small file
- missing required scenes/assets
- render errors/placeholders
- missing thumbnails
- Short outside configured duration bounds
- caption file missing or malformed
- publication fact gate not passed

### Layer 2 — visual-layout validation

Programmatic checks include:

- text clipping
- safe-area violations
- invalid/missing assets
- excessive duplicate consecutive layouts
- blank frames
- extreme low contrast where detectable

### Layer 3 — local multimodal critic

Qwen 3.5 may review a generated contact sheet plus selected thumbnails using a fixed rubric for obvious composition, hierarchy, clutter, repetition, and branding issues.

This critic is advisory and may trigger at most one targeted rerender/correction pass. Deterministic safety/fact checks remain the hard authority.

## Hardware scheduling

GPU-heavy stages run sequentially to fit a 6 GB RTX 4050.

Recommended lifecycle:

1. load Qwen for editorial work
2. explicitly release/unload Qwen
3. run Chatterbox narration
4. release TTS GPU memory
5. run Whisper alignment
6. release ASR GPU memory
7. render motion graphics / encode
8. optionally reload Qwen for final contact-sheet critique

AutoTube must not keep Ollama, TTS, and Whisper simultaneously occupying GPU memory when avoidable.

A hardware profile controls:

- model ids
- context size
- TTS backend
- ASR backend/model
- renderer concurrency
- NVENC availability
- maximum parallel asset downloads

## Renderer-neutral interface

Python writes a versioned render package such as:

```text
render-package/
  manifest.json
  script.json
  scenes.json
  captions.json
  asset-manifest.json
  audio/
  images/
  fonts/
```

`manifest.json` includes a schema version. The Remotion project reads this package only through the schema.

This boundary ensures that a future renderer can replace Remotion without changing research, scripting, publishing, or analytics modules.

## Repository architecture

Planned additions:

```text
app/
  editorial/
    outline.py
    hooks.py
    critic.py
  planning/
    scene_schema.py
    scene_planner.py
    shorts.py
  assets/
    resolver.py
    screenshots.py
    manifest.py
  narration/
    chatterbox.py
    kokoro.py
    timing.py
  captions/
    align.py
  audio/
    mix.py
    library.py
  rendering/
    package.py
    runner.py
    validation.py
  shorts/
    pipeline.py
  visuals/
    thumbnail_v2.py
  quality/
    visual_critic.py

video/
  package.json
  src/
    Root.tsx
    compositions/
      KernelRushLong.tsx
      LobbySignalLong.tsx
      KernelRushShort.tsx
      LobbySignalShort.tsx
    scenes/
    components/
    themes/
```

The existing basic Pillow/FFmpeg renderer remains temporarily as a `legacy` fallback until the new system passes supervised output review.

## Error handling

- model timeout: retry once only when transient
- invalid JSON from scene planner: constrained repair pass, then fail closed
- missing source asset: deterministic fallback scene
- TTS segment failure: retry segment, then fallback TTS
- caption alignment failure: block production captions rather than guess timestamps
- Remotion failure: preserve render package and logs for diagnosis
- failed quality gate: never upload
- optional Short failure: long-form may still proceed if long-form passes and policy allows

## Testing strategy

### Unit tests

- scene schema validation
- hook selection rules
- renderer package generation
- asset manifest provenance
- TTS backend fallback
- caption mismatch handling
- audio mix configuration
- thumbnail layouts
- quality-gate rules

### Golden-image/component tests

Render deterministic still frames for key scene types and compare dimensions/layout invariants. Avoid brittle pixel-perfect assertions where platform font rasterization can differ.

### Integration tests

- synthetic research packet → script → scene plan
- sample render package → short Remotion render
- narration segment → timing alignment
- final MP4 → ffprobe validation

### Hardware smoke test

Windows workstation smoke command validates:

- Ollama model available
- TTS loads on CUDA
- Whisper model loads
- Node/renderer dependencies available
- FFmpeg/NVENC capability
- short 5–10 second render succeeds

## Supervised rollout

Do not enable `run-daily --live` immediately after implementation.

### Stage A

Render fixed internal sample stories specifically designed to exercise charts, screenshots, comparisons, timelines, captions, and audio.

### Stage B

Generate one real KernelRush and one real LobbySignal episode without upload. Inspect:

- hook
- narration
- pacing
- visual repetition
- typography
- screenshots
- captions
- audio balance
- thumbnail quality
- Short quality

### Stage C

Tune themes/templates and voice settings.

### Stage D

Run 3–7 supervised daily renders.

### Stage E

Only after consistent output, allow private YouTube staging and later unattended scheduling.

## Deferred from this implementation

- paid generative-video APIs
- autonomous use of copyrighted creator footage
- expensive local text-to-video diffusion as the primary visual engine
- photorealistic AI presenters
- autonomous comment/reply system
- sponsor insertion
- multi-language channels

Local generative image/video can be added later only as an optional scene adapter with independent licensing and hardware review.

## Definition of done

The professional media engine is complete when:

1. both channel themes render distinctly,
2. Qwen produces schema-valid editorial/scene plans,
3. a multi-scene 1080p KernelRush test episode renders,
4. a multi-scene 1080p LobbySignal test episode renders,
5. Chatterbox narration works with Kokoro fallback,
6. Whisper-aligned captions are rendered accurately,
7. source assets are captured with provenance metadata,
8. background audio and SFX are mixed correctly,
9. dedicated 9:16 Shorts render from the same story,
10. 3–5 thumbnail variants render,
11. deterministic QA blocks malformed output,
12. a contact-sheet visual review path exists,
13. the existing YouTube private-first publisher can consume the final long-form output,
14. CI/unit/integration tests pass,
15. no secrets or unlicensed bundled media are committed.

## Guiding principle

AutoTube should behave like a small editorial production team: one system researches, one writes, one critiques, one directs visuals, deterministic software edits, and QA decides whether the result is allowed to ship. The goal is not maximum automation at any quality; the goal is maximum automation while preserving professional presentation and factual trust.
