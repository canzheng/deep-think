# Question Generator Skill Design

**Status:** Approved working design

**Scope:** This document defines how the modular question-generator becomes a
topic-only skill that accepts natural-language user input, pauses for routing
verification, and then produces the final rendered artifact.

## 1. Purpose

The repository already contains:
- a staged prompt workflow
- durable shared state
- an orchestrator that can execute all stages
- a render step that returns the final artifact

What it does not yet provide is a clean skill-level workflow for:
- starting from a raw user topic instead of a prebuilt state file
- pausing after `Routing` for human confirmation
- applying routing corrections without rerunning `Routing`
- resuming the remaining workflow after confirmation

This design adds that missing user-facing layer while preserving the existing
stage contracts and prompt assets.

## 2. Core Decisions

### 2.1. Topic-Only Entry

The skill accepts only one initial input:
- the user's natural-language topic/request

The full user request becomes the raw `topic` field in shared state.

The skill does not ask the user to provide structured routing fields up front.

### 2.2. Routing Is The Bootstrap Analysis Stage

`Routing` remains the first workflow stage.

It reads only:
- `topic`

It writes only:
- `routing`

No new bootstrap analysis stage is added.

### 2.3. Human Confirmation Happens At The Skill Layer

After `Routing`, the skill must pause and show the inferred routing fields to
the user for confirmation.

This confirmation step is not a workflow stage and does not belong in the
prompt assets or stage contracts.

It belongs in the skill because it is:
- interactive
- user-facing
- specific to the operator workflow, not the analysis model

### 2.4. Routing Is Never Rerun

If the user corrects routing after the first pass:
- Codex must directly update the affected `routing` fields
- Codex must not rerun the `Routing` stage

If the user's correction is ambiguous:
- Codex should ask one focused follow-up question
- Codex should not guess
- Codex should still not rerun `Routing`

### 2.5. Shared State Remains The Sole Workflow State

The live `shared_state.json` remains the only analysis object passed between
stages.

Prompt artifacts, raw responses, and other run artifacts remain outside shared
state.

## 3. Target User Workflow

### 3.1. Topic Submission

The user gives one natural-language topic such as:
- "Should we expand Atlas into healthcare next quarter?"

The skill creates the minimal initial shared state:

```json
{
  "topic": "Should we expand Atlas into healthcare next quarter?"
}
```

### 3.2. Routing Pass

The skill initializes a run from that topic and executes only `Routing`.

The result is a run directory containing:
- `shared_state.json`
- stage artifacts for `routing`

### 3.3. Routing Review

The skill summarizes the inferred routing fields for the user:
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

The user may:
- confirm everything
- correct selected fields in natural language

### 3.4. Direct Routing Patch

Codex interprets the user's clarification and updates only the clearly affected
fields in `routing`.

Examples:
- "Make this a research memo, not a decision memo."
- "The time horizon is the next 12 months, not the next quarter."
- "This is policy/regulation first and company strategy second."

Codex may also update:
- matching `classification_rationales`
- `assumptions` when the user explicitly replaces them

Codex must preserve unaffected routing fields.

### 3.5. Resume Remaining Workflow

After confirmation or correction, the skill resumes the recipe from
`Boundary` through `Render`.

The final artifact is returned directly to the user.

## 4. Runtime Changes

### 4.1. Topic Bootstrap Helper

Add a small helper that converts a raw topic string into the minimal initial
state object:

```json
{
  "topic": "<raw user request>"
}
```

The helper should not fabricate placeholder sections for downstream state.

### 4.2. Topic-Based Run Initialization

Add an orchestrator entrypoint that initializes a run from a topic instead of
copying an existing state file.

This should write:
- `shared_state.json` with only the `topic` field
- a normal run manifest

### 4.3. Resume Existing Run

Add an orchestrator entrypoint that executes a recipe against an existing
`run_dir`, optionally starting from a named stage.

This is required so the workflow can:
- stop after `Routing`
- accept user verification
- continue from `Boundary`

### 4.4. Routing Patch Helper

Add a helper that applies a partial update to the `routing` section only.

The patch must:
- merge only into `routing`
- preserve unrelated routing fields
- allow nested updates inside `classification_rationales`

This helper is deterministic persistence only.
Natural-language interpretation remains the skill's job.

## 5. CLI Changes

Recommended new commands:

- `init-topic-run`
  - initialize a run from a raw topic
- `update-routing`
  - apply a partial routing patch to an existing run
- `run-recipe-on-run`
  - execute a recipe against an existing run, optionally from a named stage
- `run-topic`
  - convenience command that initializes from topic and optionally pauses after
    `routing`

Preferred skill usage:
- `init-topic-run`
- `run-stage --stage routing`
- user verification
- `update-routing`
- `run-recipe-on-run --start-stage boundary`

This keeps the interactive pause explicit and easy to reason about.

## 6. Skill Packaging

Create a repo-local skill source that documents the operator workflow.

The skill should instruct Codex to:
- treat the full user message as `topic`
- run Python only through `conda run -n truth-seek`
- initialize the topic run
- run `Routing`
- present the inferred routing summary for confirmation
- patch routing directly from clear user corrections
- never rerun `Routing`
- resume the workflow from `Boundary`
- return the final rendered artifact

The skill may include:
- `SKILL.md`
- `references/commands.md`

`agents/openai.yaml` is optional and can be added later if UI metadata becomes
important.

## 7. Testing Strategy

Add tests for:
- topic bootstrap state creation
- topic-based run initialization
- routing patch merge behavior
- recipe execution against an existing run directory
- CLI plumbing for the new commands

The tests should mock Codex execution where needed, following the current
orchestrator test pattern.

## 8. Non-Goals

This design does not:
- add a new workflow stage for routing review
- rerun `Routing` after user feedback
- change stage contracts for downstream stages
- replace the existing recipe-driven orchestrator
- require the user to provide structured routing fields up front
