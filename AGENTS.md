# Repository Guidance

The conceptual host prompt and top-level design reference for the question
generator is:
- `prompt/question-generator/question-generator-modular.md`

Prompt/design guidance modules live under:
- `prompt/question-generator/adapters/`
- `prompt/question-generator/output-modes/`

Runtime stage prompt templates live under:
- `prompt/question-generator/stages/`

Stage input/output contracts and shared state schemas live under:
- `prompt/question-generator/contracts/`

The shared state schema lives at:
- `prompt/question-generator/contracts/shared_state_schema.json`

Rules:
- Runtime stage prompt templates must remain consistent with the modular
  generator source.
- If the modular generator changes, update affected stage templates and contracts.
- The renderer must use only shared-state-derived context declared by the
  render contract as its analysis input.
- Feedback loops are orchestrator-controlled; stage prompts may request feedback but should not jump stages themselves.
- Always run Python commands through the Conda-managed environment instead of the system Python so dependency resolution stays consistent.
- Contracts are the source of truth for stage dependencies, adapter
  dependencies, and output schemas.
- Canonical user-facing workflow stage names are:
  `Routing`, `Boundary`, `Structure`, `Scenarios`, `Question Generation`,
  `Evidence Planning`, `Decision Logic`, `Signal Translation`, `Monitoring`,
  `Render`.
- Adapter `stage_guidance` JSON keys must use normalized runtime stage ids:
  `routing`, `boundary`, `structure`, `scenarios`, `question_generation`,
  `evidence_planning`, `decision_logic`, `signal_translation`, `monitoring`,
  `render`.
- Adapter stage-guidance importance levels must use only: `Important`,
  `Moderate`, `Light`, or `None`.
