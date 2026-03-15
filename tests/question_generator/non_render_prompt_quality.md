# Non-Render Prompt Quality Review

This workflow checks the assembled non-render prompts with a structured Codex review pass.

It is a second quality layer on top of local unit tests:
- local tests verify assembly correctness
- the Codex review verifies prompt quality properties that are hard to assert mechanically

## Scope

This workflow covers only these non-render stages:
- `routing`
- `boundary`
- `structure`
- `scenarios`
- `question_generation`
- `evidence_planning`
- `decision_logic`
- `signal_translation`
- `monitoring`

It does not cover `render`.

## Review Criteria

The Codex review must score each stage against:
- hard gates:
  - `Instruction Coherence`
  - `Input Precedence Clarity`
  - `Output Requirement Clarity`
  - `Sufficient Starting Context`
- scored dimensions:
  - `Task Clarity`
  - `Context Usefulness`
  - `Guidance And Constraint Clarity`
  - `Readability`
  - `Output Readiness`
  - `Confidence To Execute`
  - `Context Efficiency`
  - `Risk Of Misinterpretation`

Pass rule:
- every hard gate must be `PASS` for every reviewed stage

Reporting rule:
- all scored dimensions must be reported even when the review fails

## Inputs

This workflow uses:
- the populated shared-state fixture at [populated_state.json](tests/question_generator/fixtures/populated_state.json)
- a seeded stress-case topic chosen by [assemble_non_render_prompts.py](tests/question_generator/assemble_non_render_prompts.py)
- the reviewer rubric at [non_render_prompt_review_prompt.md](tests/question_generator/non_render_prompt_review_prompt.md)
- the structured output contract at [non_render_prompt_review_schema.json](tests/question_generator/non_render_prompt_review_schema.json)

The assembled prompts should already use the repo’s prompt-facing labels such as `Relevant Context` and `Stage Guidance` when those runtime changes are active.

## Step 1: Generate The Review Prompt Set

Run:

```bash
conda run -n truth-seek python tests/question_generator/assemble_non_render_prompts.py --output-dir tests/question_generator/artifacts/non_render_prompt_review_prompts --manifest tests/question_generator/artifacts/non_render_prompt_review_manifest.json --seed 20260313
```

This creates:
- the selected review topic
- one fully assembled prompt file for each non-render stage
- a manifest JSON file listing the prompt paths

## Step 2: Ask Codex To Review Each Prompt Separately

Give Codex:
- the rubric in [non_render_prompt_review_prompt.md](tests/question_generator/non_render_prompt_review_prompt.md)
- the manifest in `tests/question_generator/artifacts/non_render_prompt_review_manifest.json`
- one prompt file at a time from `tests/question_generator/artifacts/non_render_prompt_review_prompts/`

Ask Codex to:
- review one prompt at a time
- return JSON only
- produce one review object for that prompt
- save the result as a JSON array

Suggested output path:
- `tests/question_generator/artifacts/non_render_prompt_review.json`

Recommended process:
- review each prompt file listed in the manifest separately
- collect one review object per prompt
- combine those review objects into the final JSON array

This avoids false negatives caused by reviewing one very large multi-prompt bundle in a single pass.

## Step 3: Validate The Structured Review

Run:

```bash
conda run -n truth-seek python tests/question_generator/check_non_render_prompt_review.py --input tests/question_generator/artifacts/non_render_prompt_review.json
```

The checker will:
- validate each stage review result
- print the hard-gate outcomes
- print all dimension scores
- print the overall recommendation per stage
- return a failing exit code if any hard gate fails or if the JSON is malformed

Expected terminal summary:
- `QUALITY REVIEW PASS`
- or `QUALITY REVIEW FAIL`

## Example Review Output Shape

The review JSON should be an array like:

```json
[
  {
    "stage": "routing",
    "hard_gates": {
      "instruction_coherence": "PASS",
      "input_precedence_clarity": "PASS",
      "output_requirement_clarity": "PASS",
      "sufficient_starting_context": "PASS"
    },
    "scores": {
      "task_clarity": 4,
      "context_usefulness": 4,
      "guidance_and_constraint_clarity": 4,
      "readability": 4,
      "output_readiness": 4,
      "confidence_to_execute": 4,
      "context_efficiency": 3,
      "risk_of_misinterpretation": 4
    },
    "top_findings": [],
    "overall_recommendation": "Accept",
    "summary": "Clear and usable non-render prompt."
  }
]
```

## Local Verification

Before using the workflow, run the focused test file:

```bash
conda run -n truth-seek python -m unittest tests.question_generator.test_non_render_prompt_quality -v
```

This verifies:
- schema shape
- stage list
- deterministic topic selection
- prompt-set generation
- checker behavior

## Notes

- The bundle generator changes the topic only in memory; it does not modify the fixture file.
- Hard gates determine pass or fail.
- Scores are diagnostic for now and do not fail the workflow by themselves.
