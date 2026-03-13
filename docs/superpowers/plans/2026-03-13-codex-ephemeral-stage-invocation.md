# Codex Ephemeral Stage Invocation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the orchestrator call a fresh ephemeral Codex answering session for each stage, always using `gpt-5.4` with `high` reasoning, while preserving stage artifacts and contract-scoped state merge behavior.

**Architecture:** Extend the orchestrator to generate a per-stage response schema, build and run a `codex exec --ephemeral` subprocess, persist stdout/stderr and the final raw reply, then parse and merge only the contract-owned state sections. Keep the manual prepare/apply path available for debugging, but add an automatic `run-stage` path that performs the full prepare -> invoke -> apply flow in one command.

**Tech Stack:** Python standard library, existing question-generator runtime, local Codex CLI, `unittest`

---

## Chunk 1: Codex Invocation Contract

### Task 1: Define the invocation policy and artifact set

**Files:**
- Modify: `tools/question_generator/orchestrator.py`
- Modify: `tests/question_generator/test_orchestrator.py`

- [ ] **Step 1: Write the failing tests**

Add tests that assert:
- the built Codex command always includes `exec`, `--ephemeral`, `-m gpt-5.4`, and `reasoning_effort="high"`
- the stage artifact directory gets a persisted `response.schema.json`
- the response schema includes the stage output schema plus optional `feedback` when the contract supports it

- [ ] **Step 2: Run the focused orchestrator test file to verify it fails**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_orchestrator -v`
Expected: FAIL because the Codex invocation helpers and schema artifact behavior do not exist yet.

- [ ] **Step 3: Write the minimal implementation**

Implement:
- fixed answering-session execution constants
- response-schema generation helpers
- command-construction helpers for `codex exec`
- stage artifact paths for schema/stdout/stderr

- [ ] **Step 4: Re-run the focused orchestrator tests**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_orchestrator -v`
Expected: PASS for the new command-construction and schema-artifact tests.

## Chunk 2: Automatic Ephemeral Stage Execution

### Task 2: Invoke Codex automatically and persist execution artifacts

**Files:**
- Modify: `tools/question_generator/orchestrator.py`
- Modify: `tests/question_generator/test_orchestrator.py`

- [ ] **Step 1: Write the failing tests**

Add tests that assert:
- `run_stage` prepares the prompt, invokes the subprocess, and applies the response
- subprocess stdout and stderr are persisted into stage artifacts
- the manifest records model, reasoning effort, ephemeral execution, and command metadata
- subprocess failures raise clean errors and do not silently merge state

- [ ] **Step 2: Run the focused orchestrator test file to verify it fails**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_orchestrator -v`
Expected: FAIL because automatic invocation and execution-artifact persistence are not implemented yet.

- [ ] **Step 3: Write the minimal implementation**

Implement:
- subprocess invocation with stdin-fed prompt text
- persisted stdout/stderr artifacts
- timeout-aware error handling
- automatic handoff from invocation to response parsing and merge

- [ ] **Step 4: Re-run the focused orchestrator tests**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_orchestrator -v`
Expected: PASS for the automatic stage-execution tests.

## Chunk 3: CLI Flow, Docs, And Regression Coverage

### Task 3: Expose one-shot automatic stage execution and document it

**Files:**
- Modify: `tools/question_generator/cli.py`
- Modify: `tests/question_generator/test_cli.py`
- Modify: `prompt/question-generator/README.md`
- Modify: `prompt/question-generator/IMPLEMENTATION.md`
- Modify: `guidelines/question-generator-workflow.md`
- Test: `tests/question_generator/test_cli.py`
- Test: `tests/question_generator/test_orchestrator.py`

- [ ] **Step 1: Write the failing CLI tests**

Add tests that assert:
- the CLI can run one stage end-to-end with `run-stage`
- the CLI still supports manual `prepare-stage` and `apply-response`
- the automatic path reports the parsed response artifact or updated state path

- [ ] **Step 2: Run the focused CLI and orchestrator tests to verify they fail**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_cli tests.question_generator.test_orchestrator -v`
Expected: FAIL because the `run-stage` command does not exist yet.

- [ ] **Step 3: Write the minimal implementation**

Implement:
- `run-stage` CLI command
- any command-line flags needed for Codex binary path and timeout
- documentation updates for the automatic ephemeral invocation flow

- [ ] **Step 4: Run the targeted regression suite**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_cli tests.question_generator.test_orchestrator tests.question_generator.test_assembler tests.question_generator.test_contract_loading -v`
Expected: PASS

- [ ] **Step 5: Run the full question-generator test suite**

Run: `conda run -n truth-seek python -m unittest discover -s tests/question_generator -p 'test_*.py' -v`
Expected: PASS
