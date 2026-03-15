# Truth Seek

This repository contains prompt, contract, and runtime tooling for the `question-generator` workflow.

The main working area today is:
- [prompt/question-generator/README.md](/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/README.md)

## What This Repo Contains

- [prompt/question-generator/question-generator-modular.md](/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/question-generator-modular.md): modular source of truth for the question generator
- [prompt/question-generator/stages](/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages): stage prompt templates
- [prompt/question-generator/adapters](/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/adapters): structured adapter content and stage guidance
- [prompt/question-generator/output-modes](/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/output-modes): output-mode guidance
- [prompt/question-generator/contracts](/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts): stage contracts and shared-state schemas
- [tools/question_generator](/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator): Python assembler and orchestration runtime
- [tests/question_generator](/Users/canzheng/Work/sandbox/truth-seek/tests/question_generator): unit tests, review prompts, and prompt artifacts
- [tmp/question-runs](/Users/canzheng/Work/sandbox/truth-seek/tmp/question-runs): local run artifacts from end-to-end workflows

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

The durable workflow state lives in one file shaped by:
- [shared_state_schema.json](/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/shared_state_schema.json)

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
  tests.question_generator.test_state_rendering \
  tests.question_generator.test_state_resolution -v
```

## Recommended Reading

- [AGENTS.md](/Users/canzheng/Work/sandbox/truth-seek/AGENTS.md)
- [prompt/question-generator/README.md](/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/README.md)
- [prompt/question-generator/IMPLEMENTATION.md](/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/IMPLEMENTATION.md)
- [docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md](/Users/canzheng/Work/sandbox/truth-seek/docs/superpowers/specs/2026-03-13-question-generator-architecture-design.md)
