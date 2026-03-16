# OpenClaw Executor Abstraction Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:executing-plans or superpowers:subagent-driven-development when implementing this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the question-generator stage runner behind a backend abstraction so the current Codex execution path remains intact while adding an OpenClaw-native execution path that prefers `llm-task` for JSON stages, falls back to chat-completions with JSON hardening and repair, and preserves the existing prompt assembly and local validation flow.

**Architecture:** Move stage execution out of `orchestrator.py`’s Codex-specific subprocess path into executor classes. Keep prompt assembly, contracts, and shared-state merge semantics unchanged. Add capability-aware OpenClaw executors that select `llm-task` for non-render stages when available, otherwise use Gateway `/v1/chat/completions` plus a repair pass, while `render` always uses plain text chat-completions.

**Tech Stack:** Python 3 via `conda run -n truth-seek`, existing question-generator runtime, standard library HTTP/JSON/subprocess support, `unittest`, markdown skill packaging.

---

## File Structure

**Files to create**
- `tools/question_generator/executors.py`
  - backend-neutral executor interface and shared result/config models
- `tools/question_generator/openclaw_executor.py`
  - OpenClaw capability detection, `llm-task` integration, Gateway HTTP fallback, JSON hardening, repair flow
- `tests/question_generator/test_executors.py`
  - focused tests for executor selection, fallback, and repair behavior
- `skills/question-generator-skill/openclaw/SKILL.md`
  - OpenClaw packaging artifact layered on top of the existing Codex skill

**Files to modify**
- `tools/question_generator/orchestrator.py`
  - remove direct dependence on `codex exec` in `run_stage`
  - adopt backend-neutral executor invocation
  - neutralize backend-specific artifact naming and manifest fields
- `tools/question_generator/cli.py`
  - optional executor/backend selection surface for local testing
- `tests/question_generator/test_orchestrator.py`
  - update Codex-path tests to use the new executor abstraction
  - add OpenClaw-path orchestration tests
- `README.md`
  - document executor selection and any required OpenClaw env/config
- `prompt/question-generator/README.md`
  - document how OpenClaw execution differs only at the runner layer

**Possible files to modify if needed**
- `skills/question-generator-skill/SKILL.md`
  - only if small wording changes are needed to reference the OpenClaw packaging artifact

## Chunk 1: Lock The Executor Abstraction In Tests

### Task 1: Add failing tests for backend-neutral stage execution

**Files:**
- Create: `tests/question_generator/test_executors.py`
- Modify: `tests/question_generator/test_orchestrator.py`

- [ ] **Step 1: Add a failing test for a backend-neutral `StageExecutionResult`**

Cover:
- `response_text`
- `backend_name`
- trace/error fields

- [ ] **Step 2: Add a failing test that `run_stage` delegates to an injected executor**

Verify that:
- the prepared prompt text is passed to the executor
- the orchestrator no longer depends directly on `subprocess.run`
- the returned response text still flows through `apply_stage_response`

- [ ] **Step 3: Add a failing test that backend-neutral artifact names are written**

Replace assumptions about:
- `codex.stdout.jsonl`
- `codex.stderr.txt`

with neutral fields such as:
- `executor_trace_path`
- `executor_error_path`
- `executor_backend`

- [ ] **Step 4: Add a failing test for OpenClaw JSON-stage capability routing**

Cover:
- non-render stage uses `llm-task` when capability is present
- same stage falls back to chat-completions when capability is absent

- [ ] **Step 5: Add a failing test for one repair pass on invalid JSON fallback**

Verify:
- first chat-completions response is invalid
- executor sends a second repair request
- repaired JSON is returned to the orchestrator

- [ ] **Step 6: Run focused tests and confirm failure**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_executors \
  tests.question_generator.test_orchestrator -v
```

Expected:
- FAIL because the executor abstraction does not exist yet

## Chunk 2: Introduce Executor Models And Preserve Codex Behavior

### Task 2: Add the executor interface and Codex implementation first

**Files:**
- Create: `tools/question_generator/executors.py`
- Modify: `tools/question_generator/orchestrator.py`
- Modify: `tests/question_generator/test_orchestrator.py`

- [ ] **Step 1: Define the executor models**

Add:
- `StageExecutionResult`
- `StageExecutor` protocol or abstract base class
- optional backend config dataclasses if needed

- [ ] **Step 2: Move the current Codex subprocess logic into `CodexStageExecutor`**

Preserve:
- `codex exec --ephemeral`
- current model and reasoning settings
- current stage prompt wrapper semantics

- [ ] **Step 3: Refactor `run_stage` to accept or resolve an executor**

The orchestrator should:
- prepare the prompt as it does today
- call the executor
- persist backend-neutral trace artifacts
- pass the resulting response text into `apply_stage_response`

- [ ] **Step 4: Keep the Codex path behaviorally equivalent**

Do not change:
- prompt assembly
- JSON parsing
- state merge semantics
- topic bootstrap flow

- [ ] **Step 5: Run focused tests**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_orchestrator -v
```

Expected:
- PASS for all Codex-path tests using the new abstraction

## Chunk 3: Add OpenClaw HTTP And Capability-Aware JSON Execution

### Task 3: Implement the OpenClaw executor family

**Files:**
- Create: `tools/question_generator/openclaw_executor.py`
- Create: `tests/question_generator/test_executors.py`

- [ ] **Step 1: Add OpenClaw runtime config loading**

Support environment-driven config for:
- Gateway base URL
- bearer token
- target agent id
- optional flag or capability marker for `llm-task`

- [ ] **Step 2: Implement chat-completions transport**

Use standard-library HTTP support.

Cover:
- request body assembly
- bearer auth
- stateless request model
- text response extraction

- [ ] **Step 3: Implement `llm-task` capability path for JSON stages**

Design this as optional:
- if capability is unavailable, do not fail the stage here
- instead route into the fallback path

- [ ] **Step 4: Implement JSON hardening wrapper for chat-completions fallback**

The wrapper should add:
- return exactly one JSON object
- no markdown fences
- concise schema reminder
- explicit rejection of non-JSON output

- [ ] **Step 5: Implement one repair pass**

If the first fallback response fails local parse or schema validation:
- send a repair request containing
  - original stage purpose
  - invalid output
  - failure reason
  - required output schema
- require corrected JSON only

- [ ] **Step 6: Ensure `render` always uses plain text execution**

Do not apply:
- JSON hardening
- repair pass
- `llm-task`

- [ ] **Step 7: Run focused executor tests**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_executors -v
```

Expected:
- PASS for capability routing and repair behavior

## Chunk 4: Wire OpenClaw Execution Into The Orchestrator And CLI

### Task 4: Add backend selection without disrupting current flows

**Files:**
- Modify: `tools/question_generator/orchestrator.py`
- Modify: `tools/question_generator/cli.py`
- Modify: `tests/question_generator/test_cli.py`
- Modify: `tests/question_generator/test_orchestrator.py`

- [ ] **Step 1: Add executor/backend selection to orchestration entrypoints**

Cover:
- `run_stage`
- `run_recipe`
- `run_recipe_on_run`
- `run_topic`

- [ ] **Step 2: Make Codex the default backend initially**

This keeps current local behavior stable while OpenClaw support lands.

- [ ] **Step 3: Add a CLI surface for backend selection**

Suggested:
- `--executor-backend codex|openclaw`

- [ ] **Step 4: Add tests for backend selection plumbing**

Verify:
- CLI passes backend choice into the orchestrator
- orchestrator resolves the right executor implementation

- [ ] **Step 5: Run focused CLI and orchestrator tests**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_cli \
  tests.question_generator.test_orchestrator -v
```

Expected:
- PASS with both Codex-default and OpenClaw-plumbing tests

## Chunk 5: Add OpenClaw Packaging Artifact

### Task 5: Package the existing skill for OpenClaw without forking the workflow

**Files:**
- Create: `skills/question-generator-skill/openclaw/SKILL.md`
- Modify: `README.md`
- Modify: `prompt/question-generator/README.md`

- [ ] **Step 1: Write the OpenClaw-specific `SKILL.md`**

Preserve:
- topic-first workflow
- routing confirmation pause
- direct routing patch semantics

Add:
- minimal `metadata.openclaw`
- note that JSON stages prefer `llm-task` when available
- note that fallback uses Gateway chat-completions with repair

- [ ] **Step 2: Document OpenClaw runtime expectations**

Include:
- required env/config
- private Gateway requirement
- artifact location stays under repo `tmp/question-runs`

- [ ] **Step 3: Update repo docs**

Clarify:
- prompt assembly is unchanged
- only the executor layer differs
- OpenClaw packaging is an additional artifact, not a replacement for the Codex skill

## Chunk 6: Final Verification

### Task 6: Run the full focused verification surface

**Files:**
- Verify: `tools/question_generator/executors.py`
- Verify: `tools/question_generator/openclaw_executor.py`
- Verify: `tools/question_generator/orchestrator.py`
- Verify: `tools/question_generator/cli.py`
- Verify: `skills/question-generator-skill/openclaw/SKILL.md`

- [ ] **Step 1: Run the focused test suite**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_cli \
  tests.question_generator.test_executors \
  tests.question_generator.test_orchestrator -v
```

Expected:
- PASS with 0 failures

- [ ] **Step 2: Sanity-check CLI help if new flags were added**

Run:

```bash
conda run -n truth-seek python -m tools.question_generator.cli run-stage --help
conda run -n truth-seek python -m tools.question_generator.cli run-topic --help
```

Expected:
- backend-selection flags render cleanly

- [ ] **Step 3: Summarize residual risks**

Check for:
- OpenClaw capability detection may still need environment-specific tuning
- `llm-task` integration depends on real agent/tool availability
- chat-completions fallback still depends on prompt discipline plus repair

Plan complete and saved to `docs/superpowers/plans/2026-03-16-openclaw-executor-abstraction.md`. Ready to execute?
