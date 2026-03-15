# Render Output-Mode Subtemplates Design

**Status:** Draft working design

**Scope:** This document defines the next-stage architecture for the
`Render` stage of the question generator. It replaces the current
compatibility-path design with an output-mode-selected render template family
while preserving `Render` as one orchestration stage.

## 1. Purpose

`Render` is the stage that turns accumulated workflow state into the final user
artifact.

Unlike the non-render stages, `Render` is driven primarily by
`routing.output_mode`. A `Decision Memo`, `Monitoring Dashboard`,
`Scenario Tree`, and `Deep-Research Prompt` are not small variations of the
same deliverable. They are different final products with different prompt
shapes, different state needs, and different quality criteria.

The design goal is to make `Render` explicit about that difference instead of
continuing to treat it as:
- one broad state dump
- one compatibility template
- one output-mode document blob

## 2. Core Decision

Keep `Render` as one orchestration stage, but implement it as:
- one shared render context builder
- one output-mode-selected render subtemplate
- one thin common wrapper only where it adds real value

This means:
- the Python runtime chooses the correct render template based on
  `routing.output_mode`
- the model does not decide which render template to use
- prompt templates do not contain large internal mode-switching logic

## 3. Why This Design

This design is preferred over a single giant render template because:
- output modes are materially different deliverables
- prompt quality is easier to reason about when each mode has its own template
- tests can verify one render mode at a time
- output-mode-specific dependencies become auditable instead of hidden in
  broad context dumps

It is preferred over splitting `Render` into multiple workflow stages because:
- orchestration stays simple
- stage naming stays stable
- contracts remain centered on one terminal stage
- the distinction is template-selection logic, not workflow branching

## 4. Current State

Current implementation:
- `Render` now uses an output-mode-selected Mustache path in
  `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/assembler.py`
- `10-render.md` acts as the shared render wrapper
- output-mode-specific render bodies live under
  `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/render/`
- the legacy compatibility placeholders are no longer used in prompt assembly

What has already been modernized:
- `10-render.md` already has cleaner prompt-facing wording
- the docs now include an explicit output-mode dependency map for `Render`

## 5. Target Architecture

### 5.1. Stage Identity

`Render` remains a single workflow stage.

The orchestrator still sees only:
- `Render`

The internal render runtime then chooses one subtemplate based on:
- `routing.output_mode`

### 5.2. Template Selection

The Python runtime should:
1. read `routing.output_mode`
2. normalize it to the canonical output-mode name
3. map that mode to a render subtemplate path
4. build the corresponding render context
5. render the selected subtemplate

This control flow belongs in Python, not in Mustache templates.

### 5.3. Template Family

Recommended layout:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/10-render.md`
  - shared render wrapper, only if it continues to add real value
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/render/research-memo.md`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/render/decision-memo.md`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/render/monitoring-dashboard.md`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/render/scenario-tree.md`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/render/deep-research-prompt.md`

Preferred rule:
- use the shared wrapper only for content that is truly common across all
  output modes
- keep output-mode-specific wording and structure in the subtemplates

### 5.4. Render Context

`Render` should move to the same general assembly model as non-render stages:
- build one prepared render context
- render through Mustache

However, the render context differs from non-render stages because it is
selected by output mode.

The render context should contain:
- common routing/framing fields
- output-mode-specific analysis slices
- stage guidance
- required output schema
- feedback schema when supported

The context should not contain:
- one giant full-state markdown block
- hidden broad summaries that the template did not explicitly ask for

The render contract is the source of truth for render reads:
- `reads_required_common` declares wrapper-only reads
- `reads_by_output_mode` declares subtemplate-only reads keyed by canonical
  output-mode name
- overlap is allowed

The Python runtime should use those contract declarations to assemble the
render context rather than maintaining a separate hardcoded dependency map.

## 6. Render Inputs

### 6.1. Common Framing

These fields are useful across render modes:

From `routing`:
- `question`
- `explicit_constraints`
- `desired_output`
- `decision_context`
- `risk_tolerance`
- `time_horizon`
- `unit_of_analysis`
- `assumptions`

### 6.2. Adapter Influence

`output_mode` is required to select the render subtemplate, but it should not
also render as a `Stage Guidance` item. The chosen subtemplate already encodes
the output-mode-specific deliverable shape.

Render `Stage Guidance` should be owned by the selected subtemplate, not the
shared wrapper.

`Render` returns the final deliverable as plain text:
- no runtime `--output-schema` constraint
- no JSON-only answering wrapper
- no required `response.schema.json` or `response.parsed.json` artifact

Per-subtemplate adapter influence:

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

### 6.3. Output-Mode-Specific Inputs

The currently preferred mode-specific input map is:

#### Research Memo

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
- all scenario fields for `base_case`
- all scenario fields for `alternative_scenarios[]`

From `questions`:
- `top_killer_questions`
- `clarifying`
- `structural`
- `stakeholder`
- `evidence`
- adapter-specific question buckets when they materially sharpen the memo

From `evidence_plan`:
- `evidence_hierarchy`
- `preferred_source_types`
- `backup_source_types`
- `conflict_resolution_rules`
- `question_to_evidence_mapping`

Optional:
- compact `signals` layer when the memo should end with monitoring guidance
- `decision_logic.appropriate_evidence_threshold`
- `decision_logic.triggers` when the memo should translate research into action
- all uncertainty-map fields when the memo needs an explicit uncertainty section
  or a stronger `What Would Change the Conclusion` ending

#### Decision Memo

From `decision_logic`:
- all decision-logic fields

From `scenarios`:
- `probability_logic`
- `reversibility`
- `decision_mode_implications`
- `branch_triggers`
for `base_case` and `alternative_scenarios[]`

From `evidence_plan`:
- `evidence_hierarchy`
- `question_to_evidence_mapping`

From `uncertainty_map`:
- all uncertainty-map fields

From `synthesis`:
- all synthesis fields

Optional:
- `questions.top_killer_questions`
- `monitoring.what_to_monitor_next`

#### Monitoring Dashboard

From `monitoring`:
- all monitoring fields

From `signals`:
- all signal fields

Optional:
- `decision_logic.triggers`
- `decision_logic.hedge_exit_kill_criteria`
- scenario `branch_triggers` when competing paths should be shown
- `routing.uncertainty_mode` and `routing.decision_mode` when the deliverable
  should name the dominant modes explicitly
- `uncertainty_map.task_material_uncertainties` when the dashboard should end
  with a stronger `What Would Change the Conclusion` section

#### Scenario Tree

From `scenarios`:
- all scenario fields for `base_case`
- all scenario fields for `alternative_scenarios[]`

From `structure`:
- `causal_mechanism`
- `killer_variables`
- `threshold_variables`

Optional:
- `boundary.exact_object_of_analysis`
- `boundary.core_system`
- `boundary.scope_assumptions`
- signal trigger fields when the tree should also show monitoring logic
- `evidence_plan.question_to_evidence_mapping` and
  `signals.belief_update_implications` when the tree should include
  `Evidence That Would Raise / Lower Each Scenario`
- all uncertainty-map fields when the tree should include `Confidence and Key
  Unknowns` or `What Would Change the Conclusion`

#### Deep-Research Prompt

From `boundary`:
- all boundary fields

From `structure`:
- all structure fields

From `scenarios`:
- all scenario fields

From `questions`:
- all question buckets, especially `top_killer_questions`

From `evidence_plan`:
- all evidence-plan fields

From `uncertainty_map`:
- all uncertainty-map fields

#### Investment Worksheet

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

### 6.4. Archived v7 Coverage Table

This table maps archived v7 section-XII deliverable sections to current render
inputs. Coverage labels mean:

- `Direct`: the current shared state or adapter guidance maps cleanly
- `Approximate`: the section is supported, but only through a proxy field set
- `Missing`: no credible current source exists

| Output mode | v7 section(s) | Current source(s) | Coverage |
| --- | --- | --- | --- |
| Research Memo | System Boundary | `boundary.*` | Direct |
| Research Memo | Decisive Stakeholders; Causal Mechanism; Killer Variables / Bottlenecks | `structure.decisive_stakeholders`, `structure.causal_mechanism`, `structure.killer_variables`, `structure.bottlenecks` | Direct |
| Research Memo | Scenario Branches | `scenarios.base_case.*`, `scenarios.alternative_scenarios[]*` | Direct |
| Research Memo | Highest-Value Questions; Top 3 Killer Questions | `questions.structural`, `questions.evidence`, `questions.top_killer_questions` | Direct |
| Research Memo | Evidence Plan; Research Priorities | `evidence_plan.*`, `questions.top_killer_questions` | Direct |
| Research Memo | Uncertainty Map | `uncertainty_map.*` | Direct |
| Research Memo | Decision-Mode Implications | `scenarios.*.decision_mode_implications`, conditional `decision_mode` guidance | Direct |
| Research Memo | Signals to Watch | `signals.*` | Direct |
| Research Memo | What Would Change the Conclusion | `scenarios.*.branch_triggers`, `decision_logic.triggers`, `uncertainty_map.task_material_uncertainties`, `signals.thresholds` | Direct |
| Decision Memo | Decision to Be Made; Recommendation; Why Now / Why Not Now; What Must Be True; Key Risks / Failure Modes | `routing.question`, `synthesis.*` | Direct |
| Decision Memo | Decision Mode and Why It Fits | required `decision_mode` guidance | Direct |
| Decision Memo | Evidence Standard Required to Act | `decision_logic.appropriate_evidence_threshold`, conditional `evidence_mode` guidance | Direct |
| Decision Memo | Uncertainty That Can Be Reduced / Must Be Accepted | `uncertainty_map.*` | Direct |
| Decision Memo | Reversibility / Sizing / Staging Logic; Triggers | `decision_logic.reversibility_logic`, `sizing_logic`, `staging_logic`, `triggers`, `hedge_exit_kill_criteria` | Direct |
| Decision Memo | Top 3 Killer Questions; Evidence Plan; What to Monitor Next | `questions.top_killer_questions`, `evidence_plan.*`, `monitoring.what_to_monitor_next` | Direct |
| Decision Memo | What Would Change the Conclusion | `decision_logic.triggers`, `decision_logic.hedge_exit_kill_criteria`, `scenarios.*.branch_triggers`, `uncertainty_map.task_material_uncertainties` | Direct |
| Monitoring Dashboard | What Is Being Monitored; Core Thesis / Competing Paths | `boundary.exact_object_of_analysis`, `boundary.core_system`, `scenarios.base_case.summary`, `scenarios.alternative_scenarios[].summary` | Direct |
| Monitoring Dashboard | Signal Table; Evidence Source Preference; Escalation Triggers; Action Triggers | `signals.*`, `monitoring.what_to_watch[*]` | Direct |
| Monitoring Dashboard | Dominant Uncertainty Mode; Dominant Decision Mode | `routing.uncertainty_mode`, `routing.decision_mode`, required render guidance | Direct |
| Monitoring Dashboard | Noise to Ignore | `monitoring.what_to_watch[*].noise_to_ignore` | Direct |
| Monitoring Dashboard | Top 3 Killer Questions | `questions.top_killer_questions` | Direct |
| Monitoring Dashboard | What Would Change the Conclusion | `uncertainty_map.task_material_uncertainties`, `scenarios.*.branch_triggers` | Direct |
| Scenario Tree | Base Case; Alternative Scenarios; Branch Triggers; Probability Logic; Decision-Mode Implications by Scenario | `scenarios.base_case.*`, `scenarios.alternative_scenarios[]*` | Direct |
| Scenario Tree | Evidence That Would Raise / Lower Each Scenario | `evidence_plan.question_to_evidence_mapping`, `signals.belief_update_implications` | Approximate |
| Scenario Tree | Dominant Uncertainty Mode | required `uncertainty_mode` guidance | Direct |
| Scenario Tree | Signals to Watch | `signals.signal`, `signals.thresholds`, `signals.update_rules` | Direct |
| Scenario Tree | Top 3 Killer Questions | `questions.top_killer_questions` | Direct |
| Scenario Tree | Confidence and Key Unknowns; What Would Change the Conclusion | `uncertainty_map.*`, `scenarios.*.branch_triggers` | Direct |
| Investment Worksheet | Expression Type; Thesis Fit; Mechanism; Decisive Stakeholders; Killer Variables / Bottlenecks | `routing.question`, `synthesis.recommendation_or_action_frame`, `structure.causal_mechanism`, `structure.decisive_stakeholders`, `structure.killer_variables`, `structure.bottlenecks` | Direct |
| Investment Worksheet | Market-Implied View | `scenarios.base_case.probability_logic` | Approximate |
| Investment Worksheet | Evidence / Uncertainty / Decision Mode Rationale | `routing.evidence_mode`, `routing.uncertainty_mode`, `routing.decision_mode`, plus required render guidance | Direct |
| Investment Worksheet | Catalysts; Killer Questions; Monitoring Signals | `signals.signal`, `questions.top_killer_questions` | Direct |
| Investment Worksheet | Portfolio Role / Sizing / Staging; Verdict | `decision_logic.must_know_before_action`, `reversibility_logic`, `sizing_logic`, `staging_logic`, `synthesis.why_now_or_why_not_now` | Direct |
| Investment Worksheet | Conviction | `synthesis.what_must_be_true` | Approximate |
| Investment Worksheet | What Would Change the View | `decision_logic.triggers`, `uncertainty_map.task_material_uncertainties` | Direct |
| Deep-Research Prompt | Research Objective; Stakeholders to Analyze; Mechanisms to Test; Variables / Bottlenecks to Assess; Core Questions | `routing.question`, `structure.stakeholders`, `structure.causal_mechanism`, `structure.killer_variables`, `structure.bottlenecks`, `structure.threshold_variables`, `questions.*` | Direct |
| Deep-Research Prompt | Required Output | selected output-mode subtemplate instructions | Approximate |
| Deep-Research Prompt | Evidence Mode and Source Priorities; Uncertainty Mode and What It Implies; Decision Mode and What It Implies | `routing.evidence_mode`, `routing.uncertainty_mode`, `routing.decision_mode`, `evidence_plan.*`, `uncertainty_map.*`, `questions.decision_mode_specific`, required render guidance | Direct |
| Deep-Research Prompt | Signals / Evidence to Collect; Rules | `evidence_plan.*`, `routing.explicit_constraints`, `routing.assumptions`, `evidence_plan.conflict_resolution_rules` | Direct |
| Deep-Research Prompt | Final Prompt | render output itself | Direct |

## 7. Template Design Rules

Render subtemplates should:
- read like model-facing prompt instructions for one specific deliverable type
- inline only the fields needed for that output mode
- keep common framing compact
- avoid restating the entire workflow history
- own their own `Stage Guidance` blocks
- use conditional blocks where helpful

Render subtemplates should not:
- rely on a single giant state dump
- hardcode a universal deliverable outline across all output modes
- expose orchestration or repository internals

## 8. Runtime Design

The runtime should move from:
- `Render` compatibility placeholders

to:
- prepared render context
- selected render subtemplate
- Mustache render

Recommended Python responsibilities:
- choose render mode template
- prepare common framing
- prepare output-mode-specific fields
- prepare output-mode-specific `stage_guidance`
- expand output schema
- render prompt

The runtime should not:
- rely on template conditionals to choose the render mode
- force the model to infer the expected deliverable shape from unrelated
  context

## 9. Testing Strategy

Render needs its own deterministic template tests.

At minimum:
- one prepared shared-state fixture
- one render assembly test per output mode
- no unresolved Mustache tags
- expected mode-specific sections or values appear
- no legacy `Relevant Context` broad dump remains unless intentionally retained

Prompt quality review for `Render` should come later under a separate rubric.
Its quality criteria differ from non-render stages because it produces a final
artifact rather than an intermediate analytical state update.

## 10. Migration Strategy

Recommended order:
1. define the render context builder and template-selection map
2. create output-mode subtemplates
3. rewrite `10-render.md` into a thin common wrapper, or remove that wrapper if
   it adds no value
4. keep `Render` on the output-mode-selected Mustache path in `assembler.py`
5. update tests and examples
6. regenerate assembled artifacts

## 11. Open Questions

### 11.1. Keep A Common Wrapper Or Not?

The current recommendation is:
- keep a thin wrapper only if it holds genuinely shared instructions
- otherwise let each subtemplate be fully standalone

### 11.2. Should Output-Mode Guidance Stay As Raw Documents?

Today `Render` still receives the full output-mode document through the legacy
path.

The preferred long-term direction is:
- move output-mode prompt content into the selected render subtemplate family
- keep Python responsible only for selecting the mode and building the context

### 11.3. Should Render Get Its Own Review Gate?

Yes, eventually.

But that should happen after the runtime/template migration, because render
quality needs a deliverable-focused rubric rather than the current non-render
analytical-stage rubric.
