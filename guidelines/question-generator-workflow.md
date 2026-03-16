# Question Generator Workflow

This document describes the recommended modular `v7` stage workflow.

The workflow is organized as sequential stages that write into a shared state
file. Each stage should:
- read the current state
- update only the fields it owns
- avoid redoing upstream work unless a feedback loop is explicitly triggered
- be assembled from its stage prompt template, its contract, the current shared
  state, and the routed adapters selected from `routing`

Canonical state template:
- `prompt/question-generator/contracts/shared_state_schema.json`

Reference prompt:
- `prompt/question-generator/question-generator-modular.md`

Assembler runtime:
- `tools/question_generator/assembler.py`
- `tools/question_generator/cli.py`

Checked-in recipe for the end-to-end workflow:
- `prompt/question-generator/recipes/non-render.recipe.json`

## Workflow Overview

1. Routing
2. Boundary
3. Structure
4. Scenarios
5. Question Generation
6. Evidence Planning
7. Decision Logic
8. Signal Translation
9. Monitoring
10. Render

Allowed feedback loops:
- Questions -> Structure
- Evidence plan -> Scenarios

Use these loops only when a killer question exposes:
- a missing stakeholder
- a broken mechanism
- a hidden bottleneck
- a scenario branch that was structurally missed

## Shared State Rules

The state file should be carried throughout the workflow and treated as the
single source of truth for intermediate reasoning.

Run-artifact rule:
- persist prompts and model replies for every stage as run artifacts
- persist the response schema and Codex stdout/stderr artifacts for every
  automatic stage run
- do not store those artifacts inside shared state
- `shared_state.json` remains the only analysis object passed between stages

Answering-session rule:
- the orchestrator should call the answering session automatically
- each stage should use a fresh ephemeral Codex session
- the answering session should always use `gpt-5.4` with `high` reasoning

## How To Use The State File

1. Start from a minimal topic bootstrap payload such as
   `{"topic": "<raw user request>"}` and treat
   `prompt/question-generator/contracts/shared_state_schema.json` as the schema
   for the live state, not as a run-instance template.
2. Run the workflow stages in order.
3. After each stage, update only the state sections that stage owns.
4. Persist the updated shared state and pass it to the next stage.
5. Run the stage in a fresh ephemeral Codex answering session.
6. Persist the stage prompt, response schema, raw reply, parsed reply, and
   Codex stdout/stderr as run artifacts.
7. If a feedback loop is triggered, update the relevant upstream section and
   then continue forward again.
8. At render time, derive the prompt context from the accumulated shared state
   using the render contract's `reads_required_common` and
   `reads_by_output_mode` declarations, then render with the selected runtime
   subtemplate.
9. The renderer should use only shared-state-derived context as analysis input
   and should not inspect side artifacts or invent new analysis.

Recipe execution:
- use `run-recipe` when you want the orchestrator to execute a checked-in stage sequence
- the checked-in recipe runs `Routing` through `Render`
- use stage-level commands if you want to pause before `Render` and inspect the pre-render state independently

State rules:
- Routing must be completed before any downstream task runs.
- Downstream tasks should consume the selected adapters, not reclassify the
  problem casually.
- Contracts, not the old guidance files, define each stage's required and
  optional upstream stage dependencies plus adapter dependencies.
- The renderer should format contract-selected slices of accumulated state, not
  invent new analysis.
- If a downstream stage invalidates an upstream assumption, update the state and
  explicitly mark the feedback loop that was triggered.

## Stage 1 - Routing

Stage prompt:
- `prompt/question-generator/stages/01-routing.md`

Stage contract:
- `prompt/question-generator/contracts/01-routing.contract.json`


## Stage 2 - Boundary

Stage prompt:
- `prompt/question-generator/stages/02-boundary.md`

Stage contract:
- `prompt/question-generator/contracts/02-boundary.contract.json`


## Stage 3 - Structure

Stage prompt:
- `prompt/question-generator/stages/03-structure.md`

Stage contract:
- `prompt/question-generator/contracts/03-structure.contract.json`


## Stage 4 - Scenarios

Stage prompt:
- `prompt/question-generator/stages/04-scenarios.md`

Stage contract:
- `prompt/question-generator/contracts/04-scenarios.contract.json`


## Stage 5 - Question Generation

Stage prompt:
- `prompt/question-generator/stages/05-question-generation.md`

Stage contract:
- `prompt/question-generator/contracts/05-question-generation.contract.json`


## Stage 6 - Evidence Planning

Stage prompt:
- `prompt/question-generator/stages/06-evidence-planning.md`

Stage contract:
- `prompt/question-generator/contracts/06-evidence-planning.contract.json`


## Stage 7 - Decision Logic

Stage prompt:
- `prompt/question-generator/stages/07-decision-logic.md`

Stage contract:
- `prompt/question-generator/contracts/07-decision-logic.contract.json`


## Stage 8 - Signal Translation

Stage prompt:
- `prompt/question-generator/stages/08-signal-translation.md`

Stage contract:
- `prompt/question-generator/contracts/08-signal-translation.contract.json`


## Stage 9 - Monitoring

Stage prompt:
- `prompt/question-generator/stages/09-monitoring.md`

Stage contract:
- `prompt/question-generator/contracts/09-monitoring.contract.json`


## Stage 10 - Render

Stage prompt:
- `prompt/question-generator/stages/10-render.md`

Stage contract:
- `prompt/question-generator/contracts/10-render.contract.json`


## Stage Ownership Summary

Routing owns:
- classification
- adapter selection

Boundary owns:
- scope
- object definition

Structure owns:
- actors
- incentives
- constraints
- mechanism
- bottlenecks

Scenarios own:
- branch logic
- alternative paths

Question Generation owns:
- research agenda
- killer unknowns

Evidence Planning owns:
- proof strategy
- uncertainty mapping

Decision Logic owns:
- action thresholds
- staging
- reversibility

Signal Translation owns:
- observables
- update rules

Monitoring owns:
- operational watch layer

Render owns:
- formatting only

## Quality Bar

Good workflow behavior:
- separate actors from mechanisms
- separate mechanisms from evidence
- separate evidence from signals
- separate signals from decisions
- use adapters to shape emphasis, not to replace structure
- write enough structured state that rendering is mostly deterministic

Bad workflow behavior:
- routing that already argues the conclusion
- structure work that skips incentives or constraints
- evidence work that replaces diagnosis with source dumping
- decision work that ignores reversibility or evidence threshold
- rendering that invents claims not present in state
