# Question Generator Skill Commands

Run these from the repository root:
- `/Users/canzheng/Work/sandbox/truth-seek`

## Topic Bootstrap

Initialize a run from a raw topic:

```bash
conda run -n truth-seek python -m tools.question_generator.cli init-topic-run \
  --topic "Should Atlas expand into healthcare next quarter?" \
  --output-dir tmp/question-runs \
  --run-id atlas-healthcare
```

## Run Routing Only

```bash
conda run -n truth-seek python -m tools.question_generator.cli run-stage \
  --run-dir tmp/question-runs/atlas-healthcare \
  --stage routing
```

## Apply Routing Corrections

Construct a partial routing patch from the user's feedback and apply it:

```bash
conda run -n truth-seek python -m tools.question_generator.cli update-routing \
  --run-dir tmp/question-runs/atlas-healthcare \
  --patch-json '{"output_mode":"Research Memo","time_horizon":"next 12 months"}'
```

## Resume Remaining Workflow

```bash
conda run -n truth-seek python -m tools.question_generator.cli run-recipe-on-run \
  --recipe prompt/question-generator/recipes/non-render.recipe.json \
  --run-dir tmp/question-runs/atlas-healthcare \
  --start-stage boundary
```

## One-Command Convenience Flow

Run from topic and pause after routing:

```bash
conda run -n truth-seek python -m tools.question_generator.cli run-topic \
  --topic "Should Atlas expand into healthcare next quarter?" \
  --recipe prompt/question-generator/recipes/non-render.recipe.json \
  --output-dir tmp/question-runs \
  --run-id atlas-healthcare \
  --pause-after-stage routing
```

If no pause is needed, omit `--pause-after-stage`.
