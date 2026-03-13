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
- external-session orchestration helpers with run-artifact persistence
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
- `recipes/`
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
- Adapter stage-guidance importance levels must use only: `Important`,
  `Moderate`, `Light`, or `None`.
- If a change lands in the modular source prompt, update the affected task
  templates and contracts in the same change.

Environment setup (run these from the repository root):
```bash
conda env create -f environment.yml
conda activate truth-seek
```
The current assembler target is dependency-light and relies on the Python
standard library plus `chevron` and `unittest`.

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
- orchestration helpers:
  - `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/orchestrator.py`
- CLI:
  - `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/cli.py`

Assembly model:
- stage template supplies the core prompt body
- non-render stage templates are Mustache templates over a prepared stage render context
- contract supplies required and optional stage dependencies, adapter
  dependencies, and output schema
- shared state supplies the routed context and prior stage outputs
- routed adapters supply stage-specific guidance
- render currently remains a compatibility exception and still uses the broader section-rendering path

Supported non-render Mustache context values:
- `{{{topic}}}` -> a markdown-safe rendered topic block
- `{{routing.*}}`, `{{boundary.*}}`, `{{structure.*}}`, `{{scenarios.*}}`, etc. -> direct shared-state values
- `{{#stage_guidance.required}} ... {{/stage_guidance.required}}` -> required stage-guidance entries
- `{{#stage_guidance.conditional}} ... {{/stage_guidance.conditional}}` -> conditionally relevant stage-guidance entries
- `{{{required_output_schema}}}` -> the rendered output-schema block with `$ref` entries expanded
- `{{{feedback_schema}}}` -> the rendered feedback-schema block when supported, with `$ref` entries expanded

Non-render rendering rule:
- the assembler prepares one render context per stage
- the template decides what context appears in the final prompt
- the assembler does not append a large whole-section `Relevant Context` block for non-render stages

Current prompt-facing assembly:
- non-render prompts inline only the state fields their templates reference
- `Stage Guidance` is the only prompt-visible adapter section in the first structured-adapter migration
- stage-guidance entries use the prompt-facing importance labels `Important`, `Moderate`, `Light`, and `None`
- conditional adapter guidance uses the same `[CONDITIONAL condition="..."] ... [/CONDITIONAL]` wrapper convention as other conditional prompt blocks
- render still uses section rendering under
  `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/renderers/`
  with a JSON fallback for sections that do not yet have a specialized renderer
- assembled `Required Output` and `Feedback` blocks expand schema `$ref`
  entries before rendering so stage prompts see concrete JSON shapes
- `shared_state_schema.json` is a composed JSON Schema that references one
  schema file per top-level section under `contracts/state-sections/`
- stage contracts reuse those section schemas inside `output_schema.properties`
  via `$ref` where practical

Current orchestration behavior:
- a run can be initialized into its own artifact directory
- the live `shared_state.json` remains the sole analysis input passed between stages
- a JSON recipe can define an ordered multi-stage workflow
- each prepared stage writes its assembled `prompt.md` into a stage-specific artifact directory
- each prepared stage also writes `response.schema.json`
- automatic stage execution launches a fresh ephemeral Codex answering session
- that answering session always uses `gpt-5.4` with `high` reasoning effort
- each executed stage persists `codex.stdout.jsonl` and `codex.stderr.txt`
- each applied response writes both `response.raw.md` and `response.parsed.json`
- only contract-owned state sections are merged back into `shared_state.json`
- debug artifacts live beside shared state, not inside it

CLI usage:
```bash
conda run -n truth-seek python -m tools.question_generator.cli \
  --stage decision_logic \
  --state tests/question_generator/fixtures/minimal_state.json \
  --include-optional structure \
  --include-optional question_generation
```

Automatic stage workflow:
```bash
conda run -n truth-seek python -m tools.question_generator.cli init-run \
  --state tests/question_generator/fixtures/minimal_state.json \
  --output-dir tmp/question-runs \
  --run-id demo-run

conda run -n truth-seek python -m tools.question_generator.cli run-stage \
  --run-dir tmp/question-runs/demo-run \
  --stage decision_logic
```

Recipe workflow:
```bash
conda run -n truth-seek python -m tools.question_generator.cli run-recipe \
  --recipe prompt/question-generator/recipes/non-render.recipe.json \
  --state tests/question_generator/fixtures/minimal_state.json \
  --output-dir tmp/question-runs \
  --run-id demo-non-render
```

Manual debug workflow:
```bash
conda run -n truth-seek python -m tools.question_generator.cli prepare-stage \
  --run-dir tmp/question-runs/demo-run \
  --stage decision_logic

conda run -n truth-seek python -m tools.question_generator.cli apply-response \
  --run-dir tmp/question-runs/demo-run \
  --stage decision_logic \
  --response tmp/question-runs/demo-run/decision_logic.response.md
```
