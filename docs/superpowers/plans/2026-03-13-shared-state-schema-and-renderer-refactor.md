# Shared-State Schema And Renderer Refactor Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the question-generator shared-state contract and prompt-facing state rendering so the live state remains one file, each top-level section has its own reusable schema file, prompt labels become `Relevant Context` and `Stage Guidance`, and prompt assembly can use richer per-section renderers without exposing adapter mechanics.

**Architecture:** Keep one durable shared-state JSON object, but split its contract into one JSON Schema file per top-level section under `contracts/state-sections/` and compose `shared_state_schema.json` from those files with `$ref`. In parallel, replace the generic JSON-only state renderer with a section-renderer registry that can present each state section in a more informative, model-friendly way while falling back to JSON where a custom renderer does not exist yet.

**Tech Stack:** Python 3 standard library (`json`, `pathlib`, `unittest`, `typing`), existing question-generator runtime and contracts, JSON Schema documents, markdown prompt assets.

---

## Chunk 1: Lock In The New Prompt-Facing Terminology And Rendering Contract

### Task 1: Define the new rendering interface before changing implementation

**Files:**
- Modify: `tests/question_generator/test_state_rendering.py`
- Modify: `tests/question_generator/test_assembler.py`
- Modify: `tools/question_generator/state_rendering.py`

- [ ] **Step 1: Update state-rendering tests to assert the new top-level label**

In `tests/question_generator/test_state_rendering.py`, replace assertions that expect:
- `## Current State`

with assertions for:
- `## Relevant Context`

Also add assertions that the old label is not present.

- [ ] **Step 2: Update assembler tests to assert the new guidance label**

In `tests/question_generator/test_assembler.py`, replace assertions that expect:
- `## Active Steering`

with assertions for:
- `## Stage Guidance`

Also update any prompt-order assertions to use the new names:
- `Relevant Context`
- `Stage Guidance`
- `Required Output`
- `Feedback`

- [ ] **Step 3: Add focused rendering tests for routing and fallback behavior**

Add tests that express the target renderer contract:
- routing rendering should not contain terms like `adapter`, `module`, or `selection`
- routing rendering should include human-meaningful fields such as task, domain, output mode, and assumptions
- sections without a specialized renderer should still render successfully through a generic JSON fallback

Use a populated fixture where possible so the tests exercise realistic content.

- [ ] **Step 4: Run the targeted tests to confirm they fail before implementation**

Run:

```bash
python -m unittest tests.question_generator.test_state_rendering tests.question_generator.test_assembler -v
```

Expected: FAIL because the runtime still emits `Current State` and `Active Steering`, and no specialized routing renderer exists.

- [ ] **Step 5: Commit**

```bash
git add tests/question_generator/test_state_rendering.py tests/question_generator/test_assembler.py
git commit -m "test: define prompt-facing renderer terminology"
```

## Chunk 2: Introduce A Section Renderer Registry With Backward-Compatible Fallback

### Task 2: Replace generic state rendering with a registry-driven renderer layer

**Files:**
- Create: `tools/question_generator/renderers/__init__.py`
- Create: `tools/question_generator/renderers/registry.py`
- Create: `tools/question_generator/renderers/common.py`
- Create: `tools/question_generator/renderers/topic.py`
- Create: `tools/question_generator/renderers/routing.py`
- Modify: `tools/question_generator/state_rendering.py`
- Test: `tests/question_generator/test_state_rendering.py`
- Test: `tests/question_generator/test_assembler.py`

- [ ] **Step 1: Create a small renderer registry**

Add `tools/question_generator/renderers/registry.py` with a mapping such as:

```python
SECTION_RENDERERS = {
    "topic": render_topic,
    "routing": render_routing,
}
```

Expose a helper like:

```python
def render_section(section_name: str, payload: object) -> list[str]:
    ...
```

Requirements:
- renderer output should be a list of markdown lines or a rendered string
- unknown sections should fall back to the existing JSON block behavior
- keep the implementation dependency-light

- [ ] **Step 2: Extract generic JSON fallback helpers**

Create `tools/question_generator/renderers/common.py` for reusable helpers like:
- markdown heading construction
- JSON fenced-block rendering
- list cleaning / empty-value filtering if needed

Do not bake stage-specific logic into the common helpers.

- [ ] **Step 3: Implement the topic renderer**

Add `tools/question_generator/renderers/topic.py` with a simple renderer that:
- presents the topic under a meaningful heading
- uses a fenced text block or simple paragraph consistently
- avoids JSON formatting for the raw topic unless needed for markdown safety

- [ ] **Step 4: Implement the routing renderer**

Add `tools/question_generator/renderers/routing.py` that emphasizes:
- normalized question
- explicit constraints
- decision context
- task/domain/output/evidence/uncertainty/decision modes
- rationales
- time horizon
- unit of analysis
- assumptions

Guardrails:
- do not mention adapter resolution
- do not mention selected modules
- do not mention implementation concepts like routing mechanics
- preserve fidelity to actual state values

Prefer an informative markdown summary over a raw JSON dump.

- [ ] **Step 5: Update `state_rendering.py` to use the registry**

Refactor `tools/question_generator/state_rendering.py` so:
- the top-level heading becomes `## Relevant Context`
- each section is rendered through the registry
- unknown sections still fall back to the old JSON rendering

Do not remove the existing section-heading map until the registry fully replaces it.

- [ ] **Step 6: Run the focused tests**

Run:

```bash
python -m unittest tests.question_generator.test_state_rendering tests.question_generator.test_assembler -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add tools/question_generator/renderers tools/question_generator/state_rendering.py tests/question_generator/test_state_rendering.py tests/question_generator/test_assembler.py
git commit -m "feat: add registry-based state renderers"
```

## Chunk 3: Rename Prompt-Facing Guidance Labels And Keep Assembly Stable

### Task 3: Update adapter rendering to use `Stage Guidance` without changing routing behavior

**Files:**
- Modify: `tools/question_generator/adapter_rendering.py`
- Test: `tests/question_generator/test_adapter_rendering.py`
- Test: `tests/question_generator/test_assembler.py`

- [ ] **Step 1: Change the rendered guidance label**

Update `tools/question_generator/adapter_rendering.py` so the top-level heading becomes:
- `## Stage Guidance`

Do not change the underlying adapter-resolution logic in this task.
This is a prompt-facing terminology change only.

- [ ] **Step 2: Update tests accordingly**

In `tests/question_generator/test_adapter_rendering.py` and `tests/question_generator/test_assembler.py`, change assertions from:
- `## Active Steering`

to:
- `## Stage Guidance`

Also add a regression check that non-render stages still receive only the short output-mode guidance, not the full render outline.

- [ ] **Step 3: Run the targeted tests**

Run:

```bash
python -m unittest tests.question_generator.test_adapter_rendering tests.question_generator.test_assembler -v
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add tools/question_generator/adapter_rendering.py tests/question_generator/test_adapter_rendering.py tests/question_generator/test_assembler.py
git commit -m "feat: rename prompt guidance heading"
```

## Chunk 4: Split The Shared-State Contract Into Top-Level Section Schemas

### Task 4: Create one JSON Schema file per top-level shared-state section

**Files:**
- Create: `prompt/question-generator/contracts/state-sections/topic.schema.json`
- Create: `prompt/question-generator/contracts/state-sections/routing.schema.json`
- Create: `prompt/question-generator/contracts/state-sections/boundary.schema.json`
- Create: `prompt/question-generator/contracts/state-sections/structure.schema.json`
- Create: `prompt/question-generator/contracts/state-sections/scenarios.schema.json`
- Create: `prompt/question-generator/contracts/state-sections/questions.schema.json`
- Create: `prompt/question-generator/contracts/state-sections/evidence_plan.schema.json`
- Create: `prompt/question-generator/contracts/state-sections/uncertainty_map.schema.json`
- Create: `prompt/question-generator/contracts/state-sections/decision_logic.schema.json`
- Create: `prompt/question-generator/contracts/state-sections/synthesis.schema.json`
- Create: `prompt/question-generator/contracts/state-sections/signals.schema.json`
- Create: `prompt/question-generator/contracts/state-sections/monitoring.schema.json`
- Modify: `prompt/question-generator/contracts/shared_state_schema.json`
- Test: `tests/question_generator/test_contract_loading.py`

- [ ] **Step 1: Decide the schema style and shared conventions**

Use JSON Schema documents with consistent top-level shape, for example:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "state-sections/routing.schema.json",
  "title": "Routing",
  "type": "object",
  "required": [...],
  "properties": {...},
  "additionalProperties": false
}
```

Keep the schemas pragmatic:
- required keys for stage-owned shape
- `additionalProperties: false` where current contracts already expect closed objects
- do not over-model semantic content beyond today’s contract needs

- [ ] **Step 2: Convert each top-level section into its own schema file**

Translate the current template-like shape from `shared_state_schema.json` into real schemas:
- `topic` becomes a string schema
- object sections become object schemas
- array sections define item schemas

For repeated question-like structures, reuse local `$defs` inside the relevant section schema file if it reduces duplication.

Keep the split flat:
- one file per top-level section
- no deeper file nesting yet

- [ ] **Step 3: Compose the top-level shared-state schema with `$ref`**

Rewrite `prompt/question-generator/contracts/shared_state_schema.json` into a real composed schema:
- top-level `type: object`
- `required` listing all top-level sections
- `properties` entries using `$ref` to the section schema files
- `additionalProperties: false`

The top-level live shared state should still validate as one JSON object with the same section names.

- [ ] **Step 4: Add or update schema-shape tests**

Extend `tests/question_generator/test_contract_loading.py` or add a new focused contract test to verify:
- `shared_state_schema.json` now has schema metadata and `$ref`
- every expected top-level section points to the correct file
- every referenced section file exists

If the repo already has a shared-state-schema test path, use that instead of inventing a parallel one.

- [ ] **Step 5: Run focused contract tests**

Run:

```bash
python -m unittest tests.question_generator.test_contract_loading tests.question_generator.test_pathing -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add prompt/question-generator/contracts/shared_state_schema.json prompt/question-generator/contracts/state-sections tests/question_generator/test_contract_loading.py
git commit -m "feat: split shared-state schema into section contracts"
```

## Chunk 5: Reuse Section Schemas In Stage Contracts Where It Helps

### Task 5: Reduce duplication between stage output schemas and shared-state section schemas

**Files:**
- Modify: `prompt/question-generator/contracts/01-routing.contract.json`
- Modify: `prompt/question-generator/contracts/02-boundary.contract.json`
- Modify: `prompt/question-generator/contracts/03-structure.contract.json`
- Modify: `prompt/question-generator/contracts/04-scenarios.contract.json`
- Modify: `prompt/question-generator/contracts/05-question-generation.contract.json`
- Modify: `prompt/question-generator/contracts/06-evidence-planning.contract.json`
- Modify: `prompt/question-generator/contracts/07-decision-logic.contract.json`
- Modify: `prompt/question-generator/contracts/08-signal-translation.contract.json`
- Modify: `prompt/question-generator/contracts/09-monitoring.contract.json`
- Test: `tests/question_generator/test_contract_loading.py`

- [ ] **Step 1: Choose a minimally disruptive reuse pattern**

Recommended pattern:
- keep each stage contract’s outer `output_schema` object
- replace the inner section schema bodies with `$ref` to the relevant section-schema file where practical

Example:

```json
{
  "type": "object",
  "required": ["routing"],
  "properties": {
    "routing": {
      "$ref": "./state-sections/routing.schema.json"
    }
  },
  "additionalProperties": false
}
```

For multi-section writers like `Evidence Planning` or `Decision Logic`, reference both relevant section schemas.

- [ ] **Step 2: Verify loader compatibility before broad changes**

Check whether `tools/question_generator/contracts.py` or any consumer assumes `output_schema` always has inline `properties`.

If the current loader only preserves raw schema without resolving refs, that is acceptable for assembly, but tests should confirm nothing breaks.

If any code path incorrectly assumes inline-only schemas, fix that code in the smallest possible way before continuing.

- [ ] **Step 3: Update stage contracts incrementally**

Migrate contracts one by one, running focused tests between groups, rather than rewriting all stage contracts blindly in one pass.

Suggested order:
1. `routing`
2. `boundary`
3. `structure`
4. `scenarios`
5. `question_generation`
6. `evidence_planning`
7. `decision_logic`
8. `signal_translation`
9. `monitoring`

- [ ] **Step 4: Add contract regression tests**

Add tests that verify:
- each stage contract still loads successfully
- `output_schema.raw` preserves `$ref` content
- the assembled prompt still includes the required output block for each stage

- [ ] **Step 5: Run contract and assembly tests**

Run:

```bash
python -m unittest tests.question_generator.test_contract_loading tests.question_generator.test_assembler tests.question_generator.test_examples -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add prompt/question-generator/contracts/*.contract.json tools/question_generator/contracts.py tests/question_generator/test_contract_loading.py tests/question_generator/test_assembler.py tests/question_generator/test_examples.py
git commit -m "refactor: reuse section schemas in stage contracts"
```

## Chunk 6: Expand Section Renderers Beyond Routing And Validate Prompt Quality Regressions

### Task 6: Add informative renderers for the highest-value sections first

**Files:**
- Create: `tools/question_generator/renderers/boundary.py`
- Create: `tools/question_generator/renderers/structure.py`
- Create: `tools/question_generator/renderers/scenarios.py`
- Create: `tools/question_generator/renderers/questions.py`
- Create: `tools/question_generator/renderers/evidence_plan.py`
- Create: `tools/question_generator/renderers/uncertainty_map.py`
- Create: `tools/question_generator/renderers/decision_logic.py`
- Create: `tools/question_generator/renderers/synthesis.py`
- Create: `tools/question_generator/renderers/signals.py`
- Create: `tools/question_generator/renderers/monitoring.py`
- Modify: `tools/question_generator/renderers/registry.py`
- Test: `tests/question_generator/test_state_rendering.py`
- Test: `tests/question_generator/test_assembler.py`

- [ ] **Step 1: Prioritize the highest-value renderers first**

Implement in this order:
1. `structure`
2. `scenarios`
3. `questions`
4. `decision_logic`
5. `monitoring`
6. the remaining sections

This order follows the biggest prompt-quality payoff.

- [ ] **Step 2: Keep each renderer simple and faithful**

Each renderer should:
- preserve the underlying data
- surface the most useful information first
- avoid decorative prose
- avoid final deliverable formatting
- be readable in assembled prompts

If a section is too complex to improve cleanly in one pass, keep the fallback JSON renderer for that section and document the limitation instead of forcing a bad custom summary.

- [ ] **Step 3: Add fixture-driven tests**

Use `tests/question_generator/fixtures/populated_state.json` to add tests that check:
- the specialized renderer includes key summary fields
- the specialized renderer omits obvious implementation jargon
- the output remains deterministic

Keep the tests robust:
- assert for anchor phrases and meaningful content
- avoid brittle full-string comparisons

- [ ] **Step 4: Run targeted rendering and assembly tests**

Run:

```bash
python -m unittest tests.question_generator.test_state_rendering tests.question_generator.test_assembler tests.question_generator.test_examples -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/question_generator/renderers tests/question_generator/test_state_rendering.py tests/question_generator/test_assembler.py tests/question_generator/test_examples.py
git commit -m "feat: add informative section renderers"
```

## Chunk 7: Update Docs And Regenerate Prompt Examples

### Task 7: Align implementation docs, README, and examples with the new contract and renderers

**Files:**
- Modify: `prompt/question-generator/README.md`
- Modify: `prompt/question-generator/IMPLEMENTATION.md`
- Modify: `docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md`
- Modify: `prompt/question-generator/examples/07-decision-logic.assembled.example.md`
- Optionally modify other assembled examples under `prompt/question-generator/examples/`

- [ ] **Step 1: Update the implementation docs**

In `README.md` and `IMPLEMENTATION.md`, document:
- `Relevant Context`
- `Stage Guidance`
- section renderer registry and fallback behavior
- per-section schema files under `contracts/state-sections/`
- composed `shared_state_schema.json`
- stage contracts reusing section schemas via `$ref`

- [ ] **Step 2: Reconcile the architecture doc with the implemented details**

Update the architecture spec if any small implementation details differ from the design assumptions, but keep the design intent intact.

- [ ] **Step 3: Regenerate at least one assembled example**

Use the CLI to regenerate:
- `prompt/question-generator/examples/07-decision-logic.assembled.example.md`

If other examples become stale or misleading after the renderer changes, refresh them too.

- [ ] **Step 4: Run the CLI/example tests**

Run:

```bash
python -m unittest tests.question_generator.test_cli tests.question_generator.test_examples -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add prompt/question-generator/README.md prompt/question-generator/IMPLEMENTATION.md docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md prompt/question-generator/examples
git commit -m "docs: update schema and renderer architecture"
```

## Chunk 8: Final Verification

### Task 8: Run the full question-generator test suite after the refactor

**Files:**
- No new files
- Verify: `tests/question_generator/`

- [ ] **Step 1: Run the full suite**

Run:

```bash
python -m unittest tests.question_generator.test_adapter_rendering tests.question_generator.test_adapter_resolution tests.question_generator.test_assembler tests.question_generator.test_cli tests.question_generator.test_contract_loading tests.question_generator.test_examples tests.question_generator.test_pathing tests.question_generator.test_state_rendering tests.question_generator.test_state_resolution -v
```

Expected: PASS.

- [ ] **Step 2: Assemble one stage manually for spot-checking**

Run:

```bash
python -m tools.question_generator.cli --stage decision_logic --state tests/question_generator/fixtures/populated_state.json
```

Verify manually that:
- the prompt uses `Relevant Context`
- the prompt uses `Stage Guidance`
- routing is rendered as human-meaningful context, not adapter mechanics
- the required output block still appears correctly

- [ ] **Step 3: Commit any final test or doc cleanup**

If the verification step reveals minor wording or formatting issues, fix them and make one final cleanup commit.

## Notes And Guardrails

- Keep the live shared state as one JSON file throughout this refactor.
- Keep the section-schema split flat: one file per top-level section only.
- Prefer JSON Schema `$ref` composition over custom Python schema assembly.
- Do not make section renderers produce final deliverable prose.
- Preserve a generic JSON fallback so renderer rollout can be incremental.
- Do not remove or weaken stage contract output schemas during the migration.
- The routing renderer may hide adapter mechanics in prompt output, but the underlying routing state must remain intact in the live state file.

## Verification Checklist

Before calling this work complete:
- [ ] Prompt-facing state label is `Relevant Context`.
- [ ] Prompt-facing guidance label is `Stage Guidance`.
- [ ] A renderer registry exists with JSON fallback.
- [ ] Routing uses a human-meaningful self-renderer with no adapter-selection language.
- [ ] `contracts/state-sections/` contains one schema file per top-level shared-state section.
- [ ] `shared_state_schema.json` is a composed schema using `$ref`.
- [ ] Stage contracts reuse section schemas where practical.
- [ ] README and implementation docs match the refactor.
- [ ] Full question-generator test suite passes locally.

Plan complete and saved to `docs/superpowers/plans/2026-03-13-shared-state-schema-and-renderer-refactor.md`. Ready to execute?
