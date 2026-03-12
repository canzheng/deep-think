This directory contains the modular question-generator source of truth.

Implementation reference:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/IMPLEMENTATION.md`

Shared state reference:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/shared_state_reference.md`

Current scope:
- modular source prompt
- stage prompt templates
- adapter files
- stage contracts
- shared state template
- python assembler runtime
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
  - `state-sections/`
  - `implementation-notes.md`
- python runtime:
  - `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/`

Consistency rules:
- Stage templates under `stages/` are the canonical stage prompt sources and
  must stay consistent with `question-generator-modular.md`.
- Contracts under `contracts/` define the state slices each stage may read and
  write, their adapter dependencies, their output schemas, and the shared state
  template.
- Adapter stage relevance must use the canonical workflow stage names:
  `Routing`, `Boundary`, `Structure`, `Scenarios`, `Question Generation`,
  `Evidence Planning`, `Decision Logic`, `Signal Translation`, `Monitoring`,
  `Render`.
- Adapter influence levels must use only: `Primary`, `Modulating`, `Light`,
  or `None`.
- If a change lands in the modular source prompt, update the affected task
  templates and contracts in the same change.

Environment setup (run these from the repository root):
```bash
conda env create -f environment.yml
conda activate truth-seek
```
The current assembler target is dependency-light and relies on the Python
standard library plus `unittest`.

Assembler runtime:
- stage pathing and contract loading:
  - `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/pathing.py`
  - `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/contracts.py`
- state and adapter resolution:
  - `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/state_resolution.py`
  - `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/state_rendering.py`
  - `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/adapter_resolution.py`
  - `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/adapter_rendering.py`
- prompt assembly:
  - `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/assembler.py`
- CLI:
  - `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/cli.py`

Assembly model:
- stage template supplies the core prompt body
- stage template may explicitly place assembler-provided placeholders
- contract supplies required and optional stage dependencies, adapter
  dependencies, and output schema
- shared state supplies the routed context and prior stage outputs
- routed adapters supply stage-specific steering

Supported template placeholders:
- `{{topic}}` -> a markdown-safe rendered topic block from shared state
- `{{current_state}}` -> the rendered `Relevant Context` block
- `{{active_steering}}` -> the rendered `Stage Guidance` block
- `{{required_output}}` -> the rendered output-schema block
- `{{feedback}}` -> the rendered feedback-schema block when supported

Placeholder fallback rule:
- if a template includes one of these placeholders, the assembler injects the
  matching content at that location
- if a template does not include a given block placeholder, the assembler
  appends that block after the template using the legacy order

Current prompt-facing assembly:
- `Relevant Context` renders the resolved shared-state sections for the stage
- `Stage Guidance` renders the routed adapter and output-mode guidance
- state rendering uses a section-renderer registry under
  `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/renderers/`
  with a JSON fallback for sections that do not yet have a specialized renderer
- `shared_state_schema.json` is a composed JSON Schema that references one
  schema file per top-level section under `contracts/state-sections/`
- stage contracts reuse those section schemas inside `output_schema.properties`
  via `$ref` where practical

CLI usage:
```bash
python -m tools.question_generator.cli \
  --stage decision_logic \
  --state tests/question_generator/fixtures/minimal_state.json \
  --include-optional structure \
  --include-optional question_generation
```
