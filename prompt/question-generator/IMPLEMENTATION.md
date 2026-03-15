# Question Generator Assembler Implementation

This document explains the current implementation of the question-generator
stage assembler. It focuses on:
- architecture
- prompt assembly flow
- contract and state design
- adapter and output-mode resolution
- implementation choices and tradeoffs
- current limitations

This is the implementation reference for the Python runtime under:
- `tools/question_generator/`

## Purpose

The assembler exists to turn the modular question-generator assets into a
runtime prompt for one workflow stage at a time.

The system now supports two adjacent responsibilities:
- assemble one prompt for one workflow stage
- manage an external-session stage workflow with persisted run artifacts

The assembler's job is:
- take the current shared state
- take a target stage
- load the matching stage template
- load the matching stage contract
- load the routed adapter and output-mode files that matter for that stage
- render all of that into one final prompt string

In short:

`state + stage + contracts + routed modules -> assembled stage prompt`

The current orchestrator helper supports:
- initializing a run directory with a copied `shared_state.json`
- loading a JSON recipe that defines stage order
- preparing a stage prompt into `stages/<stage-stub>/prompt.md`
- preparing a per-stage `response.schema.json`
- automatically invoking a fresh ephemeral Codex answering session for one stage
- storing the raw model reply and parsed JSON payload
- storing `codex.stdout.jsonl` and `codex.stderr.txt`
- merging only contract-owned state sections back into `shared_state.json`

The answering-session execution policy is fixed:
- model: `gpt-5.4`
- reasoning effort: `high`
- session lifetime: ephemeral, one stage per session

This keeps the orchestrator and the stage-answering model as two separate Codex
sessions while removing manual handoff steps.

## High-Level Architecture

The implementation has four layers.

### 1. Modular prompt assets

These are the authored prompt documents:
- conceptual host prompt and top-level design reference:
  - `prompt/question-generator/question-generator-modular.md`
- runtime stage templates:
  - `prompt/question-generator/stages/`
- adapters:
  - `prompt/question-generator/adapters/`
- output-mode guidance:
  - `prompt/question-generator/output-modes/`
- runtime render subtemplates:
  - `prompt/question-generator/stages/render/`

These files define the actual prompt content and domain logic.

### 2. Contracts and shared state

These are the machine-readable control files:
- stage contracts:
  - `prompt/question-generator/contracts/`
- shared state schema:
  - `prompt/question-generator/contracts/shared_state_schema.json`
- implementation notes:
  - `prompt/question-generator/contracts/implementation-notes.md`

Contracts are the assembly authority. They define:
- required upstream stage dependencies
- optional upstream stage dependencies
- adapter-dimension dependencies
- written state entities
- output schema
- feedback schema, when supported

### 3. Python runtime

The runtime lives under:
- `tools/question_generator/`

It resolves files, parses contracts, renders state, resolves adapters,
assembles prompts, manages run artifacts, and launches the ephemeral
stage-answering Codex subprocess.

### 4. Tests

Tests live under:
- `tests/question_generator/`

The test suite verifies pathing, contract parsing, state resolution, state
rendering, adapter resolution, adapter rendering, prompt assembly, CLI
behavior, and the worked example.

### `orchestrator.py`

File:
- `tools/question_generator/orchestrator.py`

Responsibilities:
- initialize one run directory
- load one workflow recipe
- persist a copied `shared_state.json`
- prepare one stage prompt into stage-local artifacts
- prepare one stage response schema artifact for JSON-returning stages
- build the pinned `codex exec --ephemeral` command for the answering session
- invoke one disposable answering session per stage
- persist subprocess stdout and stderr artifacts
- persist raw stage responses for all stages and parsed stage responses for JSON-returning stages
- merge only the stage-owned shared-state sections
- execute a full multi-stage workflow by iterating the recipe entries

Key implementation choices:
- prompt and reply artifacts live outside the shared-state schema
- response parsing accepts either plain JSON or fenced JSON blocks
- the response schema passed to Codex is derived from the contract output schema for JSON-returning stages
- `Render` returns plain text, so it does not pass `--output-schema` at execution time
- merge behavior is controlled by contract ownership, not by ad hoc field lists
- the answering session is created and destroyed automatically per stage run

## Runtime Modules

### `pathing.py`

File:
- `tools/question_generator/pathing.py`

Responsibilities:
- resolve repository root
- resolve prompt root
- map canonical stage names to stage template files
- map canonical stage names to contract files
- map adapter dimensions and routed values to module files
- normalize stage names and routed values

Key implementation choices:
- The repo root is computed from the module location rather than the current
  working directory. This makes the runtime less fragile when called from
  different directories.
- Stage names are normalized into canonical identifiers like
  `question_generation` and `signal_translation`.
- Stage template naming and contract naming are intentionally separate because
  two contracts use legacy file names:
  - `09-monitoring.contract.json`
  - `10-render.contract.json`

### `models.py`

File:
- `tools/question_generator/models.py`

Responsibilities:
- define the typed dataclasses used by the runtime

Current models:
- `OptionalRead`
- `Feedback`
- `OutputSchema`
- `StageContract`
- `ResolvedModule`

Key implementation choice:
- The runtime uses simple frozen dataclasses instead of a heavier validation
  library. The current target is dependency-light and fully compatible with the
  `truth-seek` Conda environment without extra packages.

### `contracts.py`

File:
- `tools/question_generator/contracts.py`

Responsibilities:
- load stage contracts from disk
- validate required top-level keys
- parse contract JSON into `StageContract`

Key implementation choices:
- Contracts are validated for required top-level keys at load time:
  - `stage`
  - `depends_on`
  - `writes`
  - `output_format`
  - `feedback`
  - `output_schema`
- The parser keeps both typed fields and the raw payload.
- The loader is intentionally minimal right now. It validates structure that the
  assembler depends on directly, not every possible schema detail.

### `state_resolution.py`

File:
- `tools/question_generator/state_resolution.py`

Responsibilities:
- convert stage-level dependencies into actual shared-state sections

The key map is `STAGE_TO_STATE_SECTIONS`.

Examples:
- `question_generation -> questions`
- `evidence_planning -> evidence_plan`, `uncertainty_map`
- `decision_logic -> decision_logic`, `synthesis`
- `signal_translation -> signals`

Key implementation choices:
- The assembler works in terms of stage dependencies, but the shared state is
  organized by owned entities. This module is the bridge between those two
  models.
- Required and optional reads are handled separately.
- Optional reads are included only if the caller explicitly selects them.
- `Render` no longer depends on whole-state resolution for prompt assembly.

Why this mapping exists:
- Contracts describe workflow dependencies in stage terms.
- Prompt rendering needs concrete state entities.
- Keeping the translation in one place avoids spreading stage-to-state logic
  across the assembler.

### `state_rendering.py`

File:
- `tools/question_generator/state_rendering.py`

Responsibilities:
- render resolved state sections into readable markdown blocks

Current format:
- readable section rendering for diagnostic or fallback use
- one section renderer per top-level shared-state section when available
- JSON fallback for sections without a specialized renderer

Key implementation choices:
- The renderer is registry-driven through
  `tools/question_generator/renderers/registry.py`.
- Specialized section renderers summarize the most useful fields first while
  keeping headings stable and prompt-friendly.
- Unknown sections still fall back to the legacy JSON block rendering so new
  sections can be added incrementally.
- Non-render stages no longer depend on `state_rendering.py` for prompt
  assembly. They now inline only the fields their Mustache templates reference.
- `Render` also no longer depends on `state_rendering.py` for prompt assembly.
  It now receives an explicit output-mode-selected context instead.

Tradeoff:
- readable section renderers remain useful for diagnostics and examples.
- stage prompts stay less noisy because they no longer receive whole state
  sections by default.

## Proposed Compact Field-Level Dependency Map

This section records the current field-level dependency target for non-render
prompt assembly.

Goal:
- reduce prompt noise by selecting only the stage fields that materially help
  the current stage
- move from whole-section inclusion toward field-level selection
- keep adapter-conditional expansion explicit rather than passing everything by
  default

This is the current authoring target for non-render stage templates.
The runtime still resolves dependencies from contracts at the section level,
but templates should inline only the specific fields they need through
Mustache.

Conditional input policy:
- required fields should appear normally in the prompt
- conditionally useful fields may still be included, but should be grouped into
  explicit prompt blocks marked with `[CONDITIONAL ...]` and `[/CONDITIONAL]`
- the model, not the assembler, should decide whether those conditional inputs
  materially apply
- after `Routing`, templates should not directly inject adapter-selection
  routing fields such as `task`, `domain`, `output_mode`, `evidence_mode`,
  `uncertainty_mode`, or `decision_mode`; the impact of those classifications
  should come through the stage's adapter guidance instead

Recommended template-level instruction:

```md
For any input marked `[CONDITIONAL]`, use it only if you strongly believe the
stated condition is met for the current task.
If the condition is not clearly met, ignore that input entirely.
Do not force conditional inputs into the analysis just because they are
provided.
```

Recommended block shape:

```md
[CONDITIONAL condition="Use this only if action depends on mechanism details rather than scenario summaries."]
...
[/CONDITIONAL]
```

### 1. Routing

Adapters that affect this stage:
- none

Prior-stage fields required:
- none

Output fields produced here that later stages commonly consume:
- `task`
- `domain`
- `output_mode`
- `evidence_mode`
- `uncertainty_mode`
- `decision_mode`
- `time_horizon`
- `unit_of_analysis`
- `assumptions`

Common downstream extras:
- `decision_context`
- `risk_tolerance`
- `desired_output`
- `classification_rationales` when auditability matters

### 2. Boundary

Adapters that should affect this stage:

Required:
- `task`
- `domain`

Conditional:
- `output_mode`
  Use when output form narrows scope, especially `Monitoring Dashboard`,
  `Scenario Tree`, or `Deep-Research Prompt`.
- `uncertainty_mode`
  Use when the selected mode is `Hidden-Variable Dominated` or
  `Regime-Shift Dominated` and scope may need to widen.
- `decision_mode`
  Use when the selected mode is `Portfolio Construction`, `Adversarial Game`,
  or `Optionality / Staged Commitment` and the object of action may differ.

Prior-stage fields required:

From `routing`:
- `time_horizon`
- `unit_of_analysis`
- `assumptions`

Prior-stage fields conditionally required:

From `routing`:
- `desired_output` when the user has already fixed a deliverable shape

### 3. Structure

Adapters that should affect this stage:

Required:
- `task`
- `domain`

Conditional:
- `uncertainty_mode`
  Use when hidden drivers, deception, regime shift, sparse data, or high noise
  should alter structural confidence.
- `decision_mode`
  Use when action-relevant structure matters, especially
  `Portfolio Construction`, `Adversarial Game`, or
  `Optionality / Staged Commitment`.
- `evidence_mode`
  Use when structural claims should stay close to the selected proof style.

Prior-stage fields required:

From `routing`:
- `time_horizon`
- `unit_of_analysis`

From `boundary`:
- `exact_object_of_analysis`
- `core_system`

Prior-stage fields conditionally required:

From `routing`:
- `assumptions` when scope and ontology are fragile

From `boundary`:
- `adjacent_systems` when cross-system mechanisms matter
- `out_of_scope_factors` when contamination risk is high
- `scope_assumptions` when structure needs explicit inherited scope discipline

### 4. Scenarios

Adapters that should affect this stage:

Required:
- `task`
- `domain`
- `uncertainty_mode`

Conditional:
- `decision_mode`
  Especially relevant because each scenario requires
  `decision_mode_implications`.
- `evidence_mode`
  Use when the scenario set should be narrowed to evidencable branches.
- `output_mode`
  Use when the selected output is explicitly `Scenario Tree` or
  `Monitoring Dashboard`.

Prior-stage fields required:

From `routing`:
- `time_horizon`

From `boundary`:
- `exact_object_of_analysis`
- `core_system`

From `structure`:
- `decisive_stakeholders`
- `incentives`
- `constraints`
- `causal_mechanism`
- `killer_variables`
- `bottlenecks`

Prior-stage fields conditionally required:

From `boundary`:
- `adjacent_systems` when scenario branches cross into neighboring systems

From `structure`:
- `threshold_variables` when branch points are threshold-driven
- `scarce_resources` when endurance or depletion matters
- `stakeholders` when non-decisive actors still affect path branching

### 5. Question Generation

Adapters that should affect this stage:
- all six adapters

Reason:
- the schema requires `task_specific`, `domain_specific`,
  `output_mode_specific`, `evidence_mode_specific`,
  `uncertainty_mode_specific`, and `decision_mode_specific`

Required:
- `task`
- `domain`
- `output_mode`
- `evidence_mode`
- `uncertainty_mode`
- `decision_mode`

Prior-stage fields required:

From `routing`:
- `time_horizon`
- `unit_of_analysis`

From `structure`:
- `decisive_stakeholders`
- `constraints`
- `causal_mechanism`
- `killer_variables`
- `bottlenecks`

From `scenarios`:
- `base_case.summary`
- `base_case.branch_points`
- `base_case.branch_triggers`
- `alternative_scenarios[].summary`
- `alternative_scenarios[].branch_points`
- `alternative_scenarios[].branch_triggers`

Prior-stage fields conditionally required:

From `boundary`:
- `exact_object_of_analysis`
- `core_system`
- `scope_assumptions`
  Use when scope is still ambiguous or multiple workflow passes may have caused
  drift.

From `structure`:
- `threshold_variables` when questions need to target branch thresholds
- `scarce_resources` when endurance or capacity questions matter
- `stakeholders` when broader stakeholder questioning is needed beyond decisive actors

### 6. Evidence Planning

Adapters that should affect this stage:

Required:
- `evidence_mode`
- `uncertainty_mode`

Conditional:
- `task`
- `domain`
- `decision_mode`

Prior-stage fields required:

From `questions`:
- `top_killer_questions`
- `evidence`
- `evidence_mode_specific`
- `uncertainty_mode_specific`

From `scenarios`:
- `base_case.branch_points`
- `base_case.branch_triggers`
- `alternative_scenarios[].branch_points`
- `alternative_scenarios[].branch_triggers`

Prior-stage fields conditionally required:

From `questions`:
- `decision_mode_specific` when evidence sufficiency is tied to stage gates or action gating
- `output_mode_specific` when downstream output requires a more explicit evidence rationale

From `routing`:
- `decision_context`
- `risk_tolerance`

From `structure`:
- `causal_mechanism`
- `killer_variables`
- `bottlenecks`
  Use when source choice should be mechanism-aware rather than just question-aware

### 7. Decision Logic

Adapters that should affect this stage:

Required:
- `decision_mode`
- `uncertainty_mode`

Conditional:
- `task`
- `evidence_mode`
- `domain`

Prior-stage fields required:

From `routing`:
- `decision_context`
- `risk_tolerance`
- `time_horizon`

From `scenarios`:
- `base_case.probability_logic`
- `base_case.reversibility`
- `base_case.decision_mode_implications`
- `base_case.branch_triggers`
- `alternative_scenarios[].probability_logic`
- `alternative_scenarios[].reversibility`
- `alternative_scenarios[].decision_mode_implications`
- `alternative_scenarios[].branch_triggers`

From `evidence_plan`:
- `evidence_hierarchy`
- `preferred_source_types`
- `conflict_resolution_rules`
- `question_to_evidence_mapping`

From `uncertainty_map`:
- `reducible_unknowns`
- `partially_reducible_unknowns`
- `irreducible_uncertainties`
- `task_material_uncertainties`

Prior-stage fields conditionally required:

From `questions`:
- `top_killer_questions`
  Use when action is explicitly gated by unresolved questions.

From `boundary`:
- `exact_object_of_analysis`
- `scope_assumptions`
  Use when action scope is still ambiguous.

From `structure`:
- `killer_variables`
- `bottlenecks`
- `causal_mechanism`
  Use when the action rule depends on mechanism or bottleneck details rather
  than scenario summaries alone.

### 8. Signal Translation

Adapters that should affect this stage:

Required:
- `evidence_mode`
- `uncertainty_mode`

Conditional:
- `decision_mode`
- `task`
- `domain`
- `output_mode`

Prior-stage fields required:

From `questions`:
- `top_killer_questions`

From `evidence_plan`:
- `preferred_source_types`
- `backup_source_types`
- `conflict_resolution_rules`
- `question_to_evidence_mapping`

From `scenarios`:
- `base_case.branch_points`
- `base_case.branch_triggers`
- `alternative_scenarios[].branch_points`
- `alternative_scenarios[].branch_triggers`

Prior-stage fields conditionally required:

From `decision_logic`:
- `triggers`
- `hedge_exit_kill_criteria`
- `appropriate_evidence_threshold`
  Use when signals should change action, not just belief.

From `structure`:
- `killer_variables`
- `threshold_variables`
- `bottlenecks`
  Use when signals should map directly to bottlenecks or threshold variables.

From `uncertainty_map`:
- `task_material_uncertainties`
  Use when signals should explicitly reduce dominant uncertainty.

### 9. Monitoring

Adapters that should affect this stage:

Required:
- `task`
- `uncertainty_mode`

Conditional:
- `decision_mode`
- `evidence_mode`
- `output_mode`
- `domain`

Prior-stage fields required:

From `signals`:
- `signal`
- `preferred_evidence_source`
- `backup_evidence_source`
- `cadence`
- `thresholds`
- `update_rules`
- `belief_update_implications`
- `confidence_under_current_uncertainty_mode`
- `changes_action_vs_belief`

From `uncertainty_map`:
- `task_material_uncertainties`

Prior-stage fields conditionally required:

From `decision_logic`:
- `triggers`
- `hedge_exit_kill_criteria`
  Use when monitoring should trigger adds, trims, stops, or hedges.

From `scenarios`:
- `base_case.branch_triggers`
- `alternative_scenarios[].branch_triggers`
  Use when monitoring should explicitly track competing paths.

From `evidence_plan`:
- `preferred_source_types`
- `backup_source_types`
  Use when monitoring cadence or source preference should reflect source
  hierarchy, not just signal-level defaults.

### 10. Render

`output_mode` is required to choose the render subtemplate, but it should not
also render as a `Stage Guidance` item. Render subtemplates own their own
adapter guidance.

`Render` now differs from the analytical stages in one more important way:
- it returns the final deliverable as plain text
- it does not return a JSON state update
- it does not write back into shared state

That means:
- no runtime `--output-schema` constraint for `Render`
- no JSON-only answering wrapper for `Render`
- no required `response.schema.json` artifact for `Render`
- no `response.parsed.json` artifact for `Render`

The render contract should still remain the source of truth for:
- adapter dependencies via `depends_on`
- wrapper-only reads
- output-mode-specific subtemplate reads
- write behavior via `writes`
- compatibility metadata via `output_schema`, even though `Render` no longer
  uses that schema at execution time

Current render-specific contract keys:
- `reads_required_common`
  - wrapper-only reads used by `prompt/question-generator/stages/10-render.md`
- `reads_by_output_mode`
  - subtemplate-only reads keyed by canonical output-mode name

Important rule:
- `reads_required_common` is for the wrapper only
- `reads_by_output_mode` is for the selected subtemplate only
- overlap is allowed
- the runtime resolves these declarations from the render contract and then
  builds the Mustache context from the declared wrapper and subtemplate read
  sets rather than from a hardcoded Python dependency map

Per-subtemplate adapter guidance:

- `Research Memo`
  - required: `domain`, `evidence_mode`, `uncertainty_mode`
  - conditional: `decision_mode`
- `Decision Memo`
  - required: `decision_mode`, `uncertainty_mode`
  - conditional: `evidence_mode`
- `Monitoring Dashboard`
  - required: `uncertainty_mode`, `decision_mode`
  - conditional: `evidence_mode`, `domain`
- `Scenario Tree`
  - required: `uncertainty_mode`, `decision_mode`
  - conditional: `domain`
- `Deep-Research Prompt`
  - required: `evidence_mode`, `uncertainty_mode`, `decision_mode`
  - conditional: `domain`
- `Investment Worksheet`
  - required: `evidence_mode`, `uncertainty_mode`, `decision_mode`
  - conditional: `domain`

Common framing fields useful across output modes and appropriate for
`reads_required_common`:

From `routing`:
- `question`
- `explicit_constraints`
- `desired_output`
- `decision_context`
- `risk_tolerance`
- `time_horizon`
- `unit_of_analysis`
- `assumptions`

Prior-stage fields required by common output mode and appropriate for
`reads_by_output_mode`:

If `output_mode = Research Memo`:

From `boundary`:
- `exact_object_of_analysis`
- `core_system`
- `adjacent_systems`
- `out_of_scope_factors`
- `scope_assumptions`

From `structure`:
- `stakeholders`
- `decisive_stakeholders`
- `incentives`
- `constraints`
- `causal_mechanism`
- `killer_variables`
- `bottlenecks`
- `threshold_variables`
- `scarce_resources`

From `scenarios`:
- `base_case.name`
- `base_case.summary`
- `base_case.branch_points`
- `base_case.branch_triggers`
- `base_case.reversibility`
- `base_case.probability_logic`
- `base_case.decision_mode_implications`
- `alternative_scenarios[].name`
- `alternative_scenarios[].summary`
- `alternative_scenarios[].branch_points`
- `alternative_scenarios[].branch_triggers`
- `alternative_scenarios[].reversibility`
- `alternative_scenarios[].probability_logic`
- `alternative_scenarios[].decision_mode_implications`

From `questions`:
- `top_killer_questions`
- `clarifying`
- `structural`
- `stakeholder`
- `evidence`
- adapter-specific question buckets when they materially sharpen the memo:
  - `task_specific`
  - `domain_specific`
  - `output_mode_specific`
  - `evidence_mode_specific`
  - `uncertainty_mode_specific`
  - `decision_mode_specific`

From `evidence_plan`:
- `evidence_hierarchy`
- `preferred_source_types`
- `backup_source_types`
- `conflict_resolution_rules`
- `question_to_evidence_mapping`

From `signals`:
- `signal`
- `linked_question`
- `cadence`
- `thresholds`
- `changes_action_vs_belief`
  Use as an optional compact monitoring layer when the memo should end with
  watch items.

From `decision_logic`:
- `appropriate_evidence_threshold`
- `triggers`
  Use when the memo should explicitly translate research into action
  implications.

From `uncertainty_map`:
- `reducible_unknowns`
- `partially_reducible_unknowns`
- `irreducible_uncertainties`
- `task_material_uncertainties`
  Use when the memo needs an explicit uncertainty section or a stronger
  `What Would Change the Conclusion` ending.

If `output_mode = Decision Memo`:

From `decision_logic`:
- `must_know_before_action`
- `can_learn_after_action`
- `appropriate_evidence_threshold`
- `reversibility_logic`
- `sizing_logic`
- `staging_logic`
- `hedge_exit_kill_criteria`
- `triggers`

From `scenarios`:
- `base_case.probability_logic`
- `base_case.reversibility`
- `base_case.decision_mode_implications`
- `base_case.branch_triggers`
- `alternative_scenarios[].probability_logic`
- `alternative_scenarios[].reversibility`
- `alternative_scenarios[].decision_mode_implications`
- `alternative_scenarios[].branch_triggers`

From `evidence_plan`:
- `evidence_hierarchy`
- `question_to_evidence_mapping`

From `uncertainty_map`:
- `reducible_unknowns`
- `partially_reducible_unknowns`
- `irreducible_uncertainties`
- `task_material_uncertainties`

From `synthesis`:
- `recommendation_or_action_frame`
- `why_now_or_why_not_now`
- `what_must_be_true`
- `key_risks_and_failure_modes`

From `questions`:
- `top_killer_questions`

From `monitoring`:
- `what_to_monitor_next`

If `output_mode = Monitoring Dashboard`:

From `monitoring`:
- `what_to_watch`
- `signal_most_reducing_dominant_uncertainty`
- `signal_most_likely_to_change_action`
- `what_to_monitor_next`

From `signals`:
- `signal`
- `linked_question`
- `preferred_evidence_source`
- `backup_evidence_source`
- `cadence`
- `thresholds`
- `update_rules`
- `belief_update_implications`
- `confidence_under_current_uncertainty_mode`
- `changes_action_vs_belief`

From `decision_logic`:
- `triggers`
- `hedge_exit_kill_criteria`
  Use when the dashboard should imply action thresholds, not just observation.

From `scenarios`:
- `base_case.branch_triggers`
- `alternative_scenarios[].branch_triggers`
  Use when the dashboard should show path competition.

From `routing`:
- `uncertainty_mode`
- `decision_mode`
  Use when the dashboard should explicitly name the dominant modes.

From `uncertainty_map`:
- `task_material_uncertainties`
  Use when the dashboard should end with a stronger `What Would Change the
  Conclusion` section.

If `output_mode = Scenario Tree`:

From `scenarios`:
- `base_case.name`
- `base_case.summary`
- `base_case.branch_points`
- `base_case.branch_triggers`
- `base_case.reversibility`
- `base_case.probability_logic`
- `base_case.decision_mode_implications`
- `alternative_scenarios[].name`
- `alternative_scenarios[].summary`
- `alternative_scenarios[].branch_points`
- `alternative_scenarios[].branch_triggers`
- `alternative_scenarios[].reversibility`
- `alternative_scenarios[].probability_logic`
- `alternative_scenarios[].decision_mode_implications`

From `structure`:
- `causal_mechanism`
- `killer_variables`
- `threshold_variables`

From `boundary`:
- `exact_object_of_analysis`
- `core_system`
- `scope_assumptions`
  Use when the tree needs explicit scope framing.

From `signals`:
- `signal`
- `thresholds`
- `update_rules`
- `changes_action_vs_belief`
  Use when the tree should show monitoring triggers or branch-confirmation rules.

From `evidence_plan`:
- `question_to_evidence_mapping`
  Use when the tree should include `Evidence That Would Raise / Lower Each
  Scenario`.

From `signals`:
- `belief_update_implications`
  Use when the tree should include `Evidence That Would Raise / Lower Each
  Scenario`.

From `uncertainty_map`:
- `reducible_unknowns`
- `partially_reducible_unknowns`
- `irreducible_uncertainties`
- `task_material_uncertainties`
  Use when the tree should include `Confidence and Key Unknowns` or
  `What Would Change the Conclusion`.

If `output_mode = Deep-Research Prompt`:

From `boundary`:
- `exact_object_of_analysis`
- `core_system`
- `adjacent_systems`
- `out_of_scope_factors`
- `scope_assumptions`

From `structure`:
- `stakeholders`
- `decisive_stakeholders`
- `incentives`
- `constraints`
- `causal_mechanism`
- `killer_variables`
- `bottlenecks`
- `threshold_variables`
- `scarce_resources`

From `scenarios`:
- `base_case.name`
- `base_case.summary`
- `base_case.branch_points`
- `base_case.branch_triggers`
- `base_case.reversibility`
- `base_case.probability_logic`
- `base_case.decision_mode_implications`
- `alternative_scenarios[].name`
- `alternative_scenarios[].summary`
- `alternative_scenarios[].branch_points`
- `alternative_scenarios[].branch_triggers`
- `alternative_scenarios[].reversibility`
- `alternative_scenarios[].probability_logic`
- `alternative_scenarios[].decision_mode_implications`

From `questions`:
- `top_killer_questions`
- `clarifying`
- `structural`
- `stakeholder`
- `evidence`
- `task_specific`
- `domain_specific`
- `output_mode_specific`
- `evidence_mode_specific`
- `uncertainty_mode_specific`
- `decision_mode_specific`

From `evidence_plan`:
- `evidence_hierarchy`
- `preferred_source_types`
- `backup_source_types`
- `conflict_resolution_rules`
- `question_to_evidence_mapping`

From `uncertainty_map`:
- `reducible_unknowns`
- `partially_reducible_unknowns`
- `irreducible_uncertainties`
- `task_material_uncertainties`

If `output_mode = Investment Worksheet`:

From `structure`:
- `causal_mechanism`
- `decisive_stakeholders`
- `killer_variables`
- `bottlenecks`

From `scenarios`:
- `base_case.probability_logic`

From `questions`:
- `top_killer_questions`

From `evidence_plan`:
- `evidence_hierarchy`

From `decision_logic`:
- `must_know_before_action`
- `reversibility_logic`
- `sizing_logic`
- `staging_logic`
- `triggers`

From `synthesis`:
- `recommendation_or_action_frame`
- `why_now_or_why_not_now`
- `what_must_be_true`

From `signals`:
- `signal`
- `changes_action_vs_belief`

From `uncertainty_map`:
- `task_material_uncertainties`

Archived v7 section coverage for render is documented in:
- `docs/superpowers/specs/2026-03-14-render-output-mode-subtemplates-design.md`

### `adapter_resolution.py`

File:
- `tools/question_generator/adapter_resolution.py`

Responsibilities:
- resolve the contract's adapter-dimension dependencies into concrete files
  using the `routing` block

Key implementation choices:
- `depends_on` stores adapter dimensions, not resolved file paths.
- The actual routed values come from `state["routing"]`.
- `Routing` itself resolves no modules, because routing defines the adapter
  selections rather than consuming them.
- `output_mode` is resolved from `output-modes/`, while the other dimensions are
  resolved from `adapters/`.

This separation matters:
- contracts define what a stage depends on in general
- routing defines what this specific run selected

### `adapter_rendering.py`

File:
- `tools/question_generator/adapter_rendering.py`

Responsibilities:
- render stage guidance for the current stage

Current format:
- one `## Stage Guidance` section
- one wrapper heading per resolved adapter dimension
- one stage-specific extracted steering block

Key implementation choices:
- Wrapper headings are generated by code, not stored redundantly in each
  adapter.
- Adapter assets are now structured JSON files, one type per adapter family.
- The renderer loads the stage's guidance entry directly from the adapter's
  `stage_guidance` object.
- For non-render stages, the renderer prepares structured `stage_guidance`
  entries split into `required` and `conditional`.
- Output-mode files are treated differently:
  - `Render` receives the full output-mode document
  - non-render stages receive a short moderate note that keeps them aligned to
    the eventual deliverable without pulling final-format section outlines into
    upstream analysis stages

Why output mode is special:
- output modes are authored as deliverable definitions rather than stage-style
  relevance adapters
- we still want them available during assembly, especially for `Render` and
  decision-oriented stages

Tradeoff:
- full output-mode injection remains simple and transparent for `Render`
- upstream stages avoid prompt confusion from seeing final-deliverable section
  lists in the middle of analytical work

Planned direction:
- migrate adapter assets to structured JSON
- keep `## Stage Guidance` as the only adapter-derived prompt section in the
  first migration
- store the rest of the adapter metadata in JSON without rendering it into
  stage prompts by default
- use clearer prompt-facing importance labels:
  - `Important`
  - `Moderate`
  - `Light`
  - `None`
- include one short line under `## Stage Guidance` explaining that each item’s
  label indicates how strongly it should shape the stage result

Recommended structured adapter shape:
- use one JSON type per adapter family rather than one generic adapter object
- recommended families:
  - `task_adapter`
    - `value`
    - `prioritize`
    - `stage_guidance`
  - `domain_adapter`
    - `value`
    - `typical_ontology`
    - `typical_bottlenecks`
    - `typical_signals`
    - `stage_guidance`
  - `evidence_mode_adapter`
    - `value`
    - `prioritize`
    - `strengths`
    - `weaknesses`
    - `stage_guidance`
  - `uncertainty_mode_adapter`
    - `value`
    - `research_behavior`
    - `risk`
    - `stage_guidance`
  - `decision_mode_adapter`
    - `value`
    - `use_when`
    - `research_behavior`
    - `key_questions`
    - `action_logic`
    - `monitoring_style`
    - `failure_mode`
    - `stage_guidance`
- reusable shared structure:
  - `stage_guidance`
    - keyed by canonical stage name
    - each entry contains:
      - `importance`
      - `guidance`

Important prompt-use rule:
- in the first JSON migration, only `stage_guidance` should appear in prompts
- the other adapter metadata should remain available for future prompt design,
  debugging, and routing support, but should not be dumped into prompts yet
- conditionally relevant adapter guidance should use the same
  `[CONDITIONAL condition="..."] ... [/CONDITIONAL]` wrapper convention as
  conditional state/context blocks

### `assembler.py`

File:
- `tools/question_generator/assembler.py`

Responsibilities:
- orchestrate the full prompt assembly for one stage

Current assembly flow:
1. load the stage template
2. load the stage contract
3. expand the contract output schema, and feedback schema when present
4. resolve required and selected optional state sections from the shared state
5. resolve the routed modules
6. branch by stage type:
   - non-render: prepare one Mustache render context and render the template
   - render: use the compatibility section-rendering path
7. return one markdown prompt string

Key implementation choices:
- The assembler is intentionally a renderer, not a workflow executor.
- It does not call the model.
- It does not validate model output.
- It does not merge state updates.
- Non-render prompt templating uses `chevron` Mustache rendering rather than a
  custom placeholder engine.
- The render context is prepared in Python, but prompt wording and layout stay
  in the stage template.
- `stage_guidance` remains the one adapter-derived prompt section for
  non-render stages.

Those behaviors are left to a future orchestrator.

Why this split was chosen:
- prompt assembly and workflow execution are different concerns
- prompt debugging is easier when assembly can be run independently
- it keeps the current implementation testable without introducing model or API
  dependencies

Supported non-render Mustache context values:
- shared-state values are exposed at the top level:
  - `{{routing.time_horizon}}`
  - `{{routing.decision_context}}`
  - `{{boundary.core_system}}`
  - `{{scenarios.base_case.summary}}`
  - `{{questions.top_killer_questions}}`
- `{{{topic}}}` -> markdown-safe rendered topic block
- `{{#stage_guidance.required}} ... {{/stage_guidance.required}}` -> required
  guidance entries prepared for the template
- `{{#stage_guidance.conditional}} ... {{/stage_guidance.conditional}}` ->
  conditionally relevant guidance entries prepared for the template
- `{{{required_output_schema}}}` -> rendered output-schema block with `$ref`
  entries expanded
- `{{{feedback_schema}}}` -> rendered feedback-schema block with `$ref`
  entries expanded when supported

Conditional blocks in non-render templates:
- are plain authored markdown, not Mustache helpers
- should wrap readable field groups that the model may or may not use
- rely on the template’s own instruction text plus the top-level
  `[CONDITIONAL]` rule rather than orchestration-time reasoning

Render-stage Mustache context values:
- `{{{topic}}}` -> markdown-safe rendered topic block
- `{{render_mode}}` -> selected output mode
- `{{routing.*}}` -> compact routing and framing fields
- `{{{render_body}}}` -> the already-rendered output-mode-selected body template
- `{{#stage_guidance.required}} ... {{/stage_guidance.required}}` -> required
  guidance entries
- `{{#stage_guidance.conditional}} ... {{/stage_guidance.conditional}}` ->
  conditionally relevant guidance entries
- `{{{required_output_schema}}}` -> rendered output-schema block with `$ref`
  entries expanded
- `{{{feedback_schema}}}` -> rendered feedback-schema block with `$ref`
  entries expanded when supported

### `cli.py`

File:
- `tools/question_generator/cli.py`

Responsibilities:
- expose prompt assembly from the command line

Parameters:
- `--stage`
- `--state`
- `--include-optional` (repeatable)

Important behavioral note:
- the bare `--stage ... --state ...` CLI mode assembles a prompt
- workflow subcommands handle stage execution separately

That means:
- input: current shared state JSON
- output: the assembled prompt for the requested stage

That invocation mode is best understood as a stage prompt generator. The same
CLI module also exposes workflow commands for end-to-end orchestration.

## Data Model

## Shared State

The shared state schema lives at:
- `prompt/question-generator/contracts/shared_state_schema.json`

It is the durable pre-render state for the workflow and now composes one schema
file per top-level section from
`prompt/question-generator/contracts/state-sections/`.

Main sections:
- `topic`
- `routing`
- `boundary`
- `structure`
- `scenarios`
- `questions`
- `evidence_plan`
- `uncertainty_map`
- `decision_logic`
- `synthesis`
- `signals`
- `monitoring`

Key implementation choice:
- `rendered_output` was removed from durable state

Why:
- render is a terminal formatting stage
- render should consume state, not write new analysis state back into it

## Routing Block

The `routing` block serves two jobs:
- formalize the raw user input into a normalized problem frame
- hold the routed values used for adapter resolution

This is why `routing` contains both:
- user/problem framing fields:
  - `question`
  - `explicit_constraints`
  - `desired_output`
  - `risk_tolerance`
  - `decision_context`
  - `time_horizon`
  - `unit_of_analysis`
  - `assumptions`
- routed classifications:
  - `task`
  - `secondary_task`
  - `domain`
  - `secondary_domain`
  - `output_mode`
  - `secondary_output_mode`
  - `evidence_mode`
  - `secondary_evidence_mode`
  - `uncertainty_mode`
  - `secondary_uncertainty_mode`
  - `decision_mode`
  - `secondary_decision_mode`
  - `classification_rationales`

Key implementation choice:
- routed adapter dependencies are not stored separately in state

Why:
- contracts already define which adapter dimensions each stage depends on
- state only needs to store the resolved routed values

## Contract Design

Each stage contract contains:
- `stage`
- `reads_required`
- `reads_optional`
- `depends_on`
- `writes`
- `output_format`
- `feedback`
- `output_schema`

Implementation note:
- non-render stage contracts keep an inline outer `output_schema` object but
  now reuse shared section schemas inside `properties` via `$ref`

### `reads_required`

Required upstream stage dependencies.

Example:
- `Decision Logic` requires `routing`, `scenarios`, and `evidence_planning`

### `reads_optional`

Optional upstream stage dependencies that may be included by the caller.

Each optional read has:
- `stage`
- `kind`
- `when`

Current `kind` values:
- `user_requirement`
- `situation`

Why optional reads exist:
- some stages can work with a minimal upstream set
- some stages become stronger when more context is explicitly included
- feedback loops can make downstream context relevant during stage re-entry

### `depends_on`

Adapter-dimension dependencies for the stage.

Important design decision:
- `depends_on` stores dimensions, not resolved adapter files

Example:
```json
["task", "domain", "output_mode", "evidence_mode", "uncertainty_mode", "decision_mode"]
```

At runtime:
- the contract says what dimensions matter
- the routing block supplies the selected values
- the resolver finds the actual files

### `writes`

Top-level state entities owned by the stage.

### `output_schema`

The required JSON output shape for the stage.

Key implementation choice:
- contracts, not deleted guidance files, are now the source of truth for output
  shape

Why:
- the assembler needs machine-readable output requirements
- validation belongs closer to the contract than to prose documentation

## Prompt Assembly Flow

For a stage like `decision_logic`, the runtime currently does this:

1. load `07-decision-logic.contract.json`
2. load `07-decision-logic.md`
3. expand `output_schema` and `feedback.schema` so the prompt sees concrete
   JSON shapes rather than local `$ref` pointers
4. resolve required and selected optional state sections
5. resolve routed modules from `routing`
6. prepare a Mustache render context containing:
   - top-level shared-state entities
   - `topic`
   - `stage_guidance`
   - `required_output_schema`
   - `feedback_schema`, when supported
7. render the template with Mustache
8. return one markdown prompt string

This gives a prompt shaped like:
- stage instructions and working rules
- only the specific upstream fields the template references
- stage guidance, when the stage depends on routed modules
- expanded required output schema
- expanded feedback schema, when supported

## Why We Chose Markdown Templates Plus Code

We considered a heavier prompt IR and a custom substitution system. The current
implementation uses markdown templates plus a minimal Mustache renderer for
both non-render stages and render-stage subtemplates.

Reasons:
- the authored prompt assets already exist as markdown documents
- contracts already provide structured machine-readable metadata
- state is already structured JSON
- Mustache gives us variable substitution and list sections without turning
  templates into little programs
- a separate prompt IR would add abstraction without solving a concrete current
  problem

So the implementation treats prompt assembly as:
- prepare a stage-specific render context in Python
- let the template decide what context to show and in what order
- render the prompt through Mustache

not:
- compile a new intermediate language first

## Design Decisions and Tradeoffs

### Contracts are the assembly authority

Decision:
- use contracts, not prose docs, to drive dependency resolution and output
  expectations

Why:
- machine-readable
- testable
- usable by the assembler directly
- easier to keep synchronized with runtime behavior

Tradeoff:
- requires discipline to keep contracts current when stage semantics change

### State is durable and pre-render

Decision:
- keep only durable research state in the shared state schema

Why:
- downstream stages need reusable structured outputs
- render should not write new analysis state

Tradeoff:
- the shared state schema must evolve when stage outputs grow richer

### Optional reads are caller-selected

Decision:
- the assembler does not interpret `reads_optional[].when`

Why:
- those fields are explanatory metadata
- deciding which optional reads to include is orchestration policy

Tradeoff:
- a future orchestrator must make those choices explicitly

### Adapter headings are rendered in code

Decision:
- keep wrapper phrasing in code
- keep substantive steering in adapter documents

Why:
- avoids duplicated framing text across adapter files
- gives consistent prompt wording across dimensions

Tradeoff:
- if we want more stage-specific heading nuance later, the renderer logic will
  need to grow

### State is rendered as JSON blocks

Decision:
- render current state as readable headings plus JSON

Why:
- transparent
- faithful to the actual state shape
- easy to debug during development

Tradeoff:
- less polished than a prose summarizer

## Current Limitations

The current implementation does not yet include:
- a full orchestrator that calls the model
- output validation against the contract after model execution
- state merge logic
- automatic feedback-loop execution
- stage-aware output-mode extraction comparable to adapter stage extraction
- richer prose summarization of state sections

This means the current runtime is best described as:
- a stage prompt assembler

not:
- the only entry point for the workflow; orchestration helpers also support
  end-to-end automated stage execution

## How To Use It

Environment:
```bash
conda activate truth-seek
```

Assemble a stage prompt:
```bash
conda run -n truth-seek python -m tools.question_generator.cli \
  --stage routing \
  --state research-state/problems/iran_war.json
```

Include optional stage dependencies:
```bash
conda run -n truth-seek python -m tools.question_generator.cli \
  --stage decision_logic \
  --state tests/question_generator/fixtures/minimal_state.json \
  --include-optional structure \
  --include-optional question_generation
```

What happens:
- the CLI prints the assembled prompt to stdout

Workflow commands also support:
- run initialization from an existing state file or raw topic
- automatic stage execution through fresh ephemeral Codex sessions
- response parsing and validation for JSON-returning stages
- contract-owned state merge back into `shared_state.json`

## Testing

Run the suite in the intended environment:

```bash
conda run -n truth-seek python -m unittest discover -s tests -p 'test_*.py' -v
```

The tests currently cover:
- path resolution
- contract loading
- state resolution
- state rendering
- adapter resolution
- adapter rendering
- assembled prompt shape
- CLI behavior
- example prompt consistency

## Recommended Next Step

The next major piece should be an orchestrator that:
- assembles the prompt for a stage
- calls the model
- validates output against the contract
- merges the returned state update
- manages feedback loops

That layer should sit on top of the current assembler rather than replacing it.
