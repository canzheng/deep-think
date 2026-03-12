This directory contains the modular question-generator source of truth.

Current scope:
- modular source prompt
- stage prompt templates
- stage guidance extracts
- adapter files
- stage contracts
- no assembler yet
- archived `v1`-`v7` prompts live under
  `/Users/canzheng/Work/sandbox/truth-seek/prompt/archived/`
- `question-generator-modular.md` is the modular host prompt that references
  these files and is the source of truth

Layout:
- `stages/`
- `adapters/tasks/`
- `adapters/domains/`
- `adapters/evidence-modes/`
- `adapters/uncertainty-modes/`
- `adapters/decision-modes/`
- `output-modes/`
- `contracts/`
  - `shared_state_schema.json`
  - `implementation-notes.md`

Consistency rules:
- Stage templates under `stages/` are the canonical stage prompt sources and
  must stay consistent with `question-generator-modular.md`.
- Guidance files under `stages/` are extracted from the `Reads`, `Writes`, and
  output sections of the stage templates.
- Contracts under `contracts/` define the state slices each stage may read and
  write, and also hold the shared state template.
- Adapter stage relevance must use the canonical workflow stage names:
  `Routing`, `Boundary`, `Structure`, `Scenarios`, `Question Generation`,
  `Evidence Planning`, `Decision Logic`, `Signal Translation`, `Monitoring`,
  `Render`.
- Adapter influence levels must use only: `Primary`, `Modulating`, `Light`,
  or `None`.
- If a change lands in the modular source prompt, update the affected task
  templates and contracts in the same change.
