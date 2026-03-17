---
name: deep-think
description: Use when a user wants to analyze a topic, generate a research or decision artifact, or structure an uncertain question into a memo, scenario tree, monitoring plan, or research prompt.
---

# Deep Think Skill

Use this skill to run Deep Think from a raw user topic.

This workflow involves back-and-forth interaction with AI models across
multiple stages, so it can take time to complete. The runtime now uses a
500-second timeout to reduce premature termination, and the user should not
interrupt the process just because a stage takes a while to return.

## Trigger Examples

Use this skill for requests like:
- "Analyze whether this company should expand into healthcare next year."
- "Turn this topic into a decision memo."
- "Build a research plan for this question."
- "Create a scenario tree for this issue."
- "What should I monitor for this topic?"
- "Help me think through this uncertain decision."

## Workflow

1. Treat the user's natural-language topic of interest as the raw `topic`.
2. If the user clearly asks for the final deliverable in a specific language, capture that as `output_language` for the run.
3. Set `output_language` only when the run starts. Do not change it later in the run.
4. The language preference affects only the final render stage, not upstream analysis.
5. Run the topic bootstrap flow through the Conda environment so the initial
   workflow state is the minimal payload `{"topic": "..."}` rather than a
   copy of `shared_state_schema.json`.
6. Execute `Routing` first and stop.
7. Present the inferred routing summary to the user for confirmation.
8. If the user gives clear corrections, update only those `routing` fields directly.
9. Never rerun `Routing`.
10. Resume the workflow from `Boundary`.
11. Return the final rendered artifact.

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

- Always run Python via `conda run -n deep-think`
- Use the repo CLI/orchestrator helpers instead of hand-editing run artifacts
- Keep `shared_state.json` as the only workflow state
- If the user requested a final output language, pass `--output-language "<language>"` when creating the run

Read [references/commands.md](references/commands.md) for the exact commands.
