# Deep Think Phase 1 Rename Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `deep-think` the single external/product name while removing machine-local absolute path leaks, without renaming the internal `question_generator` engine yet.

**Architecture:** Keep the runtime, prompt assembly, and internal Python/package paths stable in Phase 1. Limit the implementation surface to external naming, packaging, environment/docs references, and path hygiene. Add focused verification so the repo no longer commits `/Users/...` style paths and the OpenClaw/Codex packaging surfaces consistently use `deep-think`.

**Tech Stack:** Python 3, `unittest`, Conda environment metadata, markdown docs, Codex skill packaging, OpenClaw skill packaging, git remote configuration notes.

---

## File Structure

**Files likely to modify**
- `README.md`
- `environment.yml`
- `skills/question-generator-skill/SKILL.md`
- `skills/question-generator-skill/references/commands.md`
- `skills/question-generator-skill/openclaw/SKILL.md`
- `tools/question_generator/openclaw_package.py`
- `prompt/question-generator/README.md`
- `docs/superpowers/specs/2026-03-16-deep-think-repo-and-skill-rename-design.md`

**Files likely to create**
- `tests/question_generator/test_naming_and_path_hygiene.py`
- `docs/superpowers/plans/2026-03-16-deep-think-phase1-rename.md`

**Operational actions outside file edits**
- rename local checkout directory from `truth-seek` to `deep-think`
- create the new GitHub repository for `deep-think`
- point `origin` at the new GitHub repository

## Chunk 1: Guardrails For Naming And Path Hygiene

### Task 1: Add failing checks for external naming and absolute-path leaks

**Files:**
- Create: `tests/question_generator/test_naming_and_path_hygiene.py`
- Modify: `tests/question_generator/test_cli.py`

- [ ] **Step 1: Write a failing test for OpenClaw package naming**

Cover:
- the default OpenClaw bundle directory should move away from `skills/question-generator-skill/openclaw`
- package/archive-facing names should use `deep-think`

- [ ] **Step 2: Write a failing test for committed absolute path leaks**

Add a focused test that scans a curated set of active user-facing files and fails if it finds:
- `/Users/`
- `/home/`
- hardcoded checkout-specific absolute paths

Include at least:
- `README.md`
- `skills/question-generator-skill/SKILL.md`
- `skills/question-generator-skill/references/commands.md`
- `skills/question-generator-skill/openclaw/SKILL.md`
- `prompt/question-generator/README.md`

- [ ] **Step 3: Run the new focused tests to verify they fail**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_naming_and_path_hygiene \
  tests.question_generator.test_cli -v
```

Expected:
- FAIL because the current repo still uses `truth-seek` on external surfaces and still contains absolute path leaks

- [ ] **Step 4: Implement the minimum naming/path assertions needed for Phase 1**

Keep the test scope focused on:
- external/package names
- active docs and skill references
- no internal `question_generator` rename yet

- [ ] **Step 5: Re-run the focused tests and confirm they still fail for the right missing implementation**

Run:

```bash
conda run -n truth-seek python -m unittest \
  tests.question_generator.test_naming_and_path_hygiene \
  tests.question_generator.test_cli -v
```

Expected:
- still FAIL until the docs/package rename work is implemented

## Chunk 2: Rename The External Product Surface To Deep Think

### Task 2: Update user-facing naming, package paths, and environment references

**Files:**
- Modify: `README.md`
- Modify: `environment.yml`
- Modify: `skills/question-generator-skill/SKILL.md`
- Modify: `skills/question-generator-skill/references/commands.md`
- Modify: `skills/question-generator-skill/openclaw/SKILL.md`
- Modify: `prompt/question-generator/README.md`
- Modify: `tools/question_generator/openclaw_package.py`
- Modify: `tests/question_generator/test_openclaw_package.py`
- Modify: `tests/question_generator/test_cli.py`

- [ ] **Step 1: Update the package builder and related tests**

Rename the external package target so the OpenClaw bundle installs/builds under a `deep-think` surface rather than `question-generator-skill`.

Keep internal copied runtime paths unchanged.

- [ ] **Step 2: Rename the Codex and OpenClaw skill metadata**

Update skill-facing names/descriptions so:
- the visible skill/product name is `deep-think`
- internal references to the engine may still say `question-generator runtime` when needed

- [ ] **Step 3: Rename user-facing environment references**

Update:
- `environment.yml` environment name
- docs that say `conda run -n truth-seek`
- docs that say `conda activate truth-seek`

Target:
- `deep-think`

- [ ] **Step 4: Remove absolute machine-local paths from active user-facing files**

Replace hardcoded local checkout paths with:
- repo-relative paths
- `{baseDir}` in skill/package instructions
- generic placeholders where necessary

- [ ] **Step 5: Run the focused naming/path tests**

Run:

```bash
conda run -n deep-think python -m unittest \
  tests.question_generator.test_naming_and_path_hygiene \
  tests.question_generator.test_cli \
  tests.question_generator.test_openclaw_package -v
```

Expected:
- PASS with `deep-think` reflected on external/package surfaces
- PASS with no machine-local absolute path leaks in the scoped files

- [ ] **Step 6: Commit the rename-safe external surface changes**

```bash
git add README.md environment.yml skills/question-generator-skill/SKILL.md skills/question-generator-skill/references/commands.md skills/question-generator-skill/openclaw/SKILL.md prompt/question-generator/README.md tools/question_generator/openclaw_package.py tests/question_generator/test_naming_and_path_hygiene.py tests/question_generator/test_cli.py tests/question_generator/test_openclaw_package.py
git commit -m "refactor: rename external skill surface to deep-think"
```

## Chunk 3: Refresh Packaging And Document Repo Migration

### Task 3: Refresh the bundle, verify the repo, and document local/GitHub migration

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-03-16-deep-think-repo-and-skill-rename-design.md`
- Create or refresh: `skills/question-generator-skill/openclaw/...`

- [ ] **Step 1: Refresh the OpenClaw bundle after the rename**

Run:

```bash
conda run -n deep-think python -m tools.question_generator.cli refresh-openclaw-package
```

Verify the bundle reflects the external `deep-think` naming where appropriate while keeping the packaged runtime intact.

- [ ] **Step 2: Add concise migration notes for the local folder and new GitHub remote**

Document:
- rename local directory `truth-seek` -> `deep-think`
- create new GitHub repo
- update `origin` to the new repo

Do not script the GitHub-side creation inside the repo.

- [ ] **Step 3: Run the question-generator suite as the merge gate**

Run:

```bash
conda run -n deep-think python -m unittest discover -s tests/question_generator -p 'test_*.py'
```

Expected:
- PASS with 0 failures

- [ ] **Step 4: Run a final absolute-path sweep**

Run:

```bash
rg -n "/Users/|/home/" README.md environment.yml skills prompt tools tests docs
```

Expected:
- no hits in active committed Phase 1 surfaces

- [ ] **Step 5: Commit the refreshed bundle and migration docs**

```bash
git add README.md docs/superpowers/specs/2026-03-16-deep-think-repo-and-skill-rename-design.md skills/question-generator-skill/openclaw
git commit -m "docs: prepare deep-think repo migration"
```

## Chunk 4: Post-Repo-Rename Follow-Through

### Task 4: Apply the local folder rename and remote switch after code lands

**Files:**
- No committed file changes required

- [ ] **Step 1: Rename the local checkout directory**

Run after the code changes are merged and your shell is not relying on the old cwd.

Example:

```bash
mv /path/to/truth-seek /path/to/deep-think
```

- [ ] **Step 2: Point `origin` at the new GitHub repository**

Example:

```bash
git remote set-url origin <new-deep-think-repo-url>
git remote -v
```

Expected:
- fetch/push URLs point at the new `deep-think` repository

- [ ] **Step 3: Verify the renamed checkout still runs the test gate**

Run:

```bash
conda run -n deep-think python -m unittest discover -s tests/question_generator -p 'test_*.py'
```

Expected:
- PASS from the renamed local checkout

- [ ] **Step 4: Push to the new repository**

```bash
git push -u origin main
```

Expected:
- the `deep-think` repository becomes the canonical remote for Phase 1
