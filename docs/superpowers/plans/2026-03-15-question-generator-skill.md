# Question Generator Skill Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:executing-plans or
> superpowers:subagent-driven-development when implementing this plan. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a topic-only skill workflow for the question generator that
boots from a raw topic, pauses after routing for user verification, patches
routing directly without rerunning it, and resumes the remaining recipe to the
final render.

**Architecture:** Keep the staged question-generator workflow intact and add a
thin skill-facing orchestration layer around it. Introduce topic bootstrap and
existing-run recipe execution in the Python runtime, plus a deterministic
routing patch helper. Put the human confirmation behavior in the skill
instructions, not in the prompt-stage system.

**Tech Stack:** Python 3 via `conda run -n truth-seek`, existing
question-generator runtime, `unittest`, markdown docs, repo-local skill files.

---

## File Structure

**Files to create**
- `docs/superpowers/specs/2026-03-15-question-generator-skill-design.md`
- `docs/superpowers/plans/2026-03-15-question-generator-skill.md`
- `tools/question_generator/bootstrap.py`
- `skills/question-generator-skill/SKILL.md`
- `skills/question-generator-skill/references/commands.md`

**Files to modify**
- `tools/question_generator/orchestrator.py`
- `tools/question_generator/cli.py`
- `tests/question_generator/test_orchestrator.py`
- `tests/question_generator/test_cli.py`
- `README.md`
- `prompt/question-generator/README.md`

## Chunk 1: Lock In Bootstrap And Resume Behavior With Tests

### Task 1: Add failing orchestrator tests for topic bootstrap and routing patching

**Files:**
- Modify: `tests/question_generator/test_orchestrator.py`

- [ ] **Step 1: Add a failing test for topic bootstrap state creation**

Assert that a helper can produce:

```json
{"topic": "<raw topic>"}
```

- [ ] **Step 2: Add a failing test for topic-based run initialization**

Assert that initializing from a topic writes a run manifest and a
`shared_state.json` containing only `topic`.

- [ ] **Step 3: Add a failing test for partial routing patch merge**

Assert that:
- only `routing` is updated
- unrelated routing fields remain unchanged
- nested `classification_rationales` can be patched

- [ ] **Step 4: Add a failing test for recipe execution on an existing run**

Assert that execution can start from `boundary` and proceeds in the expected
order without reinitializing the run.

- [ ] **Step 5: Run focused orchestrator tests and confirm failure**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_orchestrator -v
```

Expected:
- FAIL because the new helpers and commands do not exist yet

## Chunk 2: Implement Bootstrap, Routing Patching, And Existing-Run Recipe Execution

### Task 2: Add runtime helpers

**Files:**
- Create: `tools/question_generator/bootstrap.py`
- Modify: `tools/question_generator/orchestrator.py`

- [ ] **Step 1: Add a minimal topic bootstrap helper**

Implement a helper that returns:

```python
{"topic": topic}
```

- [ ] **Step 2: Add topic-based run initialization**

Implement an orchestrator helper that writes the minimal topic-backed
`shared_state.json`.

- [ ] **Step 3: Add routing patch merge support**

Implement a helper that deep-merges a partial patch into `routing` only.

- [ ] **Step 4: Add recipe execution against an existing run directory**

Implement a helper that:
- loads a recipe
- optionally skips stages before `start_stage`
- runs the remaining stages against the existing `run_dir`

- [ ] **Step 5: Run focused orchestrator tests**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_orchestrator -v
```

Expected:
- PASS for the new runtime helpers

## Chunk 3: Expose The New Runtime Paths In The CLI

### Task 3: Add CLI commands for topic bootstrap and resume

**Files:**
- Modify: `tools/question_generator/cli.py`
- Modify: `tests/question_generator/test_cli.py`

- [ ] **Step 1: Add failing CLI tests**

Cover:
- `init-topic-run`
- `update-routing`
- `run-recipe-on-run`
- `run-topic`

- [ ] **Step 2: Implement CLI parsing and dispatch**

Add the new commands and keep the existing commands unchanged.

- [ ] **Step 3: Support `run-topic --pause-after routing`**

This should initialize the run, execute through `routing`, and return the run
directory so the skill can stop for human verification.

- [ ] **Step 4: Run focused CLI tests**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_cli -v
```

Expected:
- PASS for the new command surface

## Chunk 4: Add The Skill Source And Repo Docs

### Task 4: Document the operator workflow

**Files:**
- Create: `skills/question-generator-skill/SKILL.md`
- Create: `skills/question-generator-skill/references/commands.md`
- Modify: `README.md`
- Modify: `prompt/question-generator/README.md`

- [ ] **Step 1: Write the repo-local skill**

Document:
- topic-only input
- routing confirmation pause
- never rerun routing
- direct routing patching from clear user corrections
- Conda-only Python commands

- [ ] **Step 2: Add a short command reference**

Include the exact runtime commands the skill should use.

- [ ] **Step 3: Update repo docs**

Clarify:
- `shared_state_schema.json` is a schema, not an instance template
- there is now a topic-first operator flow

- [ ] **Step 4: Run doc-adjacent tests if any assumptions changed**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_cli \
  tests.question_generator.test_orchestrator -v
```

Expected:
- PASS

## Chunk 5: Run Final Verification

### Task 5: Verify the implemented surface end to end

**Files:**
- Verify: `tools/question_generator/bootstrap.py`
- Verify: `tools/question_generator/orchestrator.py`
- Verify: `tools/question_generator/cli.py`
- Verify: `skills/question-generator-skill/SKILL.md`
- Verify: `README.md`
- Verify: `prompt/question-generator/README.md`

- [ ] **Step 1: Run the focused test suite**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_cli \
  tests.question_generator.test_orchestrator -v
```

Expected:
- PASS with 0 failures

- [ ] **Step 2: Sanity-check the new CLI help text**

Run:

```bash
conda run -n truth-seek python -m tools.question_generator.cli --help
conda run -n truth-seek python -m tools.question_generator.cli init-topic-run --help
conda run -n truth-seek python -m tools.question_generator.cli update-routing --help
conda run -n truth-seek python -m tools.question_generator.cli run-recipe-on-run --help
conda run -n truth-seek python -m tools.question_generator.cli run-topic --help
```

Expected:
- help text renders cleanly for the new commands

- [ ] **Step 3: Summarize residual risks**

Check for:
- ambiguity handling still living only in the skill layer
- no automated validation of user-supplied routing corrections beyond field
  ownership
