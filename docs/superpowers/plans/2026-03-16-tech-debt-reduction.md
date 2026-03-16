# Question Generator Tech Debt Reduction Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce question-generator maintenance debt by removing dead code, deleting retired subsystems, collapsing obsolete prompt-asset duplication, and removing accidental legacy artifacts that should no longer be tracked.

**Architecture:** Keep this cleanup behavior-preserving. Start with objective debt removal in the live Python path, then remove the retired state-rendering subsystem and its isolated references. After that, remove the obsolete `output-modes/` asset path so runtime behavior is sourced from the live render-template path only, and finish with docs, tests, and artifact cleanup that reflect the simplified architecture.

**Tech Stack:** Python `unittest`, Markdown, JSON, Conda environment (`truth-seek`)

---

## Chunk 1: Remove Dead Imports, Dead Helpers, And Stale Names

### Task 1: Clean up obvious dead code in the live runtime path

**Files:**
- Modify: `tools/question_generator/assembler.py`
- Modify: `tools/question_generator/cli.py`
- Modify: `tools/question_generator/render_context.py`
- Modify: `tests/question_generator/test_assembler.py`
- Test: `tests/question_generator/test_assembler.py`
- Test: `tests/question_generator/test_cli.py`

- [ ] **Step 1: Remove unused imports from live modules**

Delete imports that are no longer used after the refactors:
- `render_adapter_sections`, `render_state_sections`, `resolve_state_sections` from `tools/question_generator/assembler.py`
- `load_recipe` from `tools/question_generator/cli.py`
- `output_modes_dir` from `tools/question_generator/render_context.py`

- [ ] **Step 2: Remove private helpers in `assembler.py` that are no longer reachable**

Delete or inline helpers that are no longer used by the live code path:
- `_render_template_placeholders`
- `_render_required_output`
- `_render_feedback`

Before removal, confirm they are not referenced by tests or other modules.

- [ ] **Step 3: Rename stale test language that encodes the old model**

Update test names and wording such as:
- `test_render_prompt_uses_full_state_and_no_feedback`

Replace with wording that matches the current contract-selected render context model.

- [ ] **Step 4: Run the focused runtime tests**

Run:
```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_assembler \
  tests.question_generator.test_cli -v
```

Expected: PASS with no behavior changes.


## Chunk 2: Remove The Retired State Rendering Path

### Task 2: Delete `state_rendering.py`, `registry.py`, and all isolated references

**Files:**
- Delete: `tools/question_generator/state_rendering.py`
- Delete: `tools/question_generator/renderers/__init__.py`
- Delete: `tools/question_generator/renderers/registry.py`
- Delete: `tools/question_generator/renderers/common.py`
- Delete: `tools/question_generator/renderers/topic.py`
- Delete: `tools/question_generator/renderers/routing.py`
- Delete: `tools/question_generator/renderers/boundary.py`
- Delete: `tools/question_generator/renderers/structure.py`
- Delete: `tools/question_generator/renderers/scenarios.py`
- Delete: `tools/question_generator/renderers/questions.py`
- Delete: `tools/question_generator/renderers/evidence_plan.py`
- Delete: `tools/question_generator/renderers/uncertainty_map.py`
- Delete: `tools/question_generator/renderers/decision_logic.py`
- Delete: `tools/question_generator/renderers/synthesis.py`
- Delete: `tools/question_generator/renderers/signals.py`
- Delete: `tools/question_generator/renderers/monitoring.py`
- Modify: `tools/question_generator/assembler.py`
- Modify: `tools/question_generator/state_resolution.py`
- Modify: `README.md`
- Modify: `prompt/question-generator/README.md`
- Modify: `prompt/question-generator/IMPLEMENTATION.md`
- Modify: `tests/question_generator/test_assembler.py`
- Delete: `tests/question_generator/test_state_rendering.py`

- [ ] **Step 1: Confirm the subsystem is not on the live workflow path**

Confirm:
- prompt assembly no longer uses `state_rendering.py`
- workflow execution does not call `state_rendering.py` or `renderers/registry.py`
- remaining references are isolated to tests and documentation

Document that conclusion in the implementation docs as part of the removal.

- [ ] **Step 2: Remove stale live code references first**

At minimum:
- remove stale imports from `tools/question_generator/assembler.py`
- remove stale render-only branches in `tools/question_generator/state_resolution.py`
- remove any other code path that still implies the subsystem is active

- [ ] **Step 3: Delete the subsystem and any tests that exist only for it**

Delete:
- `tools/question_generator/state_rendering.py`
- the full `tools/question_generator/renderers/` package
- `tests/question_generator/test_state_rendering.py`

If any remaining test references this subsystem and does not validate the active
workflow path, remove that test as part of this chunk.

- [ ] **Step 4: Remove all isolated references in code, tests, and documentation**

Update:
- root README test commands
- question-generator README runtime module inventory
- implementation docs that still describe `state_rendering.py` or `registry.py`
- stale test names that still describe the old “full-state render” model

- [ ] **Step 5: Run the focused runtime suite after removal**

Run:
```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_assembler \
  tests.question_generator.test_cli \
  tests.question_generator.test_state_resolution \
  tests.question_generator.test_examples \
  tests.question_generator.test_contract_loading \
  tests.question_generator.test_documentation_consistency -v
```

Expected: PASS with the retired subsystem fully removed.


## Chunk 3: Remove The Obsolete Output-Mode Asset Path

### Task 3: Remove `output-modes/` from the live model and docs

**Files:**
- Modify: `tools/question_generator/adapter_resolution.py`
- Modify: `tools/question_generator/pathing.py`
- Modify: `tools/question_generator/render_context.py`
- Modify: `prompt/question-generator/question-generator-modular.md`
- Modify: `prompt/question-generator/README.md`
- Modify: `prompt/question-generator/IMPLEMENTATION.md`
- Modify: `tests/question_generator/test_pathing.py`
- Modify: `tests/question_generator/test_assembler.py`
- Delete: `prompt/question-generator/output-modes/*`

- [ ] **Step 1: Confirm runtime behavior no longer needs `output-modes/`**

Confirm the active system now renders from:
- `prompt/question-generator/stages/render/` for runtime render subtemplates
- contracts and stage templates for runtime prompt structure

Also confirm any remaining `output-modes/` references are legacy docs, pathing,
or tests rather than required live runtime inputs.

- [ ] **Step 2: Remove live code references to `output-modes/`**

At minimum:
- stop resolving `output_mode` through `prompt/question-generator/output-modes/`
- update path helpers, docstrings, and any runtime naming that still implies
  `output-modes/` is part of the live prompt assembly path
- update tests to assert the live render path is `stages/render/`

- [ ] **Step 3: Delete the obsolete `output-modes/` directory and scrub docs**

Delete:
- `prompt/question-generator/output-modes/`

Then update:
- `prompt/question-generator/question-generator-modular.md`
- `prompt/question-generator/README.md`
- `prompt/question-generator/IMPLEMENTATION.md`

The final docs should describe `stages/render/` as the render-template source
and should not describe `output-modes/` as a current repo component.

- [ ] **Step 4: Verify pathing and render tests**

Run:
```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_pathing \
  tests.question_generator.test_assembler -v
```

Expected: PASS with `output-modes/` removed from the live architecture.


## Chunk 4: Remove Stale Render-State Assumptions From Remaining Tests And Docs

### Task 4: Finish scrubbing old “full-state render” language from the repo

**Files:**
- Modify: `tests/question_generator/test_assembler.py`
- Modify: `prompt/question-generator/README.md`
- Modify: `prompt/question-generator/IMPLEMENTATION.md`
- Modify: `guidelines/question-generator-workflow.md`

- [ ] **Step 1: Search for remaining “full-state render” wording**

Look for phrases like:
- `full state`
- `uses_full_state`
- similar names implying render still receives an unconditional whole-state context

- [ ] **Step 2: Update names and comments without changing behavior**

The goal is wording cleanup, not runtime changes.

- [ ] **Step 3: Re-run the focused render-related suite**

Run:
```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_assembler \
  tests.question_generator.test_state_resolution \
  tests.question_generator.test_documentation_consistency -v
```

Expected: PASS


## Chunk 5: Remove Accidental Legacy Artifacts

### Task 5: Delete checked-in test artifacts that are already ignored

**Files:**
- Modify: `tests/question_generator/non_render_prompt_quality.md`
- Modify: `tests/question_generator/test_non_render_prompt_quality.py`
- Delete: `tests/question_generator/artifacts/live_non_render_900s_prompts/*`
- Delete: `tests/question_generator/artifacts/live_render_900s_prompts/*`
- Delete: `tests/question_generator/artifacts/non_render_prompt_review_*`

- [ ] **Step 1: Confirm the repo policy already treats these as generated outputs**

Verify that `.gitignore` already excludes `tests/question_generator/artifacts/*`,
which means checked-in contents under that path are accidental legacy rather
than intended long-lived fixtures.

- [ ] **Step 2: Confirm no live test depends on tracked ignored artifacts**

Confirm whether the following are actually consumed by live tests:
- `tests/question_generator/artifacts/non_render_prompt_review_*`
- `tests/question_generator/artifacts/live_non_render_900s_prompts/`
- `tests/question_generator/artifacts/live_render_900s_prompts/`

If any test still depends on these tracked ignored outputs, update the test so
it no longer relies on accidental legacy repository state.

- [ ] **Step 3: Remove the tracked ignored outputs from git**

- delete the ignored `live_*` prompt directories from the repository
- delete `non_render_prompt_review_*` tracked outputs from the repository
- keep future generated outputs untracked under the existing ignore policy

- [ ] **Step 4: Document the intended artifact policy**

Update the prompt-quality docs/tests so they describe these artifact paths as
generated local outputs that should remain untracked. Keep this documentation
inside the existing prompt-quality docs/tests rather than adding a new README.

- [ ] **Step 5: Run the prompt-quality suite**

Run:
```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_non_render_prompt_quality -v
```

Expected: PASS with accidental legacy artifacts removed and fixture policy made explicit.


## Chunk 6: Add Guardrails Against Reintroducing Dead Paths

### Task 6: Add a small debt-prevention layer to tests and docs

**Files:**
- Modify: `tests/question_generator/test_documentation_consistency.py`
- Modify: `tests/question_generator/test_pathing.py`
- Modify: `prompt/question-generator/IMPLEMENTATION.md`

- [ ] **Step 1: Add a test for the live render-path contract**

Assert something stable like:
- runtime render selection comes from `stages/render/`
- docs no longer describe `output-modes/` as an active repo component

- [ ] **Step 2: Add a small assertion against reintroducing obsolete broad-context markers**

Keep this narrow:
- do not snapshot whole prompts
- do assert the live render and non-render prompts do not depend on the old broad context markers

- [ ] **Step 3: Document the intended architecture after cleanup**

Update `prompt/question-generator/IMPLEMENTATION.md` so it explicitly states:
- which modules are production assembly path
- which modules are diagnostics/supporting tooling
- that runtime render assets live under `stages/render/` and `output-modes/`
  has been removed

- [ ] **Step 4: Run the focused consistency suite**

Run:
```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_documentation_consistency \
  tests.question_generator.test_pathing \
  tests.question_generator.test_assembler -v
```

Expected: PASS


## Chunk 7: Final Verification

### Task 7: Verify the cleanup reduced debt without changing behavior

**Files:**
- Verify only

- [ ] **Step 1: Run the full question-generator suite**

Run:
```bash
conda run -n truth-seek python -m unittest -v
```

Expected: all tests pass.

- [ ] **Step 2: Spot-check the main architectural docs**

Re-read:
- `prompt/question-generator/README.md`
- `prompt/question-generator/IMPLEMENTATION.md`
- `guidelines/question-generator-workflow.md`

Expected:
- no stale “full-state render” phrasing
- no references to `output-modes/` as a live repo component
- no deleted subsystem still described as live runtime behavior

- [ ] **Step 3: Commit the cleanup in coherent slices**

Suggested commit sequence:
```bash
git add tools/question_generator/assembler.py tools/question_generator/cli.py tools/question_generator/render_context.py tests/question_generator/test_assembler.py tests/question_generator/test_cli.py
git commit -m "chore: remove dead question-generator runtime helpers"

git add tools/question_generator/assembler.py tools/question_generator/state_resolution.py tools/question_generator/state_rendering.py tools/question_generator/renderers README.md prompt/question-generator/README.md prompt/question-generator/IMPLEMENTATION.md tests/question_generator/test_assembler.py tests/question_generator/test_state_rendering.py
git commit -m "chore: remove retired state-rendering subsystem"

git add tools/question_generator/adapter_resolution.py tools/question_generator/pathing.py tools/question_generator/render_context.py prompt/question-generator/question-generator-modular.md prompt/question-generator/README.md prompt/question-generator/IMPLEMENTATION.md prompt/question-generator/output-modes tests/question_generator/test_pathing.py tests/question_generator/test_assembler.py
git commit -m "refactor: remove obsolete output-mode asset path"

git add tests/question_generator/non_render_prompt_quality.md tests/question_generator/test_non_render_prompt_quality.py tests/question_generator/artifacts
git commit -m "chore: make prompt artifact retention explicit"
```
