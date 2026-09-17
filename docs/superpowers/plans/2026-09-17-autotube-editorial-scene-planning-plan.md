# AutoTube Editorial + Scene Planning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace one-shot script generation with a structured local editorial pipeline that produces an approved script plus schema-valid scene plans for KernelRush and LobbySignal.

**Architecture:** Keep the existing research/fact-check pipeline, but insert a renderer-neutral editorial layer between research and media generation. Qwen 3.5 9B is called through a reusable Ollama JSON client; specialized passes produce an outline, exactly three hooks, a chosen hook, a draft, one critic pass, at most one rewrite, then a validated scene plan. Dry runs should emit `editorial.json`, `script.txt`, and `scenes.json` while the legacy renderer remains untouched.

**Tech Stack:** Python 3.11+, dataclasses, stdlib JSON/urllib, Ollama `qwen3.5:9b`, pytest.

**Spec:** `docs/superpowers/specs/2026-09-17-autotube-professional-media-engine-design.md`

## Global Constraints

- Production LLM default is `qwen3.5:9b`; override remains `AUTOTUBE_LLM_MODEL`.
- Research evidence remains authoritative; editorial quality never bypasses `validate_script`.
- Exactly three hook candidates are generated.
- At most one automatic rewrite is permitted.
- Scene planner may emit only registered scene types and motion/transition presets.
- Invalid JSON gets one constrained repair attempt, then fails closed.
- No renderer-specific React/Remotion data structures enter the Python editorial layer.

---

### Task 1: Add a structured Ollama JSON client

**Files:**
- Create: `app/editorial/ollama.py`
- Create: `app/editorial/__init__.py`
- Test: `tests/test_editorial_ollama.py`

**Interfaces:**
- Consumes: Ollama `/api/generate` HTTP endpoint and `AUTOTUBE_LLM_MODEL`.
- Produces: `OllamaJsonClient.generate_json(system_prompt: str, payload: dict, *, repair_prompt: str | None = None) -> dict` and `OllamaJsonError`.

- [ ] **Step 1: Write the failing tests**

```python
import json
from app.editorial.ollama import OllamaJsonClient, OllamaJsonError


def test_json_client_uses_configured_model(monkeypatch):
    seen = {}
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self):
            return json.dumps({'response': '{"ok": true}'}).encode()
    def fake_urlopen(req, timeout):
        seen.update(json.loads(req.data))
        return Response()
    monkeypatch.setattr('app.editorial.ollama.urllib.request.urlopen', fake_urlopen)
    client = OllamaJsonClient(model='qwen3.5:9b')
    assert client.generate_json('system', {'x': 1}) == {'ok': True}
    assert seen['model'] == 'qwen3.5:9b'


def test_json_client_repairs_invalid_json_once(monkeypatch):
    replies = iter(['not json', '{"fixed": 1}'])
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return json.dumps({'response': next(replies)}).encode()
    monkeypatch.setattr('app.editorial.ollama.urllib.request.urlopen', lambda req, timeout: Response())
    assert OllamaJsonClient().generate_json('s', {'x': 1}, repair_prompt='return valid json') == {'fixed': 1}


def test_json_client_fails_after_one_repair(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return json.dumps({'response': 'still invalid'}).encode()
    monkeypatch.setattr('app.editorial.ollama.urllib.request.urlopen', lambda req, timeout: Response())
    try:
        OllamaJsonClient().generate_json('s', {}, repair_prompt='repair')
    except OllamaJsonError:
        return
    assert False, 'expected OllamaJsonError'
```

- [ ] **Step 2: Run tests to verify RED**

Run: `pytest tests/test_editorial_ollama.py -v`
Expected: FAIL because `app.editorial.ollama` does not exist.

- [ ] **Step 3: Implement the minimal client**

```python
class OllamaJsonError(RuntimeError):
    pass

class OllamaJsonClient:
    def __init__(self, model=None, base_url='http://127.0.0.1:11434', timeout=180):
        self.model = model or os.getenv('AUTOTUBE_LLM_MODEL', 'qwen3.5:9b')
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def _call(self, prompt: str) -> str:
        body = json.dumps({'model': self.model, 'stream': False, 'prompt': prompt}).encode()
        req = urllib.request.Request(
            self.base_url + '/api/generate', body,
            headers={'Content-Type': 'application/json'},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            return json.loads(response.read())['response'].strip()

    def generate_json(self, system_prompt, payload, *, repair_prompt=None):
        raw = self._call(system_prompt + '\n\nINPUT JSON:\n' + json.dumps(payload, ensure_ascii=False))
        try:
            return json.loads(raw)
        except json.JSONDecodeError as first:
            if repair_prompt is None:
                raise OllamaJsonError(str(first)) from first
            repaired = self._call(repair_prompt + '\n\nBROKEN OUTPUT:\n' + raw)
            try:
                return json.loads(repaired)
            except json.JSONDecodeError as second:
                raise OllamaJsonError(str(second)) from second
```

- [ ] **Step 4: Run the focused tests and full suite**

Run: `pytest tests/test_editorial_ollama.py -v && pytest -q`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/editorial tests/test_editorial_ollama.py
git commit -m "feat: add structured Ollama editorial client"
```

---

### Task 2: Add editorial dataclasses and hook-selection rules

**Files:**
- Create: `app/editorial/models.py`
- Create: `app/editorial/hooks.py`
- Test: `tests/test_editorial_hooks.py`

**Interfaces:**
- Produces: `HookCandidate`, `EditorialOutline`, `Critique`, `EditorialBundle` dataclasses.
- Produces: `select_hook(hooks: tuple[HookCandidate, ...]) -> HookCandidate`.

- [ ] **Step 1: Write failing tests**

```python
from app.editorial.hooks import select_hook
from app.editorial.models import HookCandidate


def test_hook_selector_requires_exactly_three_candidates():
    try:
        select_hook((HookCandidate('a', 1, 1, 1, 1, True),))
    except ValueError as exc:
        assert 'exactly three' in str(exc)
        return
    assert False


def test_hook_selector_rejects_unsupported_candidate_even_with_high_score():
    hooks = (
        HookCandidate('unsupported', 10, 10, 10, 10, False),
        HookCandidate('specific', 8, 8, 8, 8, True),
        HookCandidate('clear', 7, 7, 9, 7, True),
    )
    assert select_hook(hooks).text == 'specific'
```

- [ ] **Step 2: Verify RED**

Run: `pytest tests/test_editorial_hooks.py -v`
Expected: FAIL on missing modules.

- [ ] **Step 3: Implement typed models and deterministic selection**

Use frozen dataclasses. `HookCandidate` fields are `text`, `specificity`, `curiosity`, `clarity`, `brevity`, `fact_supported`. `score` is the arithmetic mean of the four numeric fields. `select_hook` requires exactly three candidates, removes unsupported candidates, and returns the highest-scoring remaining hook; tied hooks preserve input order.

- [ ] **Step 4: Verify GREEN**

Run: `pytest tests/test_editorial_hooks.py -v && pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/editorial/models.py app/editorial/hooks.py tests/test_editorial_hooks.py
git commit -m "feat: add editorial models and hook selection"
```

---

### Task 3: Build the multi-pass editorial director

**Files:**
- Create: `app/editorial/director.py`
- Test: `tests/test_editorial_director.py`
- Modify: `app/scripting/engine.py` only to keep the legacy class available; do not remove it yet.

**Interfaces:**
- Consumes: research packet dict and `OllamaJsonClient`-compatible client.
- Produces: `build_editorial_bundle(packet: dict, llm) -> EditorialBundle`.

- [ ] **Step 1: Write a fake-LLM behavioral test**

The fake returns, in order: outline JSON, three hooks JSON, draft JSON, critique JSON, rewrite JSON. Assert that the resulting bundle uses the rewritten script only when `critique.needs_rewrite` is true and that exactly five model calls occur in that case.

```python
class FakeLLM:
    def __init__(self, replies): self.replies = iter(replies); self.calls = 0
    def generate_json(self, *args, **kwargs):
        self.calls += 1
        return next(self.replies)
```

Also add a second test with `needs_rewrite=False` and assert only four calls occur.

- [ ] **Step 2: Verify RED**

Run: `pytest tests/test_editorial_director.py -v`
Expected: FAIL because `build_editorial_bundle` is missing.

- [ ] **Step 3: Implement focused prompts and validation**

`director.py` must define constant prompts for:
- story architect
- hook lab
- scriptwriter
- critic
- rewrite

The prompts must explicitly say to use only supplied evidence, preserve uncertainty, and not invent dates/numbers/quotes. Parse model dictionaries into dataclasses rather than returning raw dictionaries. Reject hook payloads not containing exactly three hooks.

- [ ] **Step 4: Add fact-gate integration test**

Create a test where the fake script includes `9,999` but the research corpus does not. Call `validate_script(bundle.script, packet)` and assert it fails. This proves the new editorial layer did not weaken the existing fact gate.

- [ ] **Step 5: Run full verification**

Run: `pytest tests/test_editorial_director.py tests/test_core.py -v && pytest -q && python -m compileall -q app && ruff check app tests`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add app/editorial/director.py tests/test_editorial_director.py app/scripting/engine.py
git commit -m "feat: add multi-pass editorial director"
```

---

### Task 4: Define the renderer-neutral scene schema

**Files:**
- Create: `app/planning/__init__.py`
- Create: `app/planning/scene_schema.py`
- Test: `tests/test_scene_schema.py`

**Interfaces:**
- Produces: `SceneSpec`, `ScenePlan`, `parse_scene_plan(payload: dict) -> ScenePlan`.

Registered `scene_type` values:

```python
SCENE_TYPES = {
    'hook', 'headline', 'source_browser', 'device', 'github', 'game_store',
    'stat', 'chart', 'timeline', 'before_after', 'comparison', 'quote',
    'list', 'process', 'code', 'map', 'social_context', 'chapter',
    'conclusion', 'fallback_editorial',
}
```

Registered motions: `none`, `fade`, `push_left`, `push_up`, `slow_zoom`, `punch_in`, `parallax`.
Registered transitions: `cut`, `crossfade`, `wipe`, `slide`, `stinger`.

- [ ] **Step 1: Write failing validation tests**

Test that an unknown scene type is rejected, scene ids must be unique, every scene has non-empty narration text, and source ids are stored as tuples.

- [ ] **Step 2: Verify RED**

Run: `pytest tests/test_scene_schema.py -v`
Expected: FAIL on missing module.

- [ ] **Step 3: Implement frozen dataclasses and parser**

`SceneSpec` must include: `id`, `narration`, `purpose`, `scene_type`, `headline`, `subheadline`, `source_ids`, `asset_ids`, `motion`, `emphasis`, `transition`, `fallback_scene_type`, `data`.
`ScenePlan` includes `channel_id`, `format`, `scenes`, `schema_version='1'`.

- [ ] **Step 4: Verify GREEN and commit**

Run: `pytest tests/test_scene_schema.py -v && pytest -q`

```bash
git add app/planning tests/test_scene_schema.py
git commit -m "feat: define renderer neutral scene schema"
```

---

### Task 5: Add channel-aware scene planning

**Files:**
- Create: `app/planning/scene_planner.py`
- Test: `tests/test_scene_planner.py`

**Interfaces:**
- Produces: `plan_longform_scenes(channel_id: str, script: str, packet: dict, llm) -> ScenePlan`.
- Consumes only registered scene vocabulary from Task 4.

- [ ] **Step 1: Write failing tests**

For KernelRush fake output, assert the prompt requests restrained premium editorial pacing. For LobbySignal, assert it requests faster gaming/editorial pacing. Feed an invalid first response and a repaired second response; assert parser returns a valid plan and the LLM is called exactly twice.

- [ ] **Step 2: Verify RED**

Run: `pytest tests/test_scene_planner.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement scene-planner prompts**

KernelRush prompt targets 15–25 semantic scenes and premium tech-editorial visuals. LobbySignal targets 20–35 semantic scenes and higher-energy gaming/internet-culture visuals. Both instruct the model to prefer source/browser/product cards and original data graphics over generic imagery.

- [ ] **Step 4: Verify GREEN**

Run: `pytest tests/test_scene_planner.py -v && pytest -q && ruff check app tests`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/planning/scene_planner.py tests/test_scene_planner.py
git commit -m "feat: add channel aware scene planning"
```

---

### Task 6: Wire editorial artifacts into dry-run generation without replacing rendering

**Files:**
- Modify: `app/orchestration/daily.py`
- Create: `app/orchestration/editorial.py`
- Test: `tests/test_professional_planning_flow.py`

**Interfaces:**
- Produces: `prepare_editorial(packet, channel_id, llm) -> tuple[EditorialBundle, ScenePlan]`.
- `run_channel` writes `editorial.json`, `script.txt`, `scenes.json` before thumbnail/render stages.

- [ ] **Step 1: Write failing orchestration test**

Stub candidate collection/research and inject fake LLM output. Run `run_channel` in dry mode and assert the episode directory contains all three new artifacts and the returned result still has status `generated`.

- [ ] **Step 2: Verify RED**

Run: `pytest tests/test_professional_planning_flow.py -v`
Expected: FAIL because artifacts are not produced.

- [ ] **Step 3: Implement the narrow integration**

Preserve the existing legacy path for `script_engine` injections used by current tests. When no explicit legacy `script_engine` is provided, use the new editorial director + scene planner. Keep `validate_script` immediately after final script selection. Rendering remains the legacy renderer until later plans.

- [ ] **Step 4: Run complete verification**

Run: `pytest -q && python -m compileall -q app && ruff check app tests`
Expected: PASS with no existing test regressions.

- [ ] **Step 5: Commit**

```bash
git add app/orchestration tests/test_professional_planning_flow.py
git commit -m "feat: emit professional editorial and scene artifacts"
```

## Phase Exit Criteria

- Dry runs produce structured editorial and scene artifacts.
- Qwen is used in bounded specialized passes.
- Scene output is renderer-neutral and schema validated.
- Existing fact gate remains authoritative.
- Legacy rendering still works, so the repo is deployable at the end of this phase.
- Full CI is green.
