# Render Output-Mode Subtemplates Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:executing-plans or
> superpowers:subagent-driven-development when implementing this plan. Steps
> use checkbox syntax for tracking.

**Goal:** Replace the current `Render` compatibility path with a Mustache-based
output-mode-selected render template family. Keep `Render` as one workflow
stage while making the Python runtime choose the correct render subtemplate
from `routing.output_mode`.

**Architecture:** Build one render context from shared state, contract
metadata, and stage guidance, but shape that context according to the selected
`output_mode`. Replace the broad `{{current_state}}` / `{{active_steering}}`
compatibility placeholders with one selected render subtemplate and explicit
mode-specific fields. Keep Python responsible for choosing the render template;
do not push mode selection into Mustache.

**Tech Stack:** Python 3 via `conda run -n truth-seek`, existing
question-generator runtime, Mustache (`chevron`), JSON/JSON Schema, `unittest`,
markdown stage templates.

---

## File Structure

**Files to create**
- `prompt/question-generator/stages/render/research-memo.md`
- `prompt/question-generator/stages/render/decision-memo.md`
- `prompt/question-generator/stages/render/monitoring-dashboard.md`
- `prompt/question-generator/stages/render/scenario-tree.md`
- `prompt/question-generator/stages/render/deep-research-prompt.md`
- `tools/question_generator/render_context.py`
  - render-mode selection and context preparation helpers

**Files to modify**
- `prompt/question-generator/stages/10-render.md`
  - convert into a thin wrapper with a selected body slot, or remove most of
    its content if a wrapper no longer adds value
- `tools/question_generator/assembler.py`
  - remove the legacy render compatibility branch
  - select the render template by `routing.output_mode`
  - render `Render` through Mustache like other stages
- `tools/question_generator/adapter_rendering.py`
  - rename remaining render-path wording from legacy compatibility terms if
    needed
- `tools/question_generator/state_resolution.py`
  - only if a helper is needed for render-context extraction
- `prompt/question-generator/README.md`
- `prompt/question-generator/IMPLEMENTATION.md`
- `docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md`
- `tests/question_generator/test_assembler.py`
- `tests/question_generator/test_examples.py`
- `tests/question_generator/test_state_rendering.py`
- `tests/question_generator/test_non_render_prompt_quality.py`
  - only if shared assumptions about prompt shape need updating

**Artifacts to refresh**
- `prompt/question-generator/examples/`
- `tests/question_generator/artifacts/non_render_prompt_review_prompts/`
  - only if any shared prompt-shape assumptions change
- render-specific assembled artifacts if you add them

## Chunk 1: Lock The Render-Selection Model In Tests

### Task 1: Add failing tests for output-mode-selected render templates

**Files:**
- Modify: `tests/question_generator/test_assembler.py`
- Modify: `tests/question_generator/test_examples.py`

- [ ] **Step 1: Add a failing test that `Render` chooses a subtemplate by `routing.output_mode`**

Verify that:
- `Decision Memo` and `Monitoring Dashboard` do not render through the same
  template body
- Python chooses the render template, not Mustache conditionals inside one
  giant template

- [ ] **Step 2: Add a failing test for render-context field shape**

For at least two output modes, assert that:
- expected required fields appear
- unrelated mode-specific sections do not appear
- no legacy `{{current_state}}` block is required

- [ ] **Step 3: Add a failing test that legacy render placeholders disappear**

Assert the final render prompt no longer depends on:
- `{{current_state}}`
- `{{active_steering}}`
- `{{required_output}}`
- `{{feedback}}`

- [ ] **Step 4: Run focused tests and confirm failure**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_assembler \
  tests.question_generator.test_examples -v
```

Expected:
- FAIL because `Render` still uses the compatibility path

## Chunk 2: Implement Render Template Selection And Context Preparation

### Task 2: Add one render-context builder and one template-selection map

**Files:**
- Create: `tools/question_generator/render_context.py`
- Modify: `tools/question_generator/assembler.py`

- [ ] **Step 1: Add canonical output-mode-to-template mapping**

Support at least:
- `Research Memo`
- `Decision Memo`
- `Monitoring Dashboard`
- `Scenario Tree`
- `Deep-Research Prompt`

- [ ] **Step 2: Add common render framing extraction**

Prepare:
- `routing.question`
- `routing.explicit_constraints`
- `routing.desired_output`
- `routing.decision_context`
- `routing.risk_tolerance`
- `routing.time_horizon`
- `routing.unit_of_analysis`
- `routing.assumptions`

- [ ] **Step 3: Add output-mode-specific context builders**

Build one explicit context for each output mode using the documented dependency
map.

The builder should:
- extract only the fields needed for that mode
- keep array/object structures Mustache-friendly
- avoid broad markdown blobs

- [ ] **Step 4: Expose `stage_guidance` and schemas in the render context**

Keep:
- `stage_guidance`
- `required_output_schema`
- `feedback_schema` when supported

Rename or remove any remaining legacy render-context terminology.

- [ ] **Step 5: Run focused tests**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_assembler \
  tests.question_generator.test_examples -v
```

Expected:
- partial PASS or improved failure surface before template work lands

## Chunk 3: Create Output-Mode Render Subtemplates

### Task 3: Write one render subtemplate per output mode

**Files:**
- Create: `prompt/question-generator/stages/render/*.md`
- Modify: `prompt/question-generator/stages/10-render.md`

- [ ] **Step 1: Decide whether `10-render.md` remains a thin wrapper**

If yes:
- keep only truly shared instructions there
- inject the selected subtemplate body through one explicit body slot

If no:
- make each render subtemplate fully standalone
- keep `10-render.md` as a compatibility shim only temporarily

- [ ] **Step 2: Write `decision-memo.md`**

Focus on:
- decision logic
- synthesis
- uncertainty
- action thresholds

- [ ] **Step 3: Write `monitoring-dashboard.md`**

Focus on:
- compact monitoring presentation
- signals
- action triggers
- update cadence

- [ ] **Step 4: Write `research-memo.md`**

Focus on:
- structured analysis narrative
- key questions
- evidence logic
- scenarios

- [ ] **Step 5: Write `scenario-tree.md`**

Focus on:
- branches
- branch logic
- triggers
- threshold variables

- [ ] **Step 6: Write `deep-research-prompt.md`**

Focus on:
- direct usability as a research prompt
- complete task framing
- evidence plan
- uncertainty map

- [ ] **Step 7: Run focused render-assembly tests**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_assembler \
  tests.question_generator.test_examples -v
```

Expected:
- PASS for render-template selection and prompt assembly

## Chunk 4: Remove The Compatibility Path

### Task 4: Make `Render` use the same assembly model as other stages

**Files:**
- Modify: `tools/question_generator/assembler.py`

- [ ] **Step 1: Remove or retire `_assemble_render_stage_prompt`**

`Render` should no longer depend on:
- whole-section state rendering
- legacy placeholder replacement
- `active_steering`

- [ ] **Step 2: Route `Render` through the Mustache rendering flow**

Use:
- selected render template
- prepared render context
- expanded schema blocks

- [ ] **Step 3: Keep backward compatibility only if truly necessary**

If any compatibility layer remains, document it clearly and keep it narrow.

- [ ] **Step 4: Run the broader question-generator suite**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_adapter_rendering \
  tests.question_generator.test_adapter_resolution \
  tests.question_generator.test_assembler \
  tests.question_generator.test_cli \
  tests.question_generator.test_contract_loading \
  tests.question_generator.test_examples \
  tests.question_generator.test_non_render_prompt_quality \
  tests.question_generator.test_pathing \
  tests.question_generator.test_state_rendering \
  tests.question_generator.test_state_resolution -v
```

Expected:
- PASS

## Chunk 5: Refresh Examples, Docs, And Artifacts

### Task 5: Regenerate checked examples and align docs

**Files:**
- Modify: `prompt/question-generator/README.md`
- Modify: `prompt/question-generator/IMPLEMENTATION.md`
- Modify: `docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md`
- Refresh: `prompt/question-generator/examples/*`

- [ ] **Step 1: Refresh the checked render example**

Choose at least one output mode and regenerate a checked assembled example.

- [ ] **Step 2: Update user-facing docs**

Document:
- render subtemplate selection
- output-mode-driven render contexts
- removal of the compatibility placeholder model

- [ ] **Step 3: Refresh any affected test artifacts**

Only refresh artifacts whose prompt shape changes because of the render
migration.

- [ ] **Step 4: Run final verification**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_adapter_rendering \
  tests.question_generator.test_adapter_resolution \
  tests.question_generator.test_assembler \
  tests.question_generator.test_cli \
  tests.question_generator.test_contract_loading \
  tests.question_generator.test_examples \
  tests.question_generator.test_non_render_prompt_quality \
  tests.question_generator.test_pathing \
  tests.question_generator.test_state_rendering \
  tests.question_generator.test_state_resolution -v
```

Expected:
- PASS with refreshed render behavior

## Notes

- `Render` should still be treated as one orchestration stage.
- Python, not the model, decides which render template to use.
- The render prompt family should become output-mode-first.
- A render-specific prompt-quality rubric is explicitly out of scope for this
  plan and should be added later as a separate follow-on.
