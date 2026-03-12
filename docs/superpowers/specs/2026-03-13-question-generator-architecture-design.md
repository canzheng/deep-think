# Question Generator Architecture Design

**Status:** Draft working design

**Scope:** This document describes the architecture of the modular
question-generator system as a whole. It covers the authored prompt assets, the
shared-state contract, the stage contracts, the prompt assembler runtime, the
intended orchestrator boundary, and the next design direction for schema
composition and richer section renderers.

## 1. Purpose

The question generator exists to turn an ambiguous user topic into a structured,
stage-by-stage research and decision workflow.

It does this by:
- routing the topic into a normalized problem frame
- building durable intermediate analysis state
- assembling one prompt per workflow stage
- constraining each stage with explicit output schemas
- producing a final deliverable in the requested output mode

The system is intentionally split into:
- authored prompt logic
- machine-readable contracts
- a dependency-light assembler runtime
- a future orchestrator layer that will execute stages, validate outputs, and
  merge them into shared state

## 2. Core Design Goals

The system should optimize for:
- explicitness over hidden prompt magic
- composability over monolithic prompt documents
- durable intermediate state over one-shot prose generation
- stage-local clarity over global prompt sprawl
- machine-readable contracts over implicit conventions
- human-auditable prompt assembly

The system should avoid:
- hidden dependencies between stages
- prompt instructions that only exist in prose and not in contracts
- render-time behavior that depends on undocumented heuristics
- forcing upstream analytical stages to act like final deliverable writers

## 3. Architectural Layers

The system has four main layers.

### 3.1. Modular Prompt Assets

These are the authored prompt files that define the prompt logic:
- host prompt:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/question-generator-modular.md`
- stage templates:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/`
- adapters:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/adapters/`
- output modes:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/output-modes/`

These files define what the model should do.

### 3.2. Contracts

These are the machine-readable rules that define how stages interact:
- stage contracts:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/*.contract.json`
- shared state contract:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/shared_state_schema.json`

Contracts define:
- what a stage reads
- what a stage may optionally read
- what routed dimensions a stage depends on
- what state entities a stage writes
- what output schema a stage must satisfy
- whether feedback is supported

These files define what the runtime and orchestrator may rely on.

### 3.3. Python Assembler Runtime

The runtime lives under:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/`

Its current job is to:
- load the correct stage template
- load the correct stage contract
- resolve the relevant shared-state sections
- resolve the routed guidance modules
- render all of those into a single stage prompt

It does not yet:
- call the model
- validate stage output
- merge stage output into shared state
- run the whole workflow

### 3.4. Orchestrator

The orchestrator is the intended future execution layer.

Its job should be to:
- choose the stage to run
- assemble the stage prompt
- send it to a model
- validate the result against the stage output schema
- merge valid output into the shared state file
- manage feedback loops and re-entry

The orchestrator should not duplicate assembly logic that already lives in the
contracts and runtime.

## 4. Workflow Model

The canonical workflow is:
- Routing
- Boundary
- Structure
- Scenarios
- Question Generation
- Evidence Planning
- Decision Logic
- Signal Translation
- Monitoring
- Render

Each stage owns a durable output slice of the shared state, except `Render`,
which is terminal formatting and does not write new analysis state.

## 5. Current Assembly Model

Today, prompt assembly works like this:

1. choose a stage
2. load its stage template
3. load its stage contract
4. resolve required and selected optional state reads
5. resolve the routed guidance modules from the `routing` state
6. render prompt blocks
7. interpolate placeholders in the stage template when present
8. append any unplaced blocks using the legacy order
9. return one final markdown prompt string

The supported prompt blocks are:
- `{{topic}}`
- `{{current_state}}`
- `{{active_steering}}`
- `{{required_output}}`
- `{{feedback}}`

This behavior is implemented in:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/assembler.py`

## 6. Prompt-Facing Concepts

The runtime contains implementation concepts that should not leak into prompt
language more than necessary.

### 6.1. Topic

`topic` is the raw input topic from the user.

Prompt-facing meaning:
- the original, least-normalized statement of the problem

It should remain durable in state because downstream stages may need to compare
the raw ask with the normalized framing.

### 6.2. Routing

`routing` is not just adapter selection.

It contains:
- normalized question framing
- explicit constraints
- desired output framing
- risk tolerance
- decision context
- stage-driving classifications
- classification rationales
- time horizon
- unit of analysis
- assumptions

This means `routing` plays two roles:
- normalized problem frame
- routed stage guidance selector

This is acceptable, but prompt-facing renderers should present the meaning of
the routing block rather than implementation language such as “adapter
selection.”

### 6.3. Relevant Context

The current runtime label `Current State` is implementation-oriented.

The preferred prompt-facing term is:
- `Relevant Context`

Reason:
- it tells the model what prior analysis matters for this stage
- it avoids implying a database or state machine abstraction inside the prompt

### 6.4. Stage Guidance

The current runtime label `Active Steering` is also implementation-oriented.

The preferred prompt-facing term is:
- `Stage Guidance`

Reason:
- it explains the purpose more directly
- it sounds like model-facing instructions rather than internal runtime jargon

## 7. Shared State Design

The live shared state should remain one JSON file.

Reason:
- one durable artifact per run is easier to inspect
- one file keeps orchestration simple
- later stages benefit from one source of truth

The current top-level state sections are:
- `topic`
- `routing`
- `boundary`
- `structure`
- `scenarios`
- `questions`
- `evidence_plan`
- `uncertainty_map`
- `decision_logic`
- `synthesis`
- `signals`
- `monitoring`

This is the right top-level shape and should remain.

## 8. Shared State Contract Direction

### 8.1. Current State

Today there is one top-level contract file:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/shared_state_schema.json`

It describes the full live shared-state object.

### 8.2. Target Design

The shared-state contract should be broken into one schema file per top-level
section while still composing into one top-level shared-state schema.

Recommended structure:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/topic.schema.json`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/routing.schema.json`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/boundary.schema.json`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/structure.schema.json`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/scenarios.schema.json`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/questions.schema.json`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/evidence_plan.schema.json`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/uncertainty_map.schema.json`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/decision_logic.schema.json`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/synthesis.schema.json`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/signals.schema.json`
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/monitoring.schema.json`

Then:
- `shared_state_schema.json` becomes the composed schema for the whole live file

### 8.3. Why This Direction

Benefits:
- each section becomes easier to read and maintain
- stage contracts can reuse the same section schemas
- section renderers can align to section-level contracts
- validation can become more consistent across runtime and orchestrator
- the top-level state file remains intact

### 8.4. Schema Formalism

The recommended schema format is JSON Schema with `$ref`.

Reason:
- it is standard
- it already matches the current contract style
- it supports composition naturally
- it avoids inventing a custom schema system

Important constraint:
- use JSON Schema pragmatically
- do not force maximum strictness everywhere just because the format allows it

The goal is:
- reusable and machine-checkable contracts

not:
- bureaucratic over-modeling

## 9. Section Renderer Direction

### 9.1. Current State

Today, state rendering is generic:
- one heading per section
- one JSON block per section

This is transparent but not very informative.

### 9.2. Target Design

Each top-level shared-state section should have a dedicated self-renderer.

This does not mean each section becomes a separate runtime state file.
It means each section gets a dedicated presentation function.

Recommended structure:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/renderers/`
  - `topic.py`
  - `routing.py`
  - `boundary.py`
  - `structure.py`
  - `scenarios.py`
  - `questions.py`
  - `evidence_plan.py`
  - `uncertainty_map.py`
  - `decision_logic.py`
  - `synthesis.py`
  - `signals.py`
  - `monitoring.py`
  - `registry.py`

The renderer registry should map:
- state section name -> renderer function

Fallback behavior:
- if no specialized renderer exists, fall back to the current JSON rendering

### 9.3. Rendering Principle

Each section renderer should:
- preserve fidelity to the underlying state
- present the most decision-useful or stage-useful information first
- avoid implementation jargon
- avoid final deliverable formatting unless the stage is `Render`

Examples:

`routing` renderer should emphasize:
- normalized question
- constraints
- decision context
- task/domain/output/evidence/uncertainty/decision modes
- rationales
- time horizon
- unit of analysis
- assumptions

It should not emphasize:
- “adapter resolution”
- “selected modules”
- other runtime-specific language

`structure` renderer should emphasize:
- decisive stakeholders
- incentives
- constraints
- causal mechanism
- bottlenecks
- killer variables

`questions` renderer should emphasize:
- top killer questions first
- then compact summaries of the buckets

`decision_logic` renderer should emphasize:
- must know before action
- can learn after action
- evidence threshold
- staging
- triggers

## 10. Output Mode Guidance Design

### 10.1. Current Problem

Injecting the full output-mode document into every non-render stage creates
prompt confusion.

It makes upstream stages see:
- final section lists
- final deliverable structure
- formatting expectations that do not belong in that stage

### 10.2. Preferred Design

For non-render stages:
- output mode should influence emphasis and prioritization
- output mode should not inject full final deliverable structure

For render:
- output mode should define the final deliverable structure fully

This means:
- non-render stages get short modulating guidance
- render gets the full output-mode document

This design is already the preferred direction and should be preserved.

## 11. Stage Template Design Principles

Each stage template should be a valid standalone prompt body.

Each should contain:
- a clear role
- a clear job statement
- purpose
- guardrails
- working rules
- input precedence rules when both raw topic and normalized state are present
- output requirements
- the relevant assembler placeholders

Stage templates should not rely on the reader understanding internal repository
concepts such as:
- adapter resolution
- state machine internals
- contract loading

## 12. Render Stage Design

The `Render` stage is special.

It should:
- use the accumulated state as its sole analysis input
- obey the selected output mode for final deliverable structure
- summarize routing compactly when useful
- avoid redoing earlier analytical work

It should not:
- impose a hardcoded final section order that conflicts with the output mode

The selected output mode should define the final deliverable structure.

## 13. Testing Strategy

The testing strategy should verify both structure and prompt quality.

### 13.1. Runtime Tests

The current runtime tests should continue verifying:
- prompt assembly
- CLI assembly
- example assembly
- state rendering

### 13.2. Stage-Sweep Assembly Tests

The system should assemble every stage using:
- one populated shared-state fixture
- one randomized or stress-case topic

This catches:
- unresolved placeholders
- duplicated sections
- bad ordering
- markdown safety regressions

### 13.3. Prompt Quality Review

Prompt quality should also be evaluated with prompt-review agents or equivalent
review passes for:
- well-formedness
- understandability
- absence of conflicting instructions

This is important because not all prompt failures are structural failures.

### 13.4. Structured Codex-Run Review Gate

For non-render stages, prompt quality should be checked by a structured
Codex-run review step in addition to the local runtime tests.

This review step should:
- assemble every non-render stage prompt from:
  - one populated shared-state fixture
  - one randomized or stress-case topic
- review each assembled prompt using a fixed reviewer prompt
- require structured review output
- fail the quality gate if any hard gate fails
- always report the quality scores, even on failure

This is not a replacement for local unit tests.
It is a second layer that checks prompt quality properties that are difficult to
verify with deterministic assertions alone.

### 13.5. Review Scope

The first version of the structured review gate should apply only to:
- Routing
- Boundary
- Structure
- Scenarios
- Question Generation
- Evidence Planning
- Decision Logic
- Signal Translation
- Monitoring

It should not initially cover:
- Render

Reason:
- render-stage quality involves additional deliverable-shape questions that
  should be reviewed under a separate rubric later

### 13.6. Review Criteria

The structured review gate should use two kinds of criteria.

Hard gates:
- No Confusion
- Stage Discipline
- Input Precedence Clarity
- Output Contract Clarity

Scored dimensions:
- Task Clarity
- Context Quality
- Readability
- Completeness
- Priority Clarity
- Decision-Usefulness
- Context Efficiency
- Guidance Quality

Pass rule:
- every hard gate must be `PASS` for every reviewed non-render stage

Reporting rule:
- all scored dimensions must be reported for every reviewed stage
- scores should be visible even when a prompt fails the hard-gate check

The initial quality gate should not fail on score thresholds.
Scores are diagnostic at first; the hard gates are the actual pass/fail rule.

### 13.7. Review Artifacts

The structured review gate should be built around these checked-in artifacts:
- a reviewer prompt
- a structured review output schema
- a prompt-assembly harness for non-render stages
- a review-result checker
- documentation explaining how to run and interpret the quality gate

Recommended locations:
- reviewer prompt:
  - `/Users/canzheng/Work/sandbox/truth-seek/tests/question_generator/non_render_prompt_review_prompt.md`
- review schema:
  - `/Users/canzheng/Work/sandbox/truth-seek/tests/question_generator/non_render_prompt_review_schema.json`
- assembly harness:
  - `/Users/canzheng/Work/sandbox/truth-seek/tests/question_generator/assemble_non_render_prompts.py`
- review checker:
  - `/Users/canzheng/Work/sandbox/truth-seek/tests/question_generator/check_non_render_prompt_review.py`
- workflow notes:
  - `/Users/canzheng/Work/sandbox/truth-seek/tests/question_generator/non_render_prompt_quality.md`

### 13.8. Relationship To Deterministic Tests

The deterministic tests and the Codex-run review gate serve different purposes.

Deterministic tests should continue to verify:
- placeholder resolution
- stage-by-stage assembly success
- fallback assembly behavior
- block ordering
- absence of duplicate sections where explicitly disallowed
- CLI and example prompt generation behavior

The Codex-run review gate should verify:
- whether the prompt is understandable to a model
- whether instruction precedence is clear
- whether context is informative instead of low-signal
- whether guidance helps rather than confuses

Both layers are required for prompt quality.

## 14. Recommended Near-Term Migration Plan

The next architectural move should be:

1. rename prompt-facing render labels
   - `Current State` -> `Relevant Context`
   - `Active Steering` -> `Stage Guidance`
2. add a section renderer registry with fallback to generic JSON rendering
3. split `shared_state_schema.json` into one schema file per top-level section
4. compose the top-level shared-state schema using `$ref`
5. reuse section schemas in stage contracts where helpful
6. simplify prompt-facing `routing` rendering so it presents meaning, not
   implementation mechanics
7. add the structured Codex-run quality gate for non-render prompts

## 15. Open Questions

These questions do not block the current direction, but they should be kept
visible.

### 15.1. Should `routing` eventually split into two top-level sections?

Possible future split:
- `problem_frame`
- `routing`

This could improve conceptual clarity, but it is not required yet.

Current recommendation:
- keep one `routing` block for now
- improve rendering before changing durable state structure

### 15.2. How strict should schema validation be?

Current recommendation:
- strict on stage-owned shape and required keys
- moderate on deeper content semantics

### 15.3. Should section renderers produce markdown only, or structured
intermediate summaries first?

Current recommendation:
- markdown only for now
- do not add a prompt IR unless there is a concrete need

## 16. Final Recommendation

The right long-term shape is:
- one live shared-state file
- one schema file per top-level state section
- one composed top-level shared-state schema
- one self-renderer per top-level state section
- prompt-facing labels that describe meaning, not runtime jargon
- full output-mode structure only at `Render`
- rich `routing` state retained, but rendered in human-meaningful form

This direction improves:
- readability
- composability
- contract reuse
- prompt quality
- alignment between authored prompts, runtime assembly, and future orchestration

without giving up:
- transparency
- explicit contracts
- one-file durable state
- simple runtime behavior
