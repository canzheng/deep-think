# OpenClaw Skill Packaging And Executor Design

**Status:** Approved design

**Scope:** Define the OpenClaw packaging artifact for the question-generator so
it can run as a self-sufficient skill bundle without `conda`, while preserving
the existing staged workflow, prompt assembly, and executor abstraction
direction.

## 1. Goals

The design goals are:
- keep the current Codex skill setup as the canonical source of truth
- produce an additional OpenClaw packaging artifact
- make the OpenClaw package self-sufficient
- remove the `conda` dependency from the OpenClaw package
- keep prompt assembly, contracts, and shared-state semantics unchanged
- preserve the routing confirmation step
- support OpenClaw-native reasoning with a soft dependency on `llm-task`

## 2. Non-Goals

This design does not:
- replace the canonical Codex skill
- move workflow orchestration into the skill body
- require the main repo checkout at runtime
- require `llm-task` to be installed

## 3. Canonical Source Of Truth

The main repository remains canonical for:
- skill workflow wording
- stage templates
- contracts
- recipes
- runtime modules

The OpenClaw package is a derived artifact assembled from the canonical repo.
Changes should flow in this order:

1. update the canonical repo runtime, prompts, and skill wording
2. refresh the OpenClaw packaging artifact from those sources

## 4. Packaging Model

### 4.1. Self-Contained Bundle

The OpenClaw artifact must ship with everything needed to run the workflow
except the OpenClaw host itself and `python3`.

The bundle must include:
- OpenClaw-oriented `SKILL.md`
- packaged Python runtime modules for the question generator
- packaged prompt assets
- packaged contracts and schemas
- packaged recipes
- packaged render support files
- vendored `chevron`
- packaged persistent config for executor capability selection
- a plain `python3` entrypoint for the workflow

The bundle must not depend on:
- `conda`
- the main repo being present on disk
- imports or file paths outside the package root

### 4.2. Proposed Layout

One reasonable package layout is:

```text
question-generator-openclaw/
  SKILL.md
  config/
    runtime.json
  runtime/
    tools/question_generator/...
    prompt/question-generator/...
    vendor/chevron/...
  scripts/
    run_topic.py
    update_routing.py
    resume_run.py
  tmp/
    question-runs/   # created at runtime, not checked in
```

The exact directory names may change, but the package must satisfy these
properties:
- all runtime code uses package-relative paths only
- all prompt and contract assets are bundled with the runtime
- package-owned config lives inside the bundle layout rather than in `tmp/`
- writable run artifacts are separated from static packaged assets

### 4.3. Runtime Working Directory

Run artifacts should live under a writable package-owned scratch directory,
defaulting to:
- `tmp/question-runs/`

This keeps:
- the static bundle immutable
- generated runs easy to inspect and clean up
- OpenClaw executions independent from the source repo layout

## 5. Dependency Model

### 5.1. Hard Dependencies

The OpenClaw package should require only:
- `python3`

### 5.2. Vendored Python Dependency

The current non-stdlib Python dependency is:
- `chevron==0.14.0`

Because this surface is small, the OpenClaw package should vendor `chevron`
inside the bundle instead of requiring `pip install` or `conda`.

Reasons:
- avoids a runtime installer step
- keeps the package self-sufficient
- removes network/package-index assumptions
- is lower-friction than shipping a prebuilt environment

### 5.3. Soft Dependency On `llm-task`

The OpenClaw package has a soft dependency on `llm-task`.

Meaning:
- if `llm-task` is available, JSON-returning stages should use it
- if `llm-task` is unavailable, the package must still function correctly
- local parse and schema validation remain mandatory in both cases

This soft-dependency status should be stated clearly in the packaged
OpenClaw `SKILL.md`.

## 6. Execution Model

### 6.1. Workflow Behavior

The packaged OpenClaw skill preserves the same operator workflow:

1. treat the user's natural-language topic of interest as the raw `topic`
2. bootstrap minimal workflow state
3. run `Routing`
4. pause for user confirmation
5. patch `routing` directly from clear user corrections
6. never rerun `Routing`
7. continue from `Boundary`
8. return the final rendered artifact

### 6.2. Prompt Assembly

Prompt assembly must stay unchanged.

These layers remain canonical and should be copied into the package rather than
reinterpreted:
- prompt templates
- contracts
- shared-state schema
- recipes
- render support files

### 6.3. OpenClaw Reasoning Strategy

Executor behavior should be:
- prefer `llm-task` for JSON-returning non-render stages
- fall back to OpenClaw Gateway chat-completions when `llm-task` is absent
- use plain chat-completions for `render`
- keep local JSON parse and schema validation as the final guardrail
- allow one repair pass in the chat-completions fallback path

### 6.4. Persistent Executor Capability Config

The package should persist the JSON-stage executor choice so it does not need
to probe `llm-task` on every run.

Supported modes:
- `auto`
- `llm-task`
- `chat_fallback`

Default behavior:
- the packaged config starts in `auto`
- on the first run, the executor tries `llm-task`
- if `llm-task` succeeds, persist `llm-task`
- if `llm-task` is unavailable, persist `chat_fallback`

Subsequent behavior:
- use the persisted executor choice directly
- do not retry `llm-task` unless the operator or user explicitly resets the
  mode to `auto` or forces `llm-task`

Recovery behavior:
- if the persisted mode is `llm-task` and a later run returns a clear
  unavailable/not-found result, automatically downgrade the stored mode to
  `chat_fallback`

Override behavior:
- allow an explicit runtime or OpenClaw-config override to force:
  - `llm-task`
  - `chat_fallback`
  - `auto`

Recommended precedence:
1. explicit runtime override
2. packaged persistent config
3. default packaged value

The persistent config should live inside the package, not under `tmp/`, so the
capability decision remains part of the package-owned runtime state rather than
ephemeral run output.

### 6.4. JSON Fallback Behavior

When `llm-task` is unavailable, the executor should:

1. wrap the existing stage prompt with JSON-hardening instructions
2. call OpenClaw chat-completions
3. parse and validate locally
4. if invalid, issue one repair prompt with:
   - the original stage prompt
   - the invalid output
   - the parse or validation error
   - the expected schema
5. validate again locally

The JSON-hardening wrapper belongs in the executor layer, not in the canonical
prompt assets.

## 7. Required Runtime Changes For Packaging

To support the self-contained package, the runtime must avoid assumptions that:
- the repo root is the working directory
- `conda run -n truth-seek` is available
- prompt assets live outside the package

The package entrypoints should resolve:
- runtime root
- prompt root
- contracts root
- output scratch directory

all relative to the package itself.

## 8. OpenClaw Skill Metadata

The packaged `SKILL.md` should:
- require `python3`
- avoid requiring `conda`
- state that `llm-task` is a soft dependency
- explain that the workflow is multi-step and may take time
- explain that the package includes its own runtime and prompt assets

## 9. Tradeoff Decision

Three approaches were considered:

1. Thin adapter to the repo
   - smallest artifact
   - not self-sufficient
   - rejected

2. Self-contained skill bundle with vendored `chevron`
   - portable
   - no `conda`
   - no runtime package install
   - recommended

3. Prebuilt environment bundled with the package
   - fastest runtime bootstrap
   - heavier artifact
   - unnecessary for the current dependency surface

The selected approach is:
- self-contained OpenClaw bundle
- vendored `chevron`
- bundled runtime and prompt assets
- no `conda`
- soft dependency on `llm-task`

## 10. Implementation Implications

The next implementation pass should:
- build a package-local runtime layout
- vendor `chevron`
- replace `conda` assumptions in the OpenClaw artifact
- update the packaged `SKILL.md`
- ensure package-relative asset resolution
- keep the executor abstraction intact

The Codex-native repo workflow should remain unchanged.
