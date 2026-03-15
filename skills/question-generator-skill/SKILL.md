---
name: question-generator-skill
description: Use when a user provides a natural-language topic and wants the truth-seek question-generator workflow to produce a final artifact with a routing confirmation step.
---

# Question Generator Skill

Use this skill to run the truth-seek question-generator from a raw user topic.

## Workflow

1. Treat the user's natural-language topic of interest as the raw `topic`.
2. Run the topic bootstrap flow through the Conda environment.
3. Execute `Routing` first and stop.
4. Present the inferred routing summary to the user for confirmation.
5. If the user gives clear corrections, update only those `routing` fields directly.
6. Never rerun `Routing`.
7. Resume the workflow from `Boundary`.
8. Return the final rendered artifact.

## Routing Review Rules

Show the user these inferred routing fields:
- normalized question
- task
- domain
- output mode
- evidence mode
- uncertainty mode
- decision mode
- time horizon
- unit of analysis
- decision context
- assumptions

If the user confirms, continue immediately.

If the user corrects fields:
- interpret the correction directly
- update only the clearly affected `routing` fields
- preserve all unaffected fields
- update `classification_rationales` when the user clearly changed the reason
- update `assumptions` only when the user explicitly replaced or removed them

If the user's correction is ambiguous:
- ask one focused follow-up question
- do not guess
- do not rerun `Routing`

## Command Rules

- Always run Python via `conda run -n truth-seek`
- Use the repo CLI/orchestrator helpers instead of hand-editing run artifacts
- Keep `shared_state.json` as the only workflow state

Read [references/commands.md](references/commands.md) for the exact commands.
