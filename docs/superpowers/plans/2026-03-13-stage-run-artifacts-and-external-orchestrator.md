# Stage Run Artifacts And External Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a first orchestrator workflow that supports a separate stage-answering Codex session while persisting every stage prompt and reply as debug artifacts without polluting shared state.

**Architecture:** Introduce a small orchestrator module that manages run directories, writes assembled stage prompts, records raw and parsed stage responses, validates basic contract ownership, and merges only stage-owned sections into `shared_state.json`. Keep the model boundary external-first so the orchestrator can hand prompts to a separate Codex session without coupling this repo to a specific Codex invocation path.

**Tech Stack:** Python standard library, existing question-generator runtime, `unittest`

---

## Chunk 1: Run Artifact Model And Paths

### Task 1: Define run-artifact responsibilities

**Files:**
- Create: `tools/question_generator/orchestrator.py`
- Modify: `tools/question_generator/pathing.py`
- Modify: `tools/question_generator/models.py`
- Test: `tests/question_generator/test_orchestrator.py`

- [ ] **Step 1: Write the failing tests**

Add tests that assert:
- a run directory can be initialized from a state file
- the run directory gets a stable manifest path and stage artifact paths
- preparing a stage writes `prompt.md` before any response exists

- [ ] **Step 2: Run the focused test file to verify it fails**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_orchestrator -v`
Expected: FAIL because the orchestrator module and helpers do not exist yet.

- [ ] **Step 3: Write the minimal implementation**

Implement:
- canonical stage order helpers as needed
- run initialization helpers
- stage artifact path helpers
- manifest persistence helpers

- [ ] **Step 4: Re-run the focused test file**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_orchestrator -v`
Expected: PASS for the new artifact-path and run-initialization tests.

## Chunk 2: Response Recording And Contract-Scoped Merge

### Task 2: Record raw and parsed responses, then merge owned state sections only

**Files:**
- Modify: `tools/question_generator/orchestrator.py`
- Modify: `tools/question_generator/contracts.py`
- Test: `tests/question_generator/test_orchestrator.py`

- [ ] **Step 1: Write the failing tests**

Add tests that assert:
- a raw response with fenced JSON can be parsed into a structured payload
- the raw reply is persisted separately from the parsed JSON
- only contract-owned sections are merged into shared state
- unexpected top-level sections are rejected

- [ ] **Step 2: Run the focused test file to verify it fails**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_orchestrator -v`
Expected: FAIL because response parsing and merge enforcement are not implemented yet.

- [ ] **Step 3: Write the minimal implementation**

Implement:
- raw-response capture
- JSON extraction from plain text or fenced code blocks
- top-level contract ownership checks
- shared-state merge for the current stage only
- manifest updates after response application

- [ ] **Step 4: Re-run the focused test file**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_orchestrator -v`
Expected: PASS for the response-recording and merge tests.

## Chunk 3: CLI Flow And Regression Coverage

### Task 3: Expose the external-session workflow through a CLI and verify regressions

**Files:**
- Modify: `tools/question_generator/cli.py`
- Modify: `tools/question_generator/orchestrator.py`
- Modify: `tests/question_generator/test_cli.py`
- Test: `tests/question_generator/test_orchestrator.py`
- Test: `tests/question_generator/test_cli.py`
- Test: `tests/question_generator/test_assembler.py`

- [ ] **Step 1: Write the failing CLI tests**

Add tests that assert:
- the CLI can initialize a run
- the CLI can prepare a stage prompt into artifacts
- the CLI can apply a response file and update the run manifest/state

- [ ] **Step 2: Run the focused CLI and orchestrator tests to verify they fail**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_cli tests.question_generator.test_orchestrator -v`
Expected: FAIL because the CLI commands do not exist yet.

- [ ] **Step 3: Write the minimal implementation**

Implement:
- subcommands for run initialization, stage preparation, and stage response application
- concise stdout messages that report written artifact paths
- any small compatibility changes needed for existing prompt-assembly CLI behavior

- [ ] **Step 4: Run the targeted regression suite**

Run: `conda run -n truth-seek python -m unittest tests.question_generator.test_cli tests.question_generator.test_orchestrator tests.question_generator.test_assembler tests.question_generator.test_contract_loading -v`
Expected: PASS

- [ ] **Step 5: Run the full question-generator test suite**

Run: `conda run -n truth-seek python -m unittest discover -s tests/question_generator -p 'test_*.py' -v`
Expected: PASS
