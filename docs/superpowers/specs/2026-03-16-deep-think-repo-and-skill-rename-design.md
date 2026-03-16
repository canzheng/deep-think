# Deep Think Repo And Skill Rename Design

**Status:** Draft working design

**Scope:** Define a two-phase rename strategy that makes `deep-think` the single
external identity for the product while removing machine-local absolute path
leaks from the repository. Internal engine names may remain
`question-generator` / `question_generator` during Phase 1 for stability.

## 1. Problem

The repository currently mixes multiple identities:
- repo/product name: `truth-seek`
- engine/workflow name: `question-generator`
- skill/package surfaces derived from `question-generator`

This creates user-facing confusion because the same system is described with
different names in docs, skill packaging, archive names, and runtime examples.

The repo also contains machine-local absolute paths such as `/Users/...`, which:
- leak local filesystem details into committed content
- make docs and skill references non-portable
- create install instructions that only work on one machine

## 2. Goals

Phase 1 goals:
- make `deep-think` the single external/product name
- rename the local repo to `deep-think`
- publish to a new GitHub repo for `deep-think`
- rename user-facing skill/package/archive surfaces to `deep-think`
- rename the Conda environment from `truth-seek` to `deep-think`
- remove machine-local absolute filesystem paths from committed repo content
- keep the runtime behavior intact

Phase 2 goals:
- optionally rename internal engine names from `question-generator` /
  `question_generator` to `deep-think` / `deep_think`

## 3. Non-Goals

Phase 1 does not:
- rename Python module paths under `tools/question_generator`
- rename prompt asset directories under `prompt/question-generator`
- rename test package names under `tests/question_generator`
- rewrite every historical design/plan doc unless needed for active references

## 4. Core Decision

Use a two-phase rename:

### Phase 1: External And Operational Rename

Rename:
- GitHub repo name
- local repo directory name
- skill/package/archive names
- Conda environment name
- user-facing docs and instructions

Do not rename:
- internal engine directories and module names

This phase should also eliminate absolute path leaks from committed content.

### Phase 2: Internal Engine Rename

Later, if desired, rename:
- `prompt/question-generator`
- `tools/question_generator`
- `tests/question_generator`

This is intentionally deferred because it is a larger refactor surface with
more import, path, and packaging risk.

## 5. Naming Model

After Phase 1:
- product/repo/skill/package name: `deep-think`
- internal engine/runtime name: `question-generator` / `question_generator`

This creates one clean external name while preserving internal stability.

## 6. Absolute Path Policy

No machine-local absolute filesystem paths may remain in committed repo content.

This applies to:
- docs
- skill instructions
- command references
- packaging notes
- tests unless the path is generated at runtime inside a temp directory

Allowed replacements:
- repo-relative paths such as `prompt/question-generator/...`
- skill-relative placeholders such as `{baseDir}`
- environment-driven configuration
- dynamically discovered paths at runtime

Disallowed examples:
- `/Users/canzheng/...`
- any hardcoded home-directory path
- any machine-specific absolute checkout location

## 7. Phase 1 Rename Surface

### 7.1. Repo And GitHub Surface

Rename:
- repository folder `truth-seek` -> `deep-think`
- remote target to a new GitHub repo for `deep-think`
- onboarding/docs that mention the repository remote

Do not require:
- renaming the existing GitHub repository in place

### 7.2. Environment Surface

Rename:
- Conda environment in `environment.yml`
- docs that say `conda run -n truth-seek`
- docs that say `conda activate truth-seek`

Target:
- `deep-think`

### 7.3. Skill And Package Surface

Rename user-facing skill/package names from `question-generator-skill` to
`deep-think`.

This includes:
- skill metadata names
- skill folder names if appropriate
- bundle archive names
- install examples

The OpenClaw package should still be allowed to carry the internal runtime
under `runtime/tools/question_generator/...` during Phase 1.

### 7.4. Docs And Command References

Update user-facing docs so they consistently say:
- `deep-think` for the product
- `question-generator runtime` only when describing the internal engine

Command references should:
- avoid absolute paths
- prefer repo-relative examples
- use placeholders where needed

### 7.5. Packaging Surface

OpenClaw bundle install and archive examples should use names like:
- `deep-think-openclaw-skill.tar.gz`
- `~/.openclaw/skills/deep-think`

Codex skill examples should also reflect the `deep-think` external name.

## 8. Files Most Likely To Change In Phase 1

Likely high-priority files:
- `README.md`
- `environment.yml`
- `skills/question-generator-skill/SKILL.md`
- `skills/question-generator-skill/references/commands.md`
- `skills/question-generator-skill/openclaw/SKILL.md`
- `tools/question_generator/openclaw_package.py`
- `prompt/question-generator/README.md`
- active design/spec docs that are still part of current workflow guidance

Likely operational changes outside file content:
- local folder rename
- GitHub repo rename
- remote URL update

## 9. Files Intentionally Deferred To Phase 2

Do not rename in Phase 1:
- `tools/question_generator/...`
- `prompt/question-generator/...`
- `tests/question_generator/...`
- import paths referring to `question_generator`

These remain the internal engine until the dedicated internal rename pass.

## 10. Migration Constraints

Phase 1 must preserve:
- current tests
- current packaged OpenClaw skill behavior
- current Codex skill behavior
- current prompt assembly
- current executor abstraction

The rename should be mostly textual and packaging-oriented rather than a runtime
refactor.

## 11. Recommended Execution Order

1. remove absolute path leaks from committed files
2. rename user-facing skill/package/archive surfaces to `deep-think`
3. rename docs and command examples to `deep-think`
4. rename Conda environment references
5. rename repo folder and GitHub repo
5. rename the local repo folder
6. create the new `deep-think` GitHub repo and set it as remote
7. update remotes and any remaining onboarding references

This order reduces the chance of broken docs and path assumptions during the
transition.

## 12. Risks

Main risks in Phase 1:
- stale references to `truth-seek` in docs or packaging helpers
- missed absolute path leaks in long-form docs
- skill install examples drifting from actual folder names
- Conda env rename not reflected consistently in docs or scripts

These risks are manageable with focused search-driven cleanup and tests.

## 13. Recommendation

Proceed with:
- Phase 1 external/product/operational rename to `deep-think`
- hard enforcement of “no machine-local absolute paths in committed content”
- no internal engine rename yet

Then decide later whether Phase 2 internal rename is worth the extra churn.
