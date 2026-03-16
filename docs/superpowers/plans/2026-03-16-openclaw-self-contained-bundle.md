# OpenClaw Self-Contained Bundle Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the OpenClaw packaging artifact into a self-contained bundle with packaged runtime/assets, vendored `chevron`, and persistent package-owned executor capability config.

**Architecture:** Keep the canonical repo runtime and prompt assembly as the source of truth, but add a package builder and package-relative runtime support so the OpenClaw bundle can run with plain `python3`. The OpenClaw executor will use a package-owned config file to remember whether JSON stages should use `llm-task` or the chat fallback, probing only on first run when the mode is `auto`.

**Tech Stack:** Python 3, `unittest`, existing question-generator runtime, OpenClaw Gateway chat-completions, optional `llm-task`, vendored `chevron`.

---

## Chunk 1: Persistent Executor Capability Config

### Task 1: Add failing tests for package-owned OpenClaw executor config

**Files:**
- Modify: `tests/question_generator/test_executors.py`
- Create: `tools/question_generator/openclaw_config.py`

- [ ] **Step 1: Write the failing tests**

Add tests covering:
- loading default executor mode as `auto`
- persisting `llm-task` after a successful first probe
- persisting `chat_fallback` after a not-found `llm-task` response
- honoring an explicit runtime override over persisted config
- downgrading persisted `llm-task` to `chat_fallback` when `llm-task` later becomes unavailable
- preserving the JSON fallback path, including:
  - JSON-hardening prompt wrapper on fallback
  - one repair pass after invalid JSON
  - local parse/validate remaining the gate before success

- [ ] **Step 2: Run the focused test file to verify it fails**

Run:

```bash
conda run -n truth-seek python -m unittest tests.question_generator.test_executors -v
```

Expected:
- FAIL because the package-owned config model and persistence behavior do not exist yet

- [ ] **Step 3: Implement the package-owned config helpers**

Create a focused helper module for:
- config path resolution
- reading/writing the packaged runtime config JSON
- normalizing executor mode values: `auto`, `llm-task`, `chat_fallback`

- [ ] **Step 4: Update the OpenClaw executor to use the new config**

Modify the executor so that:
- it reads the packaged config on startup
- `auto` probes `llm-task` once and persists the result
- later runs use the stored mode directly
- explicit overrides still take precedence
- a later not-found result while in `llm-task` mode downgrades the stored mode
- the existing chat fallback keeps the current safety guarantees:
  - JSON-hardening wrapper
  - one repair pass
  - local validation before returning success

- [ ] **Step 5: Re-run the focused test file to verify it passes**

Run:

```bash
conda run -n truth-seek python -m unittest tests.question_generator.test_executors -v
```

Expected:
- PASS for the new config persistence scenarios and existing executor coverage

## Chunk 2: Self-Contained OpenClaw Bundle Layout

### Task 2: Add failing tests for package-relative runtime and bundle assembly

**Files:**
- Modify: `tests/question_generator/test_cli.py`
- Modify: `tests/question_generator/test_orchestrator.py`
- Create: `tests/question_generator/test_openclaw_package.py`
- Create: `tools/question_generator/openclaw_package.py`
- Modify: `tools/question_generator/pathing.py`
- Modify: `tools/question_generator/orchestrator.py`
- Modify: `tools/question_generator/cli.py`

- [ ] **Step 1: Write the failing tests**

Add tests covering:
- package path overrides for prompt/contracts resolution
- building the OpenClaw package into `skills/question-generator-skill/openclaw/`
- inclusion of packaged runtime assets and packaged config
- CLI support for refreshing the OpenClaw package bundle

- [ ] **Step 2: Run the relevant tests to verify they fail**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_cli \
  tests.question_generator.test_orchestrator \
  tests.question_generator.test_openclaw_package -v
```

Expected:
- FAIL because package-relative path overrides and bundle assembly do not exist yet

- [ ] **Step 3: Add package-relative path support**

Refactor path resolution so the runtime can operate from either:
- the canonical repo layout
- a packaged OpenClaw bundle root

Use a small configuration surface instead of duplicating orchestration logic.

- [ ] **Step 4: Implement the OpenClaw package builder**

Create a builder that assembles the self-contained bundle with:
- `SKILL.md`
- packaged runtime modules
- packaged prompt assets
- packaged contracts/recipes/render templates
- `config/runtime.json`
- vendored `chevron`

The builder should also ensure the package-owned `tmp/question-runs` directory exists or is documented as runtime-created.

- [ ] **Step 5: Add a CLI entrypoint for package refresh**

Expose a command that refreshes the OpenClaw package artifact from the canonical repo sources so the bundle can be regenerated consistently after future runtime changes.

- [ ] **Step 6: Re-run the targeted tests to verify they pass**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_cli \
  tests.question_generator.test_orchestrator \
  tests.question_generator.test_openclaw_package -v
```

Expected:
- PASS with the package builder and path overrides in place

## Chunk 3: Bundle Instructions, Vendored Dependency, And End-to-End Verification

### Task 3: Update the packaged skill artifact and verify the end-to-end focused suite

**Files:**
- Modify: `skills/question-generator-skill/openclaw/SKILL.md`
- Create or refresh: `skills/question-generator-skill/openclaw/config/runtime.json`
- Create or refresh: `skills/question-generator-skill/openclaw/runtime/...`
- Create or refresh: `skills/question-generator-skill/openclaw/vendor/chevron/...`
- Modify: `README.md`
- Modify: `prompt/question-generator/README.md`
- Modify: `docs/superpowers/specs/2026-03-16-openclaw-skill-packaging-and-executor-design.md`

- [ ] **Step 1: Update the packaged OpenClaw skill instructions**

Revise the packaged `SKILL.md` so it:
- requires `python3` instead of `conda`
- states `llm-task` is a soft dependency
- describes the persisted executor capability behavior
- explains that the bundle carries its own runtime and prompt assets
- explains that the workflow is multi-step and can take time to complete

- [ ] **Step 2: Refresh the bundle contents**

Run the package refresh command so the committed OpenClaw artifact includes:
- the latest runtime files
- packaged config
- vendored `chevron`

- [ ] **Step 3: Run the focused verification suite**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_cli \
  tests.question_generator.test_executors \
  tests.question_generator.test_openclaw_package \
  tests.question_generator.test_orchestrator -v
```

Expected:
- PASS with 0 failures

- [ ] **Step 4: Do a bundle sanity check**

Verify that the packaged artifact contains at least:
- `skills/question-generator-skill/openclaw/SKILL.md`
- `skills/question-generator-skill/openclaw/config/runtime.json`
- `skills/question-generator-skill/openclaw/runtime/tools/question_generator/...`
- `skills/question-generator-skill/openclaw/runtime/prompt/question-generator/...`
- `skills/question-generator-skill/openclaw/vendor/chevron/...`

- [ ] **Step 5: Summarize residual risks**

Call out any remaining gaps, especially:
- no live OpenClaw Gateway smoke test
- vendor refresh expectations when `chevron` changes
- any package-root assumptions that remain intentionally configurable
