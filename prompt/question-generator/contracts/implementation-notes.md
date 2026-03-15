# Implementation Notes

## Shared State Template

The shared state template now lives at:
- `prompt/question-generator/contracts/shared_state_schema.json`

This file is intended to hold durable pre-render research state. The goal is to
capture enough structured output from each stage that:
- downstream stages can consume prior work without re-deriving it
- contracts and state have a plausible landing place for stage-owned entities
- the render stage can treat the accumulated state as its sole analysis input

## Inclusion Decisions

### Included directly from guidance

The following guidance-level outputs were promoted into durable state because
they are useful to downstream reasoning, not just presentation:

- routing secondary classifications
- routing classification rationales
- boundary exact object of analysis and scope assumptions
- structure decisive stakeholders, threshold variables, and scarce resources
- scenario branch points, triggers, reversibility, probability logic, and
  decision-mode implications
- question families beyond the older minimal schema
- question metadata
- evidence hierarchy and question-to-evidence mapping
- uncertainty map as a first-class state section
- decision logic splits for reversibility, sizing, staging, and triggers
- synthesis as a first-class state section
- signal-level metadata
- monitoring as a first-class state section

### Included with reshaping

Some guidance items were kept but reshaped to better fit durable state:

- primary routed classifications stay in the canonical fields `task`, `domain`,
  `output_mode`, `evidence_mode`, `uncertainty_mode`, and `decision_mode`.
  Secondary classifications live in the corresponding `secondary_*` fields.
- `assumptions` stays as a single routing array rather than splitting into a
  separate `key_assumptions` field.
- `topic` is preserved as raw input, while `routing.question` is the normalized
  ask used by the workflow.
- `scenarios` remains one top-level section but is now structured as `base_case`
  plus `alternative_scenarios`.
- `questions` now uses category buckets with question objects rather than only
  flat string arrays.
- `top 3 killer questions` is stored as `top_killer_questions` rather than
  encoding the number in the field name.
- `evidence_plan` keeps source and mapping logic, while uncertainty-specific
  outputs moved into `uncertainty_map`.
- `decision_logic` keeps operational action logic, while concise conclusion
  framing lives in `synthesis`.
- `signals` and `monitoring` use structured item objects because the old flat
  arrays were too thin for later stages.

### Intentionally not kept in state

The following items were not kept as durable state:

- `rendered_output`
  - Render is a special terminal stage. It should consume the accumulated state
    rather than write new analysis state back into it.
- output-mode-specific final document schemas
  - Those belong to output-mode modules and render-time formatting, not the
    pre-render shared state.

## Contract Output Schemas

The contracts now carry explicit `output_schema` sections for each stage. Those
schemas mirror the durable pre-render entities owned by each stage in
`shared_state_schema.json`, while the render contract describes deliverable
expectations instead of new state writes.

This moves the detailed output expectations that previously lived only in
guidance into the contract layer, so stage assembly and validation can rely on
contracts for both ownership and output shape.
