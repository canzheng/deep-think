# Repository Guidance

The source of truth for the question generator is:
- `prompt/question-generator/question-generator-modular.md`

Modular components live under:
- `prompt/question-generator/adapters/`
- `prompt/question-generator/output-modes/`

Stage prompt templates live under:
- `prompt/question-generator/stages/`

Stage input/output contracts live under:
- `prompt/question-generator/contracts/`

The shared state template lives at:
- `prompt/question-generator/contracts/shared_state_schema.json`

Rules:
- Stage prompt templates must remain consistent with the modular generator source.
- If the modular generator changes, update affected stage templates and contracts.
- The renderer must use the shared state file as its sole analysis input.
- Feedback loops are orchestrator-controlled; stage prompts may request feedback but should not jump stages themselves.
- Always run Python commands through the Conda-managed environment instead of the system Python so dependency resolution stays consistent.
- Contracts are the source of truth for stage dependencies, adapter
  dependencies, and output schemas.
- Canonical workflow stage names are:
  `Routing`, `Boundary`, `Structure`, `Scenarios`, `Question Generation`,
  `Evidence Planning`, `Decision Logic`, `Signal Translation`, `Monitoring`,
  `Render`.
- Adapter stage-guidance importance levels must use only: `Important`,
  `Moderate`, `Light`, or `None`.
