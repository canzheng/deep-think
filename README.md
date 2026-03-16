# Truth Seek

This repository contains prompt, contract, and runtime tooling for the `question-generator` workflow.

The main working area today is:
- [prompt/question-generator/README.md](prompt/question-generator/README.md)

## What This Repo Contains

- [prompt/question-generator/question-generator-modular.md](prompt/question-generator/question-generator-modular.md): conceptual host prompt and top-level design reference
- [prompt/question-generator/stages](prompt/question-generator/stages): runtime stage prompt templates
- [prompt/question-generator/adapters](prompt/question-generator/adapters): structured adapter content and stage guidance
- [prompt/question-generator/stages/render](prompt/question-generator/stages/render): runtime render subtemplates selected by `routing.output_mode`
- [prompt/question-generator/contracts](prompt/question-generator/contracts): stage contracts and shared-state schemas
- [tools/question_generator](tools/question_generator): Python assembler and orchestration runtime
- [tests/question_generator](tests/question_generator): unit tests, review prompts, and prompt artifacts
- [tmp/question-runs](tmp/question-runs): local run artifacts from end-to-end workflows

## How It Works

The question generator is a staged workflow:
- `Routing`
- `Boundary`
- `Structure`
- `Scenarios`
- `Question Generation`
- `Evidence Planning`
- `Decision Logic`
- `Signal Translation`
- `Monitoring`
- `Render`

For non-render stages, the runtime:
1. loads the stage template
2. prepares a Mustache render context from shared state, contract metadata, and stage guidance
3. assembles a prompt
4. sends that prompt to a model
5. validates the model output against the stage contract
6. merges the allowed fields back into `shared_state.json`

For `Render`, the runtime:
1. selects the render subtemplate under `prompt/question-generator/stages/render/`
2. builds the prompt context from shared-state fields declared in the render contract
3. renders the final deliverable directly as plain text without merging new state

The durable workflow state lives in one file shaped by:
- [shared_state_schema.json](prompt/question-generator/contracts/shared_state_schema.json)

Important:
- `shared_state_schema.json` is the schema contract for the live state
- it is not a starter instance file
- a topic-first run can begin from the minimal state `{"topic": "<raw user request>"}`

## Setup

Create the Conda environment:

```bash
conda env create -f environment.yml
conda activate truth-seek
```

Per repo guidance, run Python through the Conda-managed environment:

```bash
conda run -n truth-seek python -m unittest
```

## Common Commands

Assemble one stage prompt:

```bash
conda run -n truth-seek python -m tools.question_generator.cli \
  --stage decision_logic \
  --state tests/question_generator/fixtures/minimal_state.json
```

Run the full question-generator recipe:

```bash
conda run -n truth-seek python -m tools.question_generator.cli run-recipe \
  --recipe prompt/question-generator/recipes/non-render.recipe.json \
  --state tests/question_generator/fixtures/minimal_state.json \
  --output-dir tmp/question-runs \
  --run-id demo-workflow
```

Initialize a run directly from a raw topic:

```bash
conda run -n truth-seek python -m tools.question_generator.cli init-topic-run \
  --topic "Should Atlas expand into healthcare next quarter?" \
  --output-dir tmp/question-runs \
  --run-id atlas-healthcare
```

Run from a raw topic and stop after routing for user verification:

```bash
conda run -n truth-seek python -m tools.question_generator.cli run-topic \
  --topic "Should Atlas expand into healthcare next quarter?" \
  --recipe prompt/question-generator/recipes/non-render.recipe.json \
  --output-dir tmp/question-runs \
  --run-id atlas-healthcare \
  --pause-after-stage routing
```

Run the same workflow through the OpenClaw executor path:

```bash
conda run -n truth-seek python -m tools.question_generator.cli run-topic \
  --topic "Should Atlas expand into healthcare next quarter?" \
  --recipe prompt/question-generator/recipes/non-render.recipe.json \
  --output-dir tmp/question-runs \
  --run-id atlas-healthcare \
  --pause-after-stage routing \
  --executor-backend openclaw
```

Notes:
- prompt assembly and contracts stay unchanged
- JSON stages prefer OpenClaw `llm-task` when available
- otherwise they fall back to OpenClaw chat-completions with local validation

Refresh the self-contained OpenClaw bundle artifact:

```bash
conda run -n truth-seek python -m tools.question_generator.cli refresh-openclaw-package
```

Packaged OpenClaw bundle notes:
- the bundle lives under `skills/question-generator-skill/openclaw`
- it carries its own runtime, prompt assets, recipes, and vendored `chevron`
- it uses `python3` and does not require `conda`
- it persists JSON-stage executor choice in `config/runtime.json`
- bundled entrypoints are:
  - `python3 {baseDir}/scripts/run_topic.py ...`
  - `python3 {baseDir}/scripts/update_routing.py ...`
  - `python3 {baseDir}/scripts/resume_run.py ...`

Resume an existing run after routing confirmation:

```bash
conda run -n truth-seek python -m tools.question_generator.cli run-recipe-on-run \
  --recipe prompt/question-generator/recipes/non-render.recipe.json \
  --run-dir tmp/question-runs/atlas-healthcare \
  --start-stage boundary
```

Run the question-generator test suite:

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
  tests.question_generator.test_state_resolution -v
```

## Recommended Reading

- [AGENTS.md](AGENTS.md)
- [prompt/question-generator/README.md](prompt/question-generator/README.md)
- [prompt/question-generator/IMPLEMENTATION.md](prompt/question-generator/IMPLEMENTATION.md)
- [docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md](docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md)
