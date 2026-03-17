---
name: deep-think
description: Use this deep think skill when a user wants to analyze a topic, generate a research or decision artifact, or structure an uncertain question into a memo, scenario tree, monitoring plan, or research prompt.
metadata: {"openclaw":{"requires":{"bins":["python3","openclaw"]}}}
---

# Deep Think For OpenClaw

Use this packaging artifact when Deep Think should run inside an OpenClaw
environment as a self-contained bundle.

`{baseDir}` means the root of the installed OpenClaw skill bundle, the
directory that contains this `SKILL.md`.

This artifact preserves the same workflow:
- topic-first input
- routing confirmation pause
- direct routing patching
- continue from `Boundary`

## Trigger Examples

Use this skill for requests like:
- "Analyze whether we should expand into healthcare next year."
- "Turn this topic into a decision memo."
- "Build a research plan for this question."
- "Create a scenario tree for this issue."
- "What should I monitor for this topic?"
- "Help me think through this uncertain decision."

## Execution Model

- The bundle carries its own Python runtime modules, prompt assets, contracts,
  recipes, and vendored `chevron`.
- Prefer the current OpenClaw agent as the default execution path.
- Treat this skill as instructions plus workflow tools for the active agent,
  not as a place to invoke a second model client by default.
- Use `prepare-stage` as the canonical prompt assembly step.
- Use `apply-response` as the validation and state-write step for structured
  stages.
- For `render`, produce raw text or markdown, not JSON.
- OpenClaw `llm-task` is optional and should be treated as an opt-in fallback
  or enhancement for strict structured extraction when it is available and
  materially helpful.
- The packaged runtime keeps a persistent executor capability config in
  `config/runtime.json`.
- The default executor mode is `session`, but the skill should not depend on
  it for normal operation.
- If a workflow command is run with `--executor-backend openclaw` and
  `llm-task` is explicitly enabled, that is a fallback path rather than the
  baseline design.

## Workflow

1. Treat the user's natural-language topic of interest as the raw `topic`.
2. If the user clearly asks for the final deliverable in a specific language, capture that as `output_language` for the run.
3. Set `output_language` only when the run starts. Do not change it later in the run.
4. The language preference affects only the final render stage, not upstream analysis.
5. Derive `run-id` by slugifying the topic into a short lowercase hyphenated label and appending a timestamp suffix for uniqueness, for example `atlas-expand-healthcare-20260317-101530`.
6. Initialize the run artifacts, complete `Routing`, and pause for user review.
7. Summarize the routing result from the run artifacts and ask for confirmation or corrections.
8. If the user corrects routing, patch it directly and continue from `Boundary`.
9. Complete the remaining stages one by one.
10. Return the final rendered artifact.

## Agent-First Stage Loop

Use this loop unless the user explicitly wants the optional OpenClaw executor path:

1. Initialize the run artifacts from the raw topic.
2. Read `shared_state.json` when needed for context.
3. Run `prepare-stage` to generate the canonical prompt for the next stage.
4. Read the generated prompt and answer it as the current agent.
5. For structured stages, return contract-conforming JSON.
6. For `render`, return raw final text or markdown.
7. Run `apply-response` to persist the result.
8. Move to the next stage only after `apply-response` succeeds.
9. Pause after `Routing` for user review, then continue from `Boundary`.

Canonical command pattern:

- Initialize only the run artifacts:
  - `python3 {baseDir}/scripts/init_topic_run.py --topic "<topic>" --output-dir {baseDir}/tmp/question-runs --run-id <run-id>`
- Inspect the current shared state when needed:
  - read `{baseDir}/tmp/question-runs/<run-id>/shared_state.json`
- Prepare one stage prompt from the current run state:
  - `python3 {baseDir}/scripts/prepare_stage.py --run-dir {baseDir}/tmp/question-runs/<run-id> --stage routing`
- Read the prepared prompt from the path returned by `prepare-stage`, for
  example:
  - `{baseDir}/tmp/question-runs/<run-id>/stages/routing/prompt.md`
- Inspect the structured-output schema when the stage is not `render`:
  - read `{baseDir}/tmp/question-runs/<run-id>/stages/routing/response.schema.json`
- Save the current agent's stage response to a file, then apply it back into
  the run state:
  - `python3 {baseDir}/scripts/apply_response.py --run-dir {baseDir}/tmp/question-runs/<run-id> --stage routing --response <response-file>`
- Continue later stages with the same `prepare-stage` then `apply-response`
  pattern:
  - `boundary`
  - `structure`
  - `scenarios`
  - `question_generation`
  - `evidence_planning`
  - `decision_logic`
  - `signal_translation`
  - `monitoring`
  - `render`

## Progress Updates

- Send a short standalone progress update before each stage after `Routing`.
- Put each progress update in its own message or paragraph. Do not concatenate multiple stage updates together.
- Use plain, compact wording such as `Proceeding to Boundary stage.` or `Proceeding to Structure stage.`
- Do not narrate acceleration or compression. Do not say you are "skipping", "accelerating", "moving quickly", or "doing the rest more efficiently".

## Critical Rules

- Never assume a hidden executor is running the stage loop for you.
- Never rerun `Routing`.
- Execute every stage in order:
  - `boundary`
  - `structure`
  - `scenarios`
  - `question_generation`
  - `evidence_planning`
  - `decision_logic`
  - `signal_translation`
  - `monitoring`
  - `render`
- Do not skip stages, merge stages, jump ahead to `render`, or compress the remaining workflow into a summary step.
- Start the next stage only after the current stage response has been applied successfully.
- After `Routing`, inspect `stages/routing/response.parsed.json` and the updated `shared_state.json`.
- Show the user these routing fields:
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
- If the user confirms routing, continue immediately from `Boundary`.
- If the user corrects routing fields, patch only the affected `routing` fields with:
  - `python3 {baseDir}/scripts/update_routing.py --run-dir {baseDir}/tmp/question-runs/<run-id> --patch-json '<json patch>'`
- Preserve all unaffected routing fields.
- Update `classification_rationales` only when the user clearly changed the reason.
- Update `assumptions` only when the user explicitly replaced or removed them.
- If the user's correction is ambiguous, ask one focused follow-up question.
- Use `llm-task` only when it is enabled and allowlisted, and only when strict structured output materially helps.
- Do not rely on `conda` or a separate repo checkout
- Keep `shared_state.json` as the only workflow state
- Keep run artifacts under `{baseDir}/tmp/question-runs`

## Runtime Notes

This workflow involves back-and-forth interaction with AI models across
multiple stages, so it can take time to complete. The runtime uses a
500-second timeout to reduce premature termination, and the user should not
interrupt the process just because a stage takes a while to return.
