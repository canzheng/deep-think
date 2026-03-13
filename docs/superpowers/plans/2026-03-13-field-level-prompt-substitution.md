# Mustache-Based Field-Level Prompt Assembly Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace whole-section non-render prompt assembly with Mustache-based field-level templates so non-render prompts include only the state fields they actually need, while still supporting repeated object structures like scenarios, questions, signals, and monitoring items.

**Architecture:** Build one render context per stage from the shared state, expanded stage contract metadata, and routed guidance. Render non-render stage templates with Mustache over that context, using the field-level dependency map in `IMPLEMENTATION.md` to decide what each template should consume. Keep `active_steering` as a temporary pre-rendered exception during the first migration, and keep render-stage broad context handling separate until its own input model is finalized. Include conditionally useful upstream fields directly in templates under explicit `[CONDITIONAL condition="..."] ... [/CONDITIONAL]` blocks rather than making the assembler reason about fuzzy applicability.

Important authoring rule:
- for stages after `Routing`, do not inject adapter-selection routing fields
  directly into the prompt
- do not use `routing.task`, `routing.domain`, `routing.output_mode`,
  `routing.evidence_mode`, `routing.uncertainty_mode`, or
  `routing.decision_mode` as ordinary prompt context
- the effect of those classifications should come through `active_steering`

**Tech Stack:** Python 3, a lightweight Mustache implementation for Python, existing question-generator assembler/runtime, markdown templates, `unittest`, Conda-managed Python execution.

---

## File Structure

**Files to modify**
- `AGENTS.md`
  - Follow the repo rule: run Python through the Conda-managed environment while executing this plan.
- `prompt/question-generator/IMPLEMENTATION.md`
  - Update the runtime description so it reflects Mustache-based non-render prompt assembly and the compact dependency map as the target runtime behavior.
- `prompt/question-generator/README.md`
  - Update prompt authoring guidance to describe Mustache templates, stage render context, and the remaining `active_steering` exception.
- `prompt/question-generator/stages/01-routing.md`
  - Rewrite as a Mustache template that uses only the topic and contract-derived metadata it needs.
- `prompt/question-generator/stages/02-boundary.md`
  - Rewrite to consume required routing fields plus explicit conditional routing groups where scope-widening logic may matter.
- `prompt/question-generator/stages/03-structure.md`
  - Rewrite to consume required routing and boundary fields plus conditional groups for hidden-variable, evidence-discipline, and cross-system context.
- `prompt/question-generator/stages/04-scenarios.md`
  - Rewrite to consume required routing, boundary, and structure fields, including conditional groups and Mustache sections where list rendering helps readability.
- `prompt/question-generator/stages/05-question-generation.md`
  - Rewrite to consume required routing, structure, and scenarios inputs, plus conditional boundary/structure groups, `active_steering`, `required_output_schema`, and `feedback_schema` if applicable.
- `prompt/question-generator/stages/06-evidence-planning.md`
  - Rewrite to consume required routing, questions, and scenarios inputs, plus conditional question/routing/structure groups, using Mustache sections for repeated question/evidence structures.
- `prompt/question-generator/stages/07-decision-logic.md`
  - Rewrite to consume required routing, scenarios, evidence-plan, and uncertainty-map inputs, plus conditional question/boundary/structure groups.
- `prompt/question-generator/stages/08-signal-translation.md`
  - Rewrite to consume required questions, evidence-plan, and scenarios inputs, plus conditional decision-logic/structure/uncertainty groups, using Mustache sections for repeated list/object structures.
- `prompt/question-generator/stages/09-monitoring.md`
  - Rewrite to consume required signals and uncertainty-map inputs, plus conditional decision-logic/scenario/evidence groups, using Mustache sections for monitoring items.
- `tools/question_generator/assembler.py`
  - Replace non-render block interpolation with Mustache rendering over a prepared stage context.
- `tools/question_generator/state_resolution.py`
  - Narrow or retire whole-section non-render reads as model-facing prompt inputs; keep only what render still needs.
- `tools/question_generator/state_rendering.py`
  - Narrow its role to render-stage support if still needed.
- `tests/question_generator/test_assembler.py`
  - Add failing tests for Mustache rendering, per-template render success, repeated object rendering, and absence of legacy whole-section blocks in non-render prompts.
- `tests/question_generator/test_cli.py`
  - Update CLI expectations to match the Mustache-rendered non-render prompt shape.
- `tests/question_generator/test_examples.py`
  - Refresh assembled example expectations if they currently rely on whole-section context blocks.
- `tests/question_generator/test_non_render_prompt_quality.py`
  - Update prompt-shape expectations to confirm Mustache-rendered non-render prompts are fully resolved and no longer rely on old block placeholders.
- `tests/question_generator/assemble_non_render_prompts.py`
  - Continue generating non-render prompt artifacts, now from Mustache templates.

**Files to create if needed**
- `tests/question_generator/fixtures/mustache_render_state.json`
  - Optional focused fixture for precise Mustache rendering tests if the broader populated fixture becomes too noisy.

**Files likely unchanged**
- `prompt/question-generator/stages/10-render.md`
  - Render remains a separate case for now.
- `tools/question_generator/adapter_rendering.py`
  - Keep `active_steering` as the one temporary pre-rendered natural-language block.

## Chunk 1: Lock The Mustache Rendering Model In Tests

### Task 1: Add failing tests for Mustache stage rendering and non-render prompt shape

**Files:**
- Modify: `tests/question_generator/test_assembler.py`
- Modify: `tests/question_generator/test_non_render_prompt_quality.py`
- Modify: `tests/question_generator/test_cli.py`

- [ ] **Step 1: Add a focused assembler test for Mustache scalar rendering**

Add a test in `tests/question_generator/test_assembler.py` that renders a temporary template like:

```mustache
Time horizon: {{routing.time_horizon}}
Scope: {{boundary.core_system}}
Decision context: {{routing.decision_context}}
```

Use a populated shared state fixture and assert:
- all values render correctly
- no unresolved Mustache tags remain
- the prompt does not append any whole-section context block

- [ ] **Step 2: Add a focused assembler test for Mustache sections over repeated objects**

Add a test that renders a temporary template using a section such as:

```mustache
{{#scenarios.alternative_scenarios}}
### {{name}}
Summary: {{summary}}
{{#branch_points}}
- {{.}}
{{/branch_points}}
{{/scenarios.alternative_scenarios}}
```

Assert:
- multiple scenario entries render
- nested string-list sections render correctly
- no unresolved Mustache tags remain

- [ ] **Step 3: Add a focused assembler test for the remaining special/context values**

Add a test that renders a temporary template containing:

```mustache
{{active_steering}}

{{required_output_schema}}

{{feedback_schema}}
```

Assert:
- `active_steering` renders natural-language guidance
- `required_output_schema` renders expanded JSON without `$ref`
- `feedback_schema` renders only for stages whose contracts support feedback

- [ ] **Step 4: Add a real-template render test sweep for all non-render stages**

Update `tests/question_generator/test_assembler.py` to render every real non-render stage template with one prepared shared state and assert:
- rendering succeeds
- no unresolved Mustache tags remain
- no `## Relevant Context` / whole-section state block appears
- any `[CONDITIONAL ...]` markers are balanced by matching `[/CONDITIONAL]`
- no old placeholders remain:
  - `{{current_state}}`
  - `{{required_output}}`
  - `{{feedback}}`
- `required_output_schema` is present and expanded
- `active_steering` appears only for stages that include it

- [ ] **Step 5: Update review-artifact tests for the new Mustache prompt shape**

Update `tests/question_generator/test_non_render_prompt_quality.py` to assert generated review prompt files:
- contain no unresolved Mustache tags
- contain no whole-section legacy context blocks
- render repeated list/object sections successfully
- still contain expanded required-output schemas
- preserve readable `[CONDITIONAL condition=\"...\"]` wrappers where templates use them

- [ ] **Step 6: Update CLI expectations**

Update `tests/question_generator/test_cli.py` so the non-render CLI test expects the Mustache-rendered prompt shape and does not require whole-section context output.

- [ ] **Step 7: Run the focused tests and confirm they fail before implementation**

Run through the Conda-managed Python environment:

```bash
conda run -n <repo-conda-env> python -m unittest \
  tests.question_generator.test_assembler \
  tests.question_generator.test_non_render_prompt_quality \
  tests.question_generator.test_cli -v
```

Expected:
- FAIL because the assembler still uses the older placeholder/block model

- [ ] **Step 8: Commit**

```bash
git add tests/question_generator/test_assembler.py tests/question_generator/test_non_render_prompt_quality.py tests/question_generator/test_cli.py
git commit -m "test: lock mustache prompt rendering behavior"
```

## Chunk 2: Implement Mustache Rendering Over A Prepared Stage Context

### Task 2: Replace non-render block interpolation with Mustache rendering

**Files:**
- Modify: `tools/question_generator/assembler.py`
- Modify: `tools/question_generator/state_resolution.py`
- Modify: `tools/question_generator/state_rendering.py`

- [ ] **Step 1: Add the Mustache dependency and document it**

Choose one lightweight Python Mustache library and wire it into the repo’s environment expectations.

Requirements:
- lightweight
- no custom logic extensions needed
- supports dotted names and sections

Document the dependency location if the repo already has a dependency manifest or environment file. If there is no manifest yet, record the requirement clearly in the relevant docs during this chunk.

- [ ] **Step 2: Build one stage render context in `assembler.py`**

Prepare a context object shaped like:

```python
{
    **shared_state,
    "required_output_schema": <expanded JSON schema>,
    "feedback_schema": <expanded JSON schema or empty>,
    "active_steering": <rendered prose block>,
}
```

Guidance:
- shared state stays top-level so templates can use paths like
  `routing.time_horizon`
- contract-derived schemas are context values, not shared-state fields
- `active_steering` remains the one temporary pre-rendered prose field

- [ ] **Step 3: Define Mustache-safe rendering rules for structured values**

Make a clear decision for how Mustache receives:
- expanded schemas
- `active_steering`
- raw shared-state lists and objects

Recommended approach:
- pass ordinary shared-state dicts/lists as structured values so Mustache sections can iterate them
- pass expanded schemas as JSON strings ready for direct insertion
- pass `active_steering` as a markdown string ready for direct insertion

Do not introduce:
- custom Mustache helpers
- custom filters
- template functions

- [ ] **Step 3a: Define the conditional block prompt convention**

Document and apply the non-Mustache wrapper convention for optional context:

```md
For any input marked `[CONDITIONAL]`, use it only if you strongly believe the
stated condition is met for the current task.
If the condition is not clearly met, ignore that input entirely.
Do not force conditional inputs into the analysis just because they are
provided.
```

And:

```md
[CONDITIONAL condition="..."]
...
[/CONDITIONAL]
```

Requirements:
- the assembler does not evaluate these conditions
- templates must keep the condition text plain-language and stage-usable
- related optional fields should be grouped into one readable block

- [ ] **Step 4: Replace the old non-render placeholder path**

Update `tools/question_generator/assembler.py` so non-render stage rendering:
- uses Mustache against the prepared context
- does not append legacy whole-section context blocks
- does not depend on `{{current_state}}`, `{{required_output}}`, or `{{feedback}}`

Keep render-stage compatibility only if the render template still depends on broader context handling.

- [ ] **Step 5: Narrow `state_resolution.py` and `state_rendering.py`**

Update:
- `tools/question_generator/state_resolution.py`
- `tools/question_generator/state_rendering.py`

So they no longer drive non-render prompt content.

Acceptable outcomes:
- render-only support remains
- or the files become compatibility utilities for render until render is migrated

Do not leave dead non-render code paths silently injecting whole sections.

- [ ] **Step 6: Run the focused tests and make them pass**

Run:

```bash
conda run -n <repo-conda-env> python -m unittest \
  tests.question_generator.test_assembler \
  tests.question_generator.test_non_render_prompt_quality \
  tests.question_generator.test_cli -v
```

Expected:
- PASS for the focused Mustache rendering tests

- [ ] **Step 7: Commit**

```bash
git add tools/question_generator/assembler.py tools/question_generator/state_resolution.py tools/question_generator/state_rendering.py tests/question_generator/test_assembler.py tests/question_generator/test_non_render_prompt_quality.py tests/question_generator/test_cli.py
git commit -m "feat: render non-render prompts with mustache"
```

## Chunk 3: Rewrite Non-Render Templates Against The Compact Dependency Map

### Task 3: Replace whole-section context usage with readable Mustache templates

**Files:**
- Modify: `prompt/question-generator/stages/01-routing.md`
- Modify: `prompt/question-generator/stages/02-boundary.md`
- Modify: `prompt/question-generator/stages/03-structure.md`
- Modify: `prompt/question-generator/stages/04-scenarios.md`
- Modify: `prompt/question-generator/stages/05-question-generation.md`
- Modify: `prompt/question-generator/stages/06-evidence-planning.md`
- Modify: `prompt/question-generator/stages/07-decision-logic.md`
- Modify: `prompt/question-generator/stages/08-signal-translation.md`
- Modify: `prompt/question-generator/stages/09-monitoring.md`
- Test: `tests/question_generator/test_assembler.py`

- [ ] **Step 1: Rewrite `01-routing.md`**

Keep routing mostly topic-driven.
Use:
- `{{topic}}`
- `{{required_output_schema}}`

Do not include `active_steering`.

- [ ] **Step 2: Rewrite `02-boundary.md`**

Inline only the compact routing fields it needs:
- `routing.time_horizon`
- `routing.unit_of_analysis`
- `routing.assumptions`

Use readable grouped subsections instead of raw key-value dumps.
Use `[CONDITIONAL]` blocks for:
- `routing.desired_output`

- [ ] **Step 3: Rewrite `03-structure.md`**

Inline only:
- routing: `task`, `domain`, `time_horizon`, `unit_of_analysis`
- boundary: `exact_object_of_analysis`, `core_system`

Keep the prompt readable and compact.
Use `[CONDITIONAL]` blocks for:
- `routing.assumptions`
- `boundary.adjacent_systems`
- `boundary.out_of_scope_factors`
- `boundary.scope_assumptions`

- [ ] **Step 4: Rewrite `04-scenarios.md`**

Inline only:
- routing: `time_horizon`
- boundary: `exact_object_of_analysis`, `core_system`
- structure: `decisive_stakeholders`, `incentives`, `constraints`, `causal_mechanism`, `killer_variables`, `bottlenecks`

Use Mustache sections for:
- `alternative_scenarios`
- any repeated string lists that improve readability

Use `[CONDITIONAL]` blocks for:
- `boundary.adjacent_systems`
- `structure.threshold_variables`
- `structure.scarce_resources`
- `structure.stakeholders`

- [ ] **Step 5: Rewrite `05-question-generation.md`**

Inline only:
- routing: `time_horizon`, `unit_of_analysis`
- structure: `decisive_stakeholders`, `constraints`, `causal_mechanism`, `killer_variables`, `bottlenecks`
- scenarios: `base_case.summary`, `base_case.branch_points`, `base_case.branch_triggers`

Retain:
- `active_steering`
- `required_output_schema`
- `feedback_schema` if the stage still uses feedback

Use `[CONDITIONAL]` blocks for:
- `boundary.exact_object_of_analysis`
- `boundary.core_system`
- `boundary.scope_assumptions`
- `structure.threshold_variables`
- `structure.scarce_resources`
- `structure.stakeholders`

- [ ] **Step 6: Rewrite `06-evidence-planning.md`**

Inline only:
- questions: `top_killer_questions`, `evidence`, `evidence_mode_specific`, `uncertainty_mode_specific`
- scenarios: `base_case.branch_points`, `base_case.branch_triggers`

Use Mustache sections for:
- repeated question lists
- `question_to_evidence_mapping` if included

Use `[CONDITIONAL]` blocks for:
- `questions.decision_mode_specific`
- `questions.output_mode_specific`
- `routing.decision_mode`
- `routing.decision_context`
- `routing.risk_tolerance`
- `structure.causal_mechanism`
- `structure.killer_variables`
- `structure.bottlenecks`

- [ ] **Step 7: Rewrite `07-decision-logic.md`**

Inline only:
- routing: `decision_context`, `risk_tolerance`, `time_horizon`
- scenarios: `base_case.probability_logic`, `base_case.reversibility`, `base_case.decision_mode_implications`, `base_case.branch_triggers`
- evidence plan: `evidence_hierarchy`, `preferred_source_types`, `conflict_resolution_rules`, `question_to_evidence_mapping`
- uncertainty map: all needed fields

Retain:
- `active_steering`
- `required_output_schema`

Use `[CONDITIONAL]` blocks for:
- `questions.top_killer_questions`
- `boundary.exact_object_of_analysis`
- `boundary.scope_assumptions`
- `structure.killer_variables`
- `structure.bottlenecks`
- `structure.causal_mechanism`

- [ ] **Step 8: Rewrite `08-signal-translation.md`**

Inline only:
- questions: `top_killer_questions`
- evidence plan: `preferred_source_types`, `backup_source_types`, `conflict_resolution_rules`, `question_to_evidence_mapping`
- scenarios: `base_case.branch_points`, `base_case.branch_triggers`

Use Mustache sections for:
- repeated questions
- repeated evidence mappings

Use `[CONDITIONAL]` blocks for:
- `decision_logic.triggers`
- `decision_logic.hedge_exit_kill_criteria`
- `decision_logic.appropriate_evidence_threshold`
- `structure.killer_variables`
- `structure.threshold_variables`
- `structure.bottlenecks`
- `uncertainty_map.task_material_uncertainties`

- [ ] **Step 9: Rewrite `09-monitoring.md`**

Inline only:
- signals
- uncertainty_map.task_material_uncertainties

Use Mustache sections for:
- `signals`
- `monitoring.what_to_watch` if present in the prompt design

Use `[CONDITIONAL]` blocks for:
- `decision_logic.triggers`
- `decision_logic.hedge_exit_kill_criteria`
- `scenarios.base_case.branch_triggers`
- `scenarios.alternative_scenarios`
- `evidence_plan.preferred_source_types`
- `evidence_plan.backup_source_types`

- [ ] **Step 10: Run the non-render assembler tests**

Run:

```bash
conda run -n <repo-conda-env> python -m unittest tests.question_generator.test_assembler -v
```

Expected:
- PASS with all non-render prompts rendering cleanly and no whole-section context blocks

- [ ] **Step 11: Commit**

```bash
git add prompt/question-generator/stages/01-routing.md prompt/question-generator/stages/02-boundary.md prompt/question-generator/stages/03-structure.md prompt/question-generator/stages/04-scenarios.md prompt/question-generator/stages/05-question-generation.md prompt/question-generator/stages/06-evidence-planning.md prompt/question-generator/stages/07-decision-logic.md prompt/question-generator/stages/08-signal-translation.md prompt/question-generator/stages/09-monitoring.md tests/question_generator/test_assembler.py
git commit -m "refactor: rewrite non-render prompts as mustache templates"
```

## Chunk 4: Refresh Artifacts, Examples, And Runtime Docs

### Task 4: Update generated artifacts and documentation to match the Mustache model

**Files:**
- Modify: `tests/question_generator/assemble_non_render_prompts.py`
- Modify: `tests/question_generator/non_render_prompt_quality.md`
- Modify: `prompt/question-generator/README.md`
- Modify: `prompt/question-generator/IMPLEMENTATION.md`
- Modify: `prompt/question-generator/examples/07-decision-logic.assembled.example.md`
- Modify: `tests/question_generator/test_examples.py`

- [ ] **Step 1: Regenerate non-render prompt artifacts**

Run:

```bash
conda run -n <repo-conda-env> python tests/question_generator/assemble_non_render_prompts.py \
  --output-dir tests/question_generator/artifacts/non_render_prompt_review_prompts \
  --manifest tests/question_generator/artifacts/non_render_prompt_review_manifest.json \
  --seed 20260313
```

Confirm generated prompt files:
- contain no unresolved Mustache tags
- contain no `## Relevant Context`
- still contain expanded schemas

- [ ] **Step 2: Refresh the assembled example**

Regenerate or manually refresh:
- `prompt/question-generator/examples/07-decision-logic.assembled.example.md`

so it reflects the new Mustache-rendered inline field style rather than whole-section context blocks.

- [ ] **Step 3: Update README authoring guidance**

In `prompt/question-generator/README.md`, document:
- Mustache as the model-facing template format
- the prepared stage render context
- `required_output_schema`
- `feedback_schema`
- `active_steering` as the one temporary exception
- the `[CONDITIONAL condition=\"...\"] ... [/CONDITIONAL]` prompt convention
- the removal of whole-section non-render context rendering

- [ ] **Step 4: Update implementation documentation**

In `prompt/question-generator/IMPLEMENTATION.md`, update:
- prompt assembly flow
- template/render-context description
- compact dependency map status
- conditional block convention
- testing guidance for per-template render tests

- [ ] **Step 5: Update example tests**

Update `tests/question_generator/test_examples.py` to match the refreshed assembled example and prompt shape.

- [ ] **Step 6: Run the full question-generator test suite**

Run:

```bash
conda run -n <repo-conda-env> python -m unittest \
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

- [ ] **Step 7: Commit**

```bash
git add tests/question_generator/assemble_non_render_prompts.py tests/question_generator/non_render_prompt_quality.md prompt/question-generator/README.md prompt/question-generator/IMPLEMENTATION.md prompt/question-generator/examples/07-decision-logic.assembled.example.md tests/question_generator/test_examples.py tests/question_generator/artifacts/non_render_prompt_review_prompts tests/question_generator/artifacts/non_render_prompt_review_manifest.json
git commit -m "docs: align prompt assembly with mustache templates"
```

## Chunk 5: Re-Run Prompt Quality Review After Noise Reduction

### Task 5: Validate the new Mustache-rendered non-render prompts with the review workflow

**Files:**
- Modify: `tests/question_generator/artifacts/non_render_prompt_review.json` (if storing a baseline)
- Test: `tests/question_generator/check_non_render_prompt_review.py`

- [ ] **Step 1: Regenerate the non-render review prompt set**

Run:

```bash
conda run -n <repo-conda-env> python tests/question_generator/assemble_non_render_prompts.py \
  --output-dir tests/question_generator/artifacts/non_render_prompt_review_prompts \
  --manifest tests/question_generator/artifacts/non_render_prompt_review_manifest.json \
  --seed 20260313
```

- [ ] **Step 2: Run the external reviewer on each non-render prompt**

Use:
- `tests/question_generator/non_render_prompt_review_prompt.md`

Have the reviewer evaluate each generated prompt file separately and return one JSON array covering all nine non-render stages.

- [ ] **Step 3: Validate the reviewer output**

Run:

```bash
conda run -n <repo-conda-env> python tests/question_generator/check_non_render_prompt_review.py --input tests/question_generator/artifacts/non_render_prompt_review.json
```

Expected:
- `QUALITY REVIEW PASS`

- [ ] **Step 4: Compare reviewer findings to the old whole-section prompts**

Confirm qualitatively that:
- context usefulness improved
- context efficiency improved
- output readiness remained strong or improved
- no new input-precedence confusion was introduced

- [ ] **Step 5: Commit**

```bash
git add tests/question_generator/artifacts/non_render_prompt_review.json
git commit -m "test: refresh non-render prompt quality baseline"
```

Plan complete and saved to `docs/superpowers/plans/2026-03-13-field-level-prompt-substitution.md`. Ready to execute?
