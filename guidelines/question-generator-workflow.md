# Question Generator Workflow

This document describes the recommended modular `v7` stage workflow.

The workflow is organized as sequential stages that write into a shared state
file. Each stage should:
- read the current state
- update only the fields it owns
- avoid redoing upstream work unless a feedback loop is explicitly triggered

Canonical state template:
- `/Users/canzheng/Work/sandbox/truth-seek/research-state/shared_state_schema.json`

Reference prompt:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/question-generator-modular.md`

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

## How To Use The State File

1. Initialize a fresh copy of
   `/Users/canzheng/Work/sandbox/truth-seek/research-state/shared_state_schema.json`
   for the current topic.
2. Run the workflow stages in order.
3. After each stage, update only the state sections that stage owns.
4. Persist the full state and pass it to the next stage.
5. If a feedback loop is triggered, update the relevant upstream section and
   then continue forward again.
6. At render time, pass the full accumulated state plus the selected
   output-mode module to the renderer.
7. The renderer should treat the shared state as its sole analysis input.

State rules:
- Routing must be completed before any downstream task runs.
- Module selection should be recorded immediately after routing.
- Downstream tasks should consume the selected adapters, not reclassify the
  problem casually.
- The renderer should format accumulated state, not invent new analysis.
- If a downstream stage invalidates an upstream assumption, update the state and
  explicitly mark the feedback loop that was triggered.

## Stage 1 - Routing

Stage prompt:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/01-routing.md`

Stage guidance:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/01-routing-guidance.md`


## Stage 2 - Boundary

Stage prompt:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/02-boundary.md`

Stage guidance:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/02-boundary-guidance.md`


## Stage 3 - Structure

Stage prompt:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/03-structure.md`

Stage guidance:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/03-structure-guidance.md`


## Stage 4 - Scenarios

Stage prompt:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/04-scenarios.md`

Stage guidance:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/04-scenarios-guidance.md`


## Stage 5 - Question Generation

Stage prompt:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/05-question-generation.md`

Stage guidance:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/05-question-generation-guidance.md`


## Stage 6 - Evidence Planning

Stage prompt:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/06-evidence-planning.md`

Stage guidance:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/06-evidence-planning-guidance.md`


## Stage 7 - Decision Logic

Stage prompt:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/07-decision-logic.md`

Stage guidance:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/07-decision-logic-guidance.md`


## Stage 8 - Signal Translation

Stage prompt:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/08-signal-translation.md`

Stage guidance:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/08-signal-translation-guidance.md`


## Stage 9 - Monitoring

Stage prompt:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/09-monitoring.md`

Stage guidance:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/09-monitoring-guidance.md`


## Stage 10 - Render

Stage prompt:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/10-render.md`

Stage guidance:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/10-render-guidance.md`


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
