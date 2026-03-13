# Question Generator Architecture Design

**Status:** Draft working design

**Scope:** This document describes the architecture of the modular
question-generator system as a whole. It covers the authored prompt assets, the
shared-state contract, the stage contracts, the prompt assembler runtime, the
intended orchestrator boundary, and the next design direction for schema
composition and model-facing prompt assembly.

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
- build the render context for the stage
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

### 3.5. Separate Model Session Boundary

The orchestrator and the stage-answering model should be treated as separate
actors even when both are powered by Codex.

Recommended implementation:
- one Codex-backed orchestration session owns workflow control
- one fresh ephemeral Codex answering session is created for each stage run
- the orchestrator launches that answering session automatically
- the answering session is discarded after the stage reply is captured
- the only interface between them is the assembled stage prompt, the returned
  stage response, and the contract-governed shared-state merge

Reason:
- it preserves the stage boundary that the architecture is designed around
- it prevents orchestration context from silently leaking into stage answers
- it makes prompt and output debugging more honest
- it avoids carrying hidden stage-to-stage model memory
- it allows the model backend to change later without rewriting assembly logic

Execution policy for the answering session:
- always use `GPT-5.4`
- always use `high` reasoning effort
- always run the answering session as ephemeral/disposable

This should be treated as orchestration policy, not left to per-run operator
choice.

This means the orchestrator should be model-provider-agnostic at the boundary.
It may call Codex directly, but the architectural contract should not depend on
one in-process model session holding both roles at once.

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
4. build one stage render context from:
   - shared state
   - stage contract metadata
   - routed guidance
5. render the template through Mustache
6. return one final markdown prompt string

The target model-facing template system is Mustache.

Why Mustache:
- it supports variable substitution and list sections
- it is logic-light and much safer than a full template language
- it handles repeated object structures like scenarios, questions, signals, and
  monitoring items cleanly
- it avoids a growing pile of custom placeholder behavior

Important constraints:
- prompt templates should not depend on custom filters or helper functions
- formatting should live primarily in the templates, not in Python-generated
  markdown fragments
- Python should prepare data and metadata, not control indentation-sensitive
  prompt layout

This behavior is implemented in:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/assembler.py`

## 6. Prompt-Facing Concepts And Render Context

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

### 6.3. Mustache Render Context

Non-render templates should be authored as Mustache templates over one prepared
render context.

That render context should contain:
- the shared state object at the top level
- `required_output_schema` from the stage contract, with `$ref` expanded
- `feedback_schema` from the stage contract when supported, with `$ref`
  expanded
- `active_steering` as the currently rendered routed guidance block

This means templates can directly reference values like:
- `{{topic}}`
- `{{routing.time_horizon}}`
- `{{routing.decision_context}}`
- `{{boundary.core_system}}`
- `{{scenarios.base_case.summary}}`
- `{{required_output_schema}}`

Important rule for stages after `Routing`:
- do not inject adapter-selection routing fields such as `routing.task`,
  `routing.domain`, `routing.output_mode`, `routing.evidence_mode`,
  `routing.uncertainty_mode`, or `routing.decision_mode` directly into the
  prompt
- the effect of those routed classifications should come from the stage's
  adapter guidance instead

And they can repeat list-like structures with Mustache sections, for example:
- `alternative_scenarios`
- `top_killer_questions`
- `question_to_evidence_mapping`
- `signals`
- `what_to_watch`

### 6.4. Conditional Input Convention

Some upstream inputs are not always required, but are still useful enough that
we want them available to the model when judgment is needed.

For those cases, the preferred prompt convention is:
- always include required inputs plainly
- include optional context as explicit conditional blocks in the template
- let the model decide whether the conditional block materially applies

Non-render templates should begin with a general rule like:

```md
For any input marked `[CONDITIONAL]`, use it only if you strongly believe the
stated condition is met for the current task.
If the condition is not clearly met, ignore that input entirely.
Do not force conditional inputs into the analysis just because they are
provided.
```

Each conditional block should then be wrapped explicitly:

```md
[CONDITIONAL condition="Use this only if action depends on mechanism details rather than scenario summaries."]
...
[/CONDITIONAL]
```

Design rules:
- the condition must be written in plain language
- the condition must say when to use the block, not just what the block contains
- related optional fields should be grouped into one readable conditional block
- conditionals should be visible in the prompt, not silently decided by orchestration

Reason:
- many conditional reads are judgment calls rather than deterministic routing rules
- the workflow already relies on the model for reasoning
- keeping the decision visible in the prompt is easier to audit than burying it
  in orchestration code

### 6.5. One Temporary Exception: `active_steering`

The first Mustache migration may still keep:
- `active_steering`

as one pre-rendered natural-language block.

Reason:
- the current adapter assets are authored as markdown prose, not structured
  data

This exception is acceptable in the short term, but it is not the cleanest end
state.

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

### 7.1. Run Artifacts Must Be Separate From Shared State

The system should also persist run artifacts for debugging and auditability, but
those artifacts must not be folded into the live shared state.

Required distinction:
- shared state is the durable analysis object used by downstream stages
- run artifacts are execution traces that explain how the state was produced

The run artifacts should include at least:
- the assembled prompt for each stage
- the raw reply returned by the stage-answering agent
- the parsed structured payload used for validation and merge
- lightweight stage metadata such as stage name, run identifier, and file paths

Reason:
- the shared state should stay small, durable, and analysis-oriented
- prompts and raw model replies are essential for debugging but are not part of
  the analysis contract
- render should still treat the shared state file as its sole analysis input

Recommended storage shape:
- one run directory per workflow execution
- one live `shared_state.json` file inside that run directory
- one manifest file describing the run
- one subdirectory per stage containing prompt and response artifacts

Recommended stage artifact set:
- `prompt.md`
- `response.raw.md`
- `response.parsed.json`
- `response.schema.json`
- `codex.stdout.jsonl`
- `codex.stderr.txt`
- `stage.json`

These files are execution artifacts, not additional shared-state sections.

## 8. Shared State Contract

### 8.1. Current State

The live shared-state contract now uses one top-level composed schema:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/shared_state_schema.json`

It composes one schema file per top-level section:
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

`shared_state_schema.json` remains the one-file contract for the live state
object while using `$ref` composition internally.

### 8.2. Why This Shape

Benefits:
- each section becomes easier to read and maintain
- stage contracts can reuse the same section schemas
- section renderers can align to section-level contracts
- validation can become more consistent across runtime and orchestrator
- the top-level state file remains intact

### 8.3. Schema Formalism

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

## 9. State Schemas And Template Inputs

### 9.1. Current State

The shared-state contract remains important, but non-render prompt assembly
should no longer depend on whole-section markdown renderers.

The primary role of the shared-state schemas is now:
- durable workflow state validation
- stage-output schema reuse
- stable field paths for Mustache templates

Render remains the one stage that may still use a broader render-time context
view until its own field-level template design is settled.

### 9.2. Compact Field-Level Dependency Map

The compact dependency map in
`/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/IMPLEMENTATION.md`
should be treated as the target source of truth for non-render prompt inputs.

Meaning:
- non-render templates should reference only the fields they materially need
- the assembler should stop injecting whole required sections for non-render
  stages
- prompt noise should be reduced by moving from section-level inclusion to
  field-level inclusion
- conditionally useful fields should be surfaced through explicit
  `[CONDITIONAL] ... [/CONDITIONAL]` blocks rather than hidden orchestration
  heuristics

### 9.3. Why Field-Level Templates

Field-level templating is preferred because:
- it makes prompt dependencies visible in the template itself
- it keeps non-render prompts smaller and less noisy
- it makes prompt reviews easier because the visible context is intentional
- it removes the need for section self-renderers to decide what a model should
  see

This is the preferred non-render direction even though the shared-state file
itself remains one durable JSON object.

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
- the relevant Mustache variables and sections

Non-render templates should:
- inline only the compact state fields they need
- use readable grouped subsections rather than raw section dumps
- use Mustache sections for repeated structures when needed
- remain easy to read as prompts, not just as templates

Non-render templates should not:
- depend on giant appended context blocks
- require Python to emit preformatted markdown blobs with indentation-sensitive
  layout
- rely on growing custom placeholder semantics

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
- stage-template rendering against prepared shared state

### 13.2. Stage-Sweep Assembly Tests

The system should assemble every stage using:
- one populated shared-state fixture
- one randomized or stress-case topic

This catches:
- unresolved placeholders
- broken Mustache sections
- bad ordering
- markdown safety regressions

For the Mustache migration, one render test per real template should be the
primary deterministic safety net.

These tests should confirm at least:
- the template renders successfully with a prepared shared state
- no unresolved Mustache tags remain
- repeated list/object structures render as intended
- required output schema appears
- whole-section legacy context blocks do not reappear in non-render prompts

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
- Instruction Coherence
- Input Precedence Clarity
- Output Requirement Clarity
- Sufficient Starting Context

Scored dimensions:
- Task Clarity
- Context Usefulness
- Guidance And Constraint Clarity
- Readability
- Output Readiness
- Confidence To Execute
- Context Efficiency
- Risk Of Misinterpretation

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

## 14. Current Migration Status

The following architectural steps are now implemented:

1. prompt-facing render labels were renamed:
   - `Current State` -> `Relevant Context`
   - `Active Steering` -> `Stage Guidance`
2. a section renderer registry was added with JSON fallback behavior
3. `shared_state_schema.json` was split into one schema file per top-level section
4. the top-level shared-state schema now composes those section schemas using `$ref`
5. stage contracts now reuse section schemas where practical
6. prompt-facing `routing` rendering now presents problem meaning instead of
   adapter-selection mechanics
7. the non-render prompt quality review assets remain available as an
   additional prompt-quality gate

The following architectural steps are now the preferred next direction:

1. move non-render stage templates to Mustache
2. replace whole-section non-render context injection with compact field-level
   template inputs
3. keep `active_steering` as a temporary special-case rendered block during the
   first Mustache migration
4. keep `required_output_schema` and `feedback_schema` as contract-derived
   render-context values
5. keep render as a temporary exception that may still consume broader context
   until its own template input model is finalized

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
- do not center future non-render prompt assembly on section renderers
- use Mustache over structured state and contract data instead
- do not add a prompt IR unless there is a concrete need

### 15.4. Should adapters migrate to structured data?

Current recommendation:
- not in the first Mustache migration
- reconsider after field-level Mustache templates are working

Reason:
- adapters are currently authored as prompt prose and are still ergonomic in
  markdown
- the strongest structural pressure is around `active_steering`, not around the
  whole adapter body
- migrating adapters now would broaden the change surface too much

Likely future direction:
- if we want Mustache to be the only template mechanism with no special
  `active_steering` exception, migrate adapter stage-relevance data, and
  potentially the whole adapter asset, to structured YAML/JSON later
### 15.5. Should the orchestrator call Codex directly or support external
stage sessions first?

Current recommendation:
- call Codex directly from the orchestrator
- create one ephemeral answering session per stage invocation
- make prompt, schema, stdout/stderr, and response artifact persistence
  mandatory
- keep the model-call boundary explicit even though the orchestrator launches
  the answering session automatically

Reason:
- it preserves the separate-session architecture without manual operator steps
- it is still debuggable because the full request and reply path is persisted
- it keeps the answering session disposable after each stage

## 16. Final Recommendation

The right long-term shape is:
- one live shared-state file
- one separate run-artifact layer for prompts and model replies
- one schema file per top-level state section
- one composed top-level shared-state schema
- Mustache-based non-render stage templates over structured shared state and
  contract-derived metadata
- one temporary `active_steering` exception while adapters remain markdown
  assets
- full output-mode structure only at `Render`
- rich `routing` state retained, but consumed through explicit field-level
  template references
- a clean orchestrator-to-model boundary powered by one ephemeral Codex session
  per stage
- a fixed answering-session execution policy of `GPT-5.4` with `high`
  reasoning

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
