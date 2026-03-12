# Non-Render Prompt Quality Review Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a structured Codex-run quality review workflow for non-render assembled prompts that fails on hard-gate violations and always reports per-stage quality scores.

**Architecture:** Keep deterministic `unittest` coverage for local assembly correctness, then add a separate review workflow under `tests/question_generator/` that assembles every non-render stage prompt from a populated shared-state fixture plus a seeded stress-case topic, packages those prompts for review, validates structured review results, and prints a compact score report. The review workflow should use the checked-in reviewer prompt and treat hard gates as pass/fail while leaving scored dimensions diagnostic-only for now.

**Tech Stack:** Python 3 standard library (`json`, `argparse`, `pathlib`, `random`, `subprocess`, `sys`, `textwrap`, `typing`), existing question-generator assembler/CLI, markdown review prompt, JSON review contract, `unittest`.

---

## Chunk 1: Define The Review Contract And Deterministic Harness Boundaries

### Task 1: Add the structured review-output contract and lock in local validation behavior

**Files:**
- Create: `tests/question_generator/non_render_prompt_review_schema.json`
- Modify: `tests/question_generator/non_render_prompt_review_prompt.md`
- Create: `tests/question_generator/test_non_render_prompt_quality.py`

- [ ] **Step 1: Define the review JSON contract**

Create `tests/question_generator/non_render_prompt_review_schema.json` for one stage review result and include:
- `stage`
- `hard_gates`
- `scores`
- `top_findings`
- `overall_recommendation`
- `summary`

Required hard gates:
- `no_confusion`
- `stage_discipline`
- `input_precedence_clarity`
- `output_contract_clarity`

Required scores:
- `task_clarity`
- `context_quality`
- `readability`
- `completeness`
- `priority_clarity`
- `decision_usefulness`
- `context_efficiency`
- `guidance_quality`

Use enum-style constraints where helpful:
- hard-gate values only `PASS` or `FAIL`
- score values only integers `1` through `5`
- recommendation values only:
  - `Accept`
  - `Accept with minor improvements`
  - `Needs revision`

- [ ] **Step 2: Update the reviewer prompt to require JSON-only output**

Revise `tests/question_generator/non_render_prompt_review_prompt.md` so it still explains the rubric in natural language, but its required output section now demands JSON that conforms to `non_render_prompt_review_schema.json`.

The prompt should:
- preserve the same hard gates and scored dimensions
- require concrete findings and justifications
- explicitly prohibit extra prose outside the JSON object

- [ ] **Step 3: Add deterministic tests for the review contract**

Create `tests/question_generator/test_non_render_prompt_quality.py` with tests that:
- load the review schema file and verify expected top-level keys exist
- verify the canonical non-render stage list is present in the harness module once added
- validate that a known-good sample review payload passes local checker validation
- validate that a sample payload with one hard-gate `FAIL` is accepted as structurally valid but classified as a failing quality result
- validate that a malformed payload is rejected with a useful error

- [ ] **Step 4: Run the new test file to verify failure before implementation**

Run:

```bash
python -m unittest tests.question_generator.test_non_render_prompt_quality -v
```

Expected: FAIL because the schema and checker do not exist yet.

- [ ] **Step 5: Commit**

```bash
git add tests/question_generator/non_render_prompt_review_prompt.md tests/question_generator/non_render_prompt_review_schema.json tests/question_generator/test_non_render_prompt_quality.py
git commit -m "test: define non-render prompt review contract"
```

## Chunk 2: Build The Non-Render Prompt Review Bundle Generator

### Task 2: Assemble every non-render stage prompt from shared state plus a seeded stress-case topic

**Files:**
- Create: `tests/question_generator/assemble_non_render_prompts.py`
- Modify: `tests/question_generator/fixtures/populated_state.json`
- Test: `tests/question_generator/test_non_render_prompt_quality.py`

- [ ] **Step 1: Create the canonical stage list**

In `tests/question_generator/assemble_non_render_prompts.py`, define:

```python
NON_RENDER_STAGES = [
    "routing",
    "boundary",
    "structure",
    "scenarios",
    "question_generation",
    "evidence_planning",
    "decision_logic",
    "signal_translation",
    "monitoring",
]
```

Keep `render` out of this list intentionally.

- [ ] **Step 2: Add a seeded stress-case topic generator**

Add a helper such as:

```python
def choose_review_topic(seed: int = 20260313) -> str:
    ...
```

Requirements:
- choose from a small curated list of realistic but slightly messy topics
- be seeded so the run is repeatable
- print or return the selected topic so the review artifact records what was reviewed

Example topic pool:
- `Should we add to NVDA ahead of earnings if hyperscaler capex holds but China restrictions tighten?`
- `If a late-stage AI startup depends on GPU subsidies and regulatory waivers, what should management decide in the next 12 months?`
- `Which signals matter most if export controls shift while demand stays strong but supply remains politically constrained?`

- [ ] **Step 3: Load the populated state fixture and inject the chosen topic**

Use:
- `tests/question_generator/fixtures/populated_state.json`

When building the review bundle:
- load the populated fixture
- overwrite `state["topic"]` with the chosen stress-case topic
- assemble each stage prompt using `assemble_stage_prompt`

Do not mutate the fixture file itself during the run.

- [ ] **Step 4: Emit one review bundle artifact**

Write a script output format that is easy for Codex to review, for example:

```md
# Non-Render Prompt Review Bundle

## Review Topic
...

## Stage: routing
```md
...
```

## Stage: boundary
```md
...
```
```

Recommended default output path:
- `tests/question_generator/artifacts/non_render_prompt_review_bundle.md`

Also support `--output` for alternate paths.

- [ ] **Step 5: Add deterministic tests for the bundle generator**

Extend `tests/question_generator/test_non_render_prompt_quality.py` to verify:
- the bundle generator includes all non-render stages
- the chosen topic appears in the bundle
- no unresolved placeholders remain
- each stage heading appears exactly once

- [ ] **Step 6: Run the focused tests**

Run:

```bash
python -m unittest tests.question_generator.test_non_render_prompt_quality -v
```

Expected: PASS for the bundle-generation tests once this task is complete.

- [ ] **Step 7: Commit**

```bash
git add tests/question_generator/assemble_non_render_prompts.py tests/question_generator/test_non_render_prompt_quality.py
git commit -m "feat: add non-render prompt review bundle generator"
```

## Chunk 3: Implement Review Result Validation And Score Reporting

### Task 3: Validate structured reviewer output and enforce the hard-gate pass rule

**Files:**
- Create: `tests/question_generator/check_non_render_prompt_review.py`
- Test: `tests/question_generator/test_non_render_prompt_quality.py`

- [ ] **Step 1: Implement the local review checker**

Create `tests/question_generator/check_non_render_prompt_review.py` with functions that:
- load the review schema contract
- load one or more stage review results from JSON
- validate required keys and allowed values
- compute overall pass/fail based on hard gates only

Suggested functions:

```python
def load_review_schema() -> dict:
    ...

def validate_review_payload(payload: dict) -> list[str]:
    ...

def review_passes_hard_gates(payload: dict) -> bool:
    ...
```

Keep this validation dependency-light.
Use manual validation with the standard library unless the repo already adopts a JSON Schema validator dependency.

- [ ] **Step 2: Print a compact score report**

The checker CLI should print a clear per-stage summary including:
- stage name
- each hard gate result
- each scored dimension
- overall recommendation

Suggested report shape:

```text
Stage: decision_logic
  Hard gates: PASS PASS PASS PASS
  Scores: task=4 context=4 readability=5 completeness=4 priority=4 usefulness=5 efficiency=3 guidance=4
  Recommendation: Accept with minor improvements
```

At the end, print either:
- `QUALITY REVIEW PASS`
- `QUALITY REVIEW FAIL`

Exit non-zero if any reviewed stage fails a hard gate.

- [ ] **Step 3: Add checker tests**

Extend `tests/question_generator/test_non_render_prompt_quality.py` with cases that:
- verify a valid all-pass review returns success
- verify one hard-gate failure returns failure
- verify out-of-range scores return validation errors
- verify unknown stage names are rejected

- [ ] **Step 4: Run the focused tests**

Run:

```bash
python -m unittest tests.question_generator.test_non_render_prompt_quality -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/question_generator/check_non_render_prompt_review.py tests/question_generator/test_non_render_prompt_quality.py
git commit -m "feat: add non-render prompt review checker"
```

## Chunk 4: Document And Operationalize The Codex-Run Review Workflow

### Task 4: Write the operator-facing workflow for running the review step end to end

**Files:**
- Create: `tests/question_generator/non_render_prompt_quality.md`
- Modify: `docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md`
- Test: `tests/question_generator/test_non_render_prompt_quality.py`

- [ ] **Step 1: Document the exact workflow**

Create `tests/question_generator/non_render_prompt_quality.md` with:
- purpose of the quality gate
- scope: non-render stages only
- required inputs
- how to generate the review bundle
- how to ask Codex to perform the review using the checked-in reviewer prompt
- how to save the structured review JSON
- how to run the checker against that JSON
- what pass/fail means

Include exact commands such as:

```bash
python tests/question_generator/assemble_non_render_prompts.py --output tests/question_generator/artifacts/non_render_prompt_review_bundle.md
python tests/question_generator/check_non_render_prompt_review.py --input path/to/review.json
```

- [ ] **Step 2: Reconcile terminology with the architecture doc**

Ensure the workflow doc and architecture doc use the same terms:
- `Relevant Context`
- `Stage Guidance`
- hard gates
- scored dimensions
- non-render stages

- [ ] **Step 3: Add a smoke test for the artifact path if useful**

If the new scripts expose a stable CLI, add a lightweight test that:
- runs the bundle generator
- confirms the artifact file is created in a temp directory

Do not make `unittest` depend on an external model review.

- [ ] **Step 4: Run the full question-generator test suite**

Run:

```bash
python -m unittest tests.question_generator.test_adapter_rendering tests.question_generator.test_adapter_resolution tests.question_generator.test_assembler tests.question_generator.test_cli tests.question_generator.test_contract_loading tests.question_generator.test_examples tests.question_generator.test_non_render_prompt_quality tests.question_generator.test_pathing tests.question_generator.test_state_rendering tests.question_generator.test_state_resolution -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/question_generator/non_render_prompt_quality.md docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md tests/question_generator/test_non_render_prompt_quality.py
git commit -m "docs: add non-render prompt quality review workflow"
```

## Chunk 5: Run A Real Review And Check In A Baseline Example

### Task 5: Exercise the workflow once so future changes have a reference

**Files:**
- Optionally create: `tests/question_generator/artifacts/non_render_prompt_review_bundle.md`
- Optionally create: `tests/question_generator/artifacts/non_render_prompt_review.sample.json`
- Modify if needed: `tests/question_generator/non_render_prompt_quality.md`

- [ ] **Step 1: Generate the real review bundle**

Run:

```bash
python tests/question_generator/assemble_non_render_prompts.py --output tests/question_generator/artifacts/non_render_prompt_review_bundle.md
```

Confirm the file includes:
- review topic
- all non-render stages
- fully assembled prompts

- [ ] **Step 2: Have Codex review the bundle**

Use `tests/question_generator/non_render_prompt_review_prompt.md` as the rubric and ask Codex to produce structured JSON review output for each stage.

Save the result as:
- `tests/question_generator/artifacts/non_render_prompt_review.sample.json`

If the team does not want checked-in artifacts under `tests/question_generator/artifacts/`, place the sample under a temp path and only document the run.

- [ ] **Step 3: Validate the review output**

Run:

```bash
python tests/question_generator/check_non_render_prompt_review.py --input tests/question_generator/artifacts/non_render_prompt_review.sample.json
```

Expected:
- printed score report
- pass/fail summary based on hard gates

- [ ] **Step 4: Update docs if reality differs from the intended workflow**

If the first real run exposes friction:
- update `tests/question_generator/non_render_prompt_quality.md`
- update `tests/question_generator/non_render_prompt_review_prompt.md`
- update `tests/question_generator/non_render_prompt_review_schema.json`

Keep the workflow honest to what operators will actually do.

- [ ] **Step 5: Commit**

```bash
git add tests/question_generator/non_render_prompt_quality.md tests/question_generator/non_render_prompt_review_prompt.md tests/question_generator/non_render_prompt_review_schema.json
git commit -m "chore: baseline non-render prompt quality review flow"
```

## Notes And Guardrails

- Use the populated shared-state fixture as the review context base.
- Overwrite only the in-memory `topic` value during bundle generation.
- Keep the stress-case topic seeded and reproducible even though it is selected from a random-looking pool.
- Do not make the local `unittest` suite depend on a live model call.
- Treat hard gates as the only pass/fail rule for the first version.
- Always surface the scored dimensions, even when the prompt fails.
- Keep `Render` out of this workflow until a separate render-stage rubric exists.

## Verification Checklist

Before calling this work complete:
- [ ] The architecture design doc includes the structured Codex-run review gate.
- [ ] The reviewer prompt requires structured JSON output.
- [ ] The review schema exists and matches the checker.
- [ ] The bundle generator assembles every non-render stage from populated state plus a seeded stress-case topic.
- [ ] The checker fails on any hard-gate failure and prints scores for every stage.
- [ ] The operator doc explains the workflow end to end.
- [ ] The full question-generator test suite passes locally.

Plan complete and saved to `docs/superpowers/plans/2026-03-13-non-render-prompt-quality-review.md`. Ready to execute?
