---
name: deep-think
description: Use when a user wants to analyze a topic, generate a research or decision artifact, or structure an uncertain question into a memo, scenario tree, monitoring plan, or research prompt.
metadata: {"openclaw":{"requires":{"bins":["python3"]}}}
---

# Deep Think For OpenClaw

Use this packaging artifact when Deep Think should run inside an OpenClaw
environment as a self-contained bundle instead of relying on the repo-local
Codex runtime.

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
2. Run the bundled Python entrypoints with plain `python3`.
3. Execute `Routing` first and stop.
4. Present the inferred routing summary to the user for confirmation.
5. If the user gives clear corrections, update only those `routing` fields directly.
6. Never rerun `Routing`.
7. Resume the workflow from `Boundary`.
8. Return the final rendered artifact.

## Command Rules

- Run the bundle through:
  - `python3 {baseDir}/scripts/run_topic.py ...`
  - `python3 {baseDir}/scripts/update_routing.py ...`
  - `python3 {baseDir}/scripts/resume_run.py ...`
- Do not rely on `conda` or a separate repo checkout
- Keep `shared_state.json` as the only workflow state
- Keep run artifacts under `{baseDir}/tmp/question-runs`

## Runtime Notes

This workflow involves back-and-forth interaction with AI models across
multiple stages, so it can take time to complete. The runtime uses a
500-second timeout to reduce premature termination, and the user should not
interrupt the process just because a stage takes a while to return.
