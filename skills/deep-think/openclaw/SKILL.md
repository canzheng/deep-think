---
name: deep-think
description: Use this deep think skill when a user wants to analyze a topic, generate a research or decision artifact, or structure an uncertain question into a memo, scenario tree, monitoring plan, or research prompt.
metadata: {"openclaw":{"requires":{"bins":["python3"]}}}
---

# Deep Think For OpenClaw

Use this packaging artifact when Deep Think should run inside an OpenClaw
environment as a self-contained bundle.

This artifact preserves the same workflow:
- topic-first input
- routing confirmation pause
- direct routing patching
- resume from `Boundary`

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
- Prompt assembly, contracts, and shared-state behavior stay unchanged.
- JSON-returning stages have a soft dependency on OpenClaw `llm-task`.
- The packaged runtime keeps a persistent executor capability config in
  `config/runtime.json`.
- If that config is `auto`, the first run tries `llm-task` once and persists
  either `llm-task` or `chat_fallback`.
- If `llm-task` is unavailable, JSON-returning stages fall back to OpenClaw
  Gateway chat-completions with JSON hardening, one repair pass, and local
  validation.
- `render` uses plain text chat-completions.

## Workflow

1. Treat the user's natural-language topic of interest as the raw `topic`.
2. If the user clearly asks for the final deliverable in a specific language, capture that as `output_language` for the run.
3. Set `output_language` only when the run starts. Do not change it later in the run.
4. The language preference affects only the final render stage, not upstream analysis.
5. Derive `run-id` by slugifying the topic into a short lowercase hyphenated label and appending a timestamp suffix for uniqueness, for example `atlas-expand-healthcare-20260317-101530`.
6. Start the workflow with `python3 {baseDir}/scripts/run_topic.py` and always pass both `--run-id <run-id>` and `--pause-after-stage routing`.
7. Let that command run through `Routing` and stop.
8. Present the inferred routing summary to the user for confirmation.
9. If the user gives clear corrections, apply them with `python3 {baseDir}/scripts/update_routing.py`.
10. Never rerun `Routing`.
11. Resume the workflow from `Boundary` with `python3 {baseDir}/scripts/resume_run.py`.
12. Return the final rendered artifact.

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

- Derive `run-id` from the topic with:
  - a short slug from the first meaningful words
  - lowercase letters, numbers, and hyphens only
  - a timestamp suffix for uniqueness
  - example: `atlas-expand-healthcare-20260317-101530`
- Start with:
  - `python3 {baseDir}/scripts/run_topic.py --topic "<topic>" --run-id <run-id> --pause-after-stage routing`
- If the user requested a final output language, add:
  - `--output-language "<language>"`
- If the user confirms routing as-is:
  - `python3 {baseDir}/scripts/resume_run.py --run-dir {baseDir}/tmp/question-runs/<run-id>`
- If the user corrects routing fields:
  - `python3 {baseDir}/scripts/update_routing.py --run-dir {baseDir}/tmp/question-runs/<run-id> --patch-json '<json patch>'`
  - then `python3 {baseDir}/scripts/resume_run.py --run-dir {baseDir}/tmp/question-runs/<run-id>`
- Do not rely on `conda` or a separate repo checkout
- Keep `shared_state.json` as the only workflow state
- Keep run artifacts under `{baseDir}/tmp/question-runs`

## Runtime Notes

This workflow involves back-and-forth interaction with AI models across
multiple stages, so it can take time to complete. The runtime uses a
500-second timeout to reduce premature termination, and the user should not
interrupt the process just because a stage takes a while to return.
