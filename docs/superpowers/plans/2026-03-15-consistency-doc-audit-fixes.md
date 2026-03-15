# Question Generator Consistency Audit Fixes Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring repository documentation and related checks into alignment with the current question-generator implementation, with documentation as the primary fix surface.

**Architecture:** Treat the current Python runtime and checked-in contracts/templates as the implementation source for behavior, then update human-facing docs and repo guidance to describe that behavior precisely. Keep code changes minimal: only adjust tests or validation coverage where they currently encode outdated assumptions or fail to guard the documented invariants.

**Tech Stack:** Markdown, JSON Schema, Python `unittest`, Conda environment (`truth-seek`)

---

## Chunk 1: Fix Canonical Source-Of-Truth Wording

### Task 1: Clarify which artifacts are authoritative for what

**Files:**
- Modify: `AGENTS.md`
- Modify: `prompt/question-generator/README.md`
- Modify: `README.md`
- Modify: `prompt/question-generator/IMPLEMENTATION.md`

- [ ] **Step 1: Review the current wording for source-of-truth statements**

Read:
- `AGENTS.md`
- `README.md`
- `prompt/question-generator/README.md`
- `prompt/question-generator/IMPLEMENTATION.md`

Expected: identify all wording that currently treats both `question-generator-modular.md` and `stages/` as the same kind of source of truth.

- [ ] **Step 2: Rewrite the wording so responsibilities are distinct**

Update the docs to consistently express:
- `prompt/question-generator/question-generator-modular.md` is the conceptual host/source-of-truth reference for the overall generator design
- `prompt/question-generator/stages/` contains the runtime stage prompt templates actually assembled by the implementation
- `prompt/question-generator/contracts/` is the source of truth for stage dependencies, writes, and output schemas
- render subtemplates under `prompt/question-generator/stages/render/` are the runtime-selected render prompt bodies
- `prompt/question-generator/output-modes/` remains prompt/design guidance, not the file family selected at render-time by Python

- [ ] **Step 3: Make the language consistent across all touched docs**

Check that the same distinction appears in each file without contradiction.

Expected: no file claims that stage templates and the modular host are both the single authoritative prompt source in the same sense.


## Chunk 2: Fix Adapter Stage-Guidance Documentation

### Task 2: Document the actual adapter key format used by JSON and runtime

**Files:**
- Modify: `AGENTS.md`
- Modify: `prompt/question-generator/README.md`
- Modify: `prompt/question-generator/contracts/implementation-notes.md`
- Modify: `prompt/question-generator/adapters/schemas/stage-guidance.schema.json` (description/title text only if helpful)
- Test: `tests/question_generator/test_contract_loading.py` or a new focused adapter-schema test

- [ ] **Step 1: Confirm the implementation format**

Read:
- `tools/question_generator/adapter_models.py`
- `prompt/question-generator/adapters/schemas/stage-guidance.schema.json`
- one adapter example such as `prompt/question-generator/adapters/tasks/decide.json`

Expected: confirm that adapter `stage_guidance` is keyed by normalized stage ids like `routing`, `question_generation`, and `signal_translation`.

- [ ] **Step 2: Update repo guidance to match the actual JSON shape**

Replace wording that says adapter stage guidance must use title-cased stage names with wording like:
- user-facing canonical stage names are `Routing`, `Boundary`, ...
- adapter JSON keys use normalized runtime stage ids like `routing`, `boundary`, `question_generation`, ...

- [ ] **Step 3: Add a regression test for the documented rule**

Add or update a test that asserts the allowed adapter schema keys are the normalized runtime ids and that importance levels remain restricted to `Important`, `Moderate`, `Light`, and `None`.

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_contract_loading -v`
Expected: PASS


## Chunk 3: Fix Workflow And Render Semantics In Documentation

### Task 3: Align render docs with contract-driven selective reads

**Files:**
- Modify: `guidelines/question-generator-workflow.md`
- Modify: `prompt/question-generator/README.md`
- Modify: `prompt/question-generator/IMPLEMENTATION.md`
- Modify: `prompt/question-generator/stages/10-render.md` only if wording still overstates or understates current behavior
- Test: `tests/question_generator/test_state_resolution.py`

- [ ] **Step 1: Update the workflow guide’s render description**

Revise the workflow guide so it says:
- `shared_state.json` remains the sole durable analysis object
- render does not invent new analysis
- the runtime passes only the contract-declared common reads and output-mode-specific reads into the render prompt context
- render subtemplates operate on selected slices derived from shared state rather than an unconditional whole-state dump

- [ ] **Step 2: Update implementation and README language to match exactly**

Make sure the same model appears in the implementation doc and question-generator README:
- render is contract-driven
- `reads_required_common` feeds wrapper context
- `reads_by_output_mode` feeds selected subtemplate context
- output mode selection for rendering comes from `prompt/question-generator/stages/render/`

- [ ] **Step 3: Replace the stale full-state test expectation**

Update `tests/question_generator/test_state_resolution.py` so it no longer asserts that render “receives full state” via `resolve_state_sections`, because that function is no longer the runtime path render uses.

Prefer one of:
- remove the outdated render assertion entirely, or
- replace it with a test for `build_render_context` / render-contract selective reads

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_state_resolution tests.question_generator.test_assembler tests.question_generator.test_orchestrator -v`
Expected: PASS


## Chunk 4: Fix State Initialization Guidance

### Task 4: Document topic bootstrap correctly

**Files:**
- Modify: `guidelines/question-generator-workflow.md`
- Modify: `prompt/question-generator/contracts/shared_state_reference.md`
- Modify: `skills/question-generator-skill/SKILL.md` only if the wording can better reinforce the bootstrap behavior
- Test: `tests/question_generator/test_orchestrator.py`

- [ ] **Step 1: Correct the workflow guide’s initialization step**

Replace “initialize a fresh copy of `shared_state_schema.json`” with wording that matches the implementation:
- `shared_state_schema.json` defines the schema of live state
- a topic-first run starts from the minimal bootstrap payload `{"topic": "<raw user request>"}` via the orchestrator helpers

- [ ] **Step 2: Ensure the shared state reference reinforces schema-vs-instance separation**

Add a short note near the top of `shared_state_reference.md` clarifying:
- schema file is not an instance template
- orchestrator bootstrap creates the minimal initial state

- [ ] **Step 3: Keep the user-facing skill instructions consistent**

If needed, tighten `skills/question-generator-skill/SKILL.md` so it explicitly mirrors the actual topic bootstrap flow and does not imply copying the schema file as a run instance.

- [ ] **Step 4: Re-run the existing bootstrap tests**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_orchestrator -v`
Expected: PASS


## Chunk 5: Add Light Consistency Checks For Future Drift

### Task 5: Add tests that protect the documentation-backed invariants

**Files:**
- Modify: `tests/question_generator/test_contract_loading.py`
- Create or Modify: `tests/question_generator/test_documentation_consistency.py`

- [ ] **Step 1: Add a small invariant test for render contract semantics**

Write a test that asserts:
- render contract includes `reads_required_common`
- render contract includes `reads_by_output_mode`
- every supported render output mode has an entry

- [ ] **Step 2: Add a small invariant test for adapter stage-guidance keys**

Write a test that asserts the schema/runtime agree on the normalized stage ids used in adapter JSON.

- [ ] **Step 3: Keep the tests narrow and implementation-facing**

Do not write brittle prose-snapshot tests against long markdown files. Only verify stable structural rules that would otherwise allow docs/runtime drift to recur.

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_contract_loading tests.question_generator.test_assembler -v`
Expected: PASS


## Chunk 6: Final Verification

### Task 6: Verify the repo is internally consistent after the doc-first cleanup

**Files:**
- Verify only

- [ ] **Step 1: Run the focused question-generator suite**

Run:
```bash
conda run -n truth-seek python -m unittest -v
```

Expected: all tests pass.

- [ ] **Step 2: Spot-check the highest-risk docs manually**

Re-read:
- `AGENTS.md`
- `README.md`
- `guidelines/question-generator-workflow.md`
- `prompt/question-generator/README.md`
- `prompt/question-generator/IMPLEMENTATION.md`

Expected:
- no contradictory source-of-truth claims
- no instruction to copy `shared_state_schema.json` as a run instance
- no claim that render receives an unconditional full-state context
- no claim that adapter JSON uses title-cased stage names

- [ ] **Step 3: Commit the documentation-and-tests-only cleanup**

```bash
git add AGENTS.md README.md guidelines/question-generator-workflow.md prompt/question-generator/README.md prompt/question-generator/IMPLEMENTATION.md prompt/question-generator/contracts/shared_state_reference.md prompt/question-generator/contracts/implementation-notes.md prompt/question-generator/adapters/schemas/stage-guidance.schema.json skills/question-generator-skill/SKILL.md tests/question_generator/test_contract_loading.py tests/question_generator/test_state_resolution.py tests/question_generator/test_assembler.py tests/question_generator/test_orchestrator.py tests/question_generator/test_documentation_consistency.py
git commit -m "docs: align question-generator docs with runtime behavior"
```

