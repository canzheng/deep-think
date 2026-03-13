# Structured Adapter JSON Migration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace markdown-parsed adapter assets with per-family structured JSON adapters, rename prompt-facing guidance to `stage_guidance`, and unify stage-guidance rendering under the same Mustache-driven assembly model.

**Architecture:** Introduce one JSON schema and one runtime model per adapter family, plus a shared reusable `stage_guidance` structure keyed by canonical stage name. Keep only `stage_guidance` prompt-visible in the first migration; preserve all other adapter metadata in JSON for future use without rendering it into prompts yet. Required guidance items render plainly under `## Stage Guidance`, while conditionally relevant guidance items use the same `[CONDITIONAL condition="..."] ... [/CONDITIONAL]` wrapper convention as conditional state/context blocks.

**Tech Stack:** Python 3 in the Conda-managed `truth-seek` environment, JSON/JSON Schema, existing question-generator runtime, `unittest`, Mustache (`chevron`), prompt markdown templates.

---

## File Structure

**Files to create**
- `prompt/question-generator/adapters/schemas/stage-guidance.schema.json`
  - Shared schema for one stage-guidance entry map keyed by canonical stage name.
- `prompt/question-generator/adapters/schemas/task-adapter.schema.json`
- `prompt/question-generator/adapters/schemas/domain-adapter.schema.json`
- `prompt/question-generator/adapters/schemas/evidence-mode-adapter.schema.json`
- `prompt/question-generator/adapters/schemas/uncertainty-mode-adapter.schema.json`
- `prompt/question-generator/adapters/schemas/decision-mode-adapter.schema.json`
  - One schema per adapter family.
- `tools/question_generator/adapter_models.py`
  - Typed models/helpers for structured adapters if keeping them separate from existing runtime models is cleaner.

**Files to modify**
- `AGENTS.md`
  - Already updated for `Important` / `Moderate`; keep consistent if any examples still use old terms.
- `prompt/question-generator/IMPLEMENTATION.md`
  - Update adapter runtime design, stage-guidance context shape, and migration notes.
- `docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md`
  - Keep aligned with the implemented adapter JSON format and rendering behavior.
- `prompt/question-generator/adapters/tasks/*`
- `prompt/question-generator/adapters/domains/*`
- `prompt/question-generator/adapters/evidence-modes/*`
- `prompt/question-generator/adapters/uncertainty-modes/*`
- `prompt/question-generator/adapters/decision-modes/*`
  - Convert markdown adapter assets to JSON, or replace with adjacent `.json` files during migration.
- `tools/question_generator/models.py`
  - Extend existing runtime models if `adapter_models.py` is not introduced.
- `tools/question_generator/pathing.py`
  - Resolve adapter JSON file paths if extensions or folder conventions change.
- `tools/question_generator/adapter_resolution.py`
  - Keep module resolution working against the new asset format.
- `tools/question_generator/adapter_rendering.py`
  - Replace markdown parsing with structured JSON loading and prompt-facing stage-guidance preparation.
- `tools/question_generator/assembler.py`
  - Rename render-context field usage from legacy `active_steering` semantics to `stage_guidance`.
- `prompt/question-generator/stages/02-boundary.md`
- `prompt/question-generator/stages/03-structure.md`
- `prompt/question-generator/stages/04-scenarios.md`
- `prompt/question-generator/stages/05-question-generation.md`
- `prompt/question-generator/stages/06-evidence-planning.md`
- `prompt/question-generator/stages/07-decision-logic.md`
- `prompt/question-generator/stages/08-signal-translation.md`
- `prompt/question-generator/stages/09-monitoring.md`
  - Update `## Stage Guidance` sections to consume structured `stage_guidance` entries and explain the importance labels.
- `tests/question_generator/test_adapter_resolution.py`
- `tests/question_generator/test_adapter_rendering.py`
- `tests/question_generator/test_assembler.py`
- `tests/question_generator/test_non_render_prompt_quality.py`
- `tests/question_generator/test_examples.py`
  - Lock in structured-adapter loading and rendering behavior.

**Files likely unchanged**
- `prompt/question-generator/stages/01-routing.md`
  - Routing still does not consume stage guidance.
- `prompt/question-generator/stages/10-render.md`
  - Render can stay on the compatibility path for now.
- `tools/question_generator/state_resolution.py`
- `tools/question_generator/state_rendering.py`
  - Not central to this migration unless a test exposes a coupling.

## Chunk 1: Lock The Structured Adapter Behavior In Tests

### Task 1: Add failing tests for JSON adapter loading and stage-guidance rendering

**Files:**
- Modify: `tests/question_generator/test_adapter_rendering.py`
- Modify: `tests/question_generator/test_adapter_resolution.py`
- Modify: `tests/question_generator/test_assembler.py`

- [ ] **Step 1: Add a failing adapter-rendering test for structured stage guidance**

Write a test that prepares a minimal structured adapter payload and asserts the renderer produces prompt-facing guidance entries with:
- `Important`, `Moderate`, `Light`, or `None`
- a single guidance string per stage
- no markdown parsing of `## Stage Relevance`

- [ ] **Step 2: Add a failing test for conditional stage-guidance wrappers**

Write a test that verifies conditionally relevant guidance items are emitted under `## Stage Guidance` with:
- plain items for required guidance
- `[CONDITIONAL condition="..."] ... [/CONDITIONAL]` wrappers for conditional guidance

- [ ] **Step 3: Add a failing assembler test for the new stage-guidance context**

Write a test that renders a real non-render template and asserts:
- no unresolved `active_steering` placeholder remains
- the template consumes `stage_guidance`
- the stage-guidance intro line about importance labels is present

- [ ] **Step 4: Run the focused tests and confirm they fail**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_adapter_rendering \
  tests.question_generator.test_adapter_resolution \
  tests.question_generator.test_assembler -v
```

Expected:
- FAIL because the runtime still expects markdown adapters and legacy stage-guidance handling

## Chunk 2: Define Adapter Schemas And Convert Assets

### Task 2: Create one schema per adapter family and migrate adapter assets

**Files:**
- Create: `prompt/question-generator/adapters/schemas/*.schema.json`
- Modify: adapter asset files under `prompt/question-generator/adapters/`

- [ ] **Step 1: Add the shared `stage-guidance` schema**

Define:
- canonical stage-name keys
- `importance`
- `guidance`
- optional conditional metadata if needed, such as:
  - `condition`
  - `conditional`

Use prompt-facing importance values only:
- `Important`
- `Moderate`
- `Light`
- `None`

- [ ] **Step 2: Add one adapter schema per family**

Create:
- `task-adapter.schema.json`
- `domain-adapter.schema.json`
- `evidence-mode-adapter.schema.json`
- `uncertainty-mode-adapter.schema.json`
- `decision-mode-adapter.schema.json`

Each schema should:
- require only fields that actually exist for that family
- reuse the shared `stage-guidance` schema
- forbid unrelated family fields

- [ ] **Step 3: Convert task adapters to JSON**

Move all current task markdown content into structured JSON:
- `value`
- `prioritize`
- `stage_guidance`

- [ ] **Step 4: Convert domain adapters to JSON**

Move:
- `typical_ontology`
- `typical_bottlenecks`
- `typical_signals`
- `stage_guidance`

- [ ] **Step 5: Convert evidence-mode adapters to JSON**

Move:
- `prioritize`
- `strengths`
- `weaknesses`
- `stage_guidance`

- [ ] **Step 6: Convert uncertainty-mode adapters to JSON**

Move:
- `research_behavior`
- `risk`
- `stage_guidance`

- [ ] **Step 7: Convert decision-mode adapters to JSON**

Move:
- `use_when`
- `research_behavior`
- `key_questions`
- `action_logic`
- `monitoring_style`
- `failure_mode`
- `stage_guidance`

- [ ] **Step 8: Run focused validation tests**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_adapter_resolution \
  tests.question_generator.test_adapter_rendering -v
```

Expected:
- PASS for schema-aware loading fixtures once runtime support lands

## Chunk 3: Teach The Runtime To Load Structured Adapters

### Task 3: Replace markdown parsing with structured adapter loading

**Files:**
- Modify: `tools/question_generator/models.py` or create `tools/question_generator/adapter_models.py`
- Modify: `tools/question_generator/pathing.py`
- Modify: `tools/question_generator/adapter_resolution.py`
- Modify: `tools/question_generator/adapter_rendering.py`
- Modify: `tools/question_generator/assembler.py`

- [ ] **Step 1: Add runtime models for each adapter family**

Define typed models matching the new adapter schemas.

- [ ] **Step 2: Update adapter path resolution if needed**

Ensure adapter resolution returns the new JSON asset paths.

- [ ] **Step 3: Replace markdown `## Stage Relevance` parsing**

In `adapter_rendering.py`, load structured adapter JSON and extract the stage’s guidance entry directly from `stage_guidance`.

- [ ] **Step 4: Prepare prompt-facing `stage_guidance` entries**

For each resolved adapter that affects the stage, prepare an entry containing:
- wrapper/context label
- `importance`
- `guidance`
- conditional metadata, when present

Do not pre-render the entire block as one prose blob.

- [ ] **Step 5: Rename assembler context usage**

Ensure the non-render context exposes `stage_guidance`, not `active_steering`.

- [ ] **Step 6: Keep render-stage compatibility behavior isolated**

Do not broaden this migration into `Render` unless the current implementation requires a narrow compatibility shim.

- [ ] **Step 7: Run focused tests**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_adapter_rendering \
  tests.question_generator.test_adapter_resolution \
  tests.question_generator.test_assembler -v
```

Expected:
- PASS for structured-adapter loading and stage-guidance context behavior

## Chunk 4: Update Prompt Templates To Consume Structured Stage Guidance

### Task 4: Rewrite non-render `## Stage Guidance` sections around structured entries

**Files:**
- Modify: `prompt/question-generator/stages/02-boundary.md`
- Modify: `prompt/question-generator/stages/03-structure.md`
- Modify: `prompt/question-generator/stages/04-scenarios.md`
- Modify: `prompt/question-generator/stages/05-question-generation.md`
- Modify: `prompt/question-generator/stages/06-evidence-planning.md`
- Modify: `prompt/question-generator/stages/07-decision-logic.md`
- Modify: `prompt/question-generator/stages/08-signal-translation.md`
- Modify: `prompt/question-generator/stages/09-monitoring.md`

- [ ] **Step 1: Standardize the section intro**

Under `## Stage Guidance`, add one short line:

```md
Each guidance item includes an importance label that indicates how strongly it should shape the result of this stage.
```

- [ ] **Step 2: Render required guidance plainly**

Use Mustache sections so required guidance items render like:

```md
Important: ...
Moderate: ...
```

- [ ] **Step 3: Render conditional guidance with explicit wrappers**

Use the same prompt convention as conditional state/context blocks:

```md
[CONDITIONAL condition="..."]
Moderate: ...
[/CONDITIONAL]
```

- [ ] **Step 4: Keep prompts readable**

Do not dump non-stage-guidance adapter metadata into prompt bodies yet.

- [ ] **Step 5: Run template render tests**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_assembler \
  tests.question_generator.test_non_render_prompt_quality -v
```

Expected:
- PASS with fully rendered non-render prompts

## Chunk 5: Refresh Docs, Examples, And Artifacts

### Task 5: Align docs and generated artifacts with the structured-adapter model

**Files:**
- Modify: `prompt/question-generator/IMPLEMENTATION.md`
- Modify: `prompt/question-generator/README.md`
- Modify: `docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md`
- Modify: `tests/question_generator/assemble_non_render_prompts.py`
- Modify: `tests/question_generator/non_render_prompt_quality.md`
- Modify: `prompt/question-generator/examples/07-decision-logic.assembled.example.md`
- Modify: `tests/question_generator/test_examples.py`

- [ ] **Step 1: Refresh docs**

Document:
- per-family adapter JSON types
- `stage_guidance` naming
- `Important` / `Moderate` / `Light` / `None`
- conditional adapter-guidance wrappers

- [ ] **Step 2: Regenerate prompt artifacts**

Regenerate:
- review prompt artifacts
- worked example prompt
- any live prompt fixtures under `tests/question_generator/artifacts/`

- [ ] **Step 3: Run the full question-generator suite**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_non_render_prompt_quality \
  tests.question_generator.test_adapter_rendering \
  tests.question_generator.test_adapter_resolution \
  tests.question_generator.test_assembler \
  tests.question_generator.test_cli \
  tests.question_generator.test_contract_loading \
  tests.question_generator.test_examples \
  tests.question_generator.test_pathing \
  tests.question_generator.test_state_rendering \
  tests.question_generator.test_state_resolution -v
```

Expected:
- PASS

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md prompt/question-generator/IMPLEMENTATION.md prompt/question-generator/README.md docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md prompt/question-generator/adapters tools/question_generator tests/question_generator prompt/question-generator/examples/07-decision-logic.assembled.example.md
git commit -m "refactor: migrate adapters to structured json"
```
