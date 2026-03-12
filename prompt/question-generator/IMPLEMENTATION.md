# Question Generator Assembler Implementation

This document explains the current implementation of the question-generator
stage assembler. It focuses on:
- architecture
- prompt assembly flow
- contract and state design
- adapter and output-mode resolution
- implementation choices and tradeoffs
- current limitations

This is the implementation reference for the Python runtime under:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/`

## Purpose

The assembler exists to turn the modular question-generator assets into a
runtime prompt for one workflow stage at a time.

The system does not run the full workflow by itself yet. Its current job is:
- take the current shared state
- take a target stage
- load the matching stage template
- load the matching stage contract
- load the routed adapter and output-mode files that matter for that stage
- render all of that into one final prompt string

In short:

`state + stage + contracts + routed modules -> assembled stage prompt`

The model call, output validation, and state merge are still orchestrator work.

## High-Level Architecture

The implementation has four layers.

### 1. Modular prompt assets

These are the authored prompt documents:
- source-of-truth host prompt:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/question-generator-modular.md`
- stage templates:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/stages/`
- adapters:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/adapters/`
- output modes:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/output-modes/`

These files define the actual prompt content and domain logic.

### 2. Contracts and shared state

These are the machine-readable control files:
- stage contracts:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/`
- shared state schema:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/shared_state_schema.json`
- implementation notes:
  - `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/implementation-notes.md`

Contracts are the assembly authority. They define:
- required upstream stage dependencies
- optional upstream stage dependencies
- adapter-dimension dependencies
- written state entities
- output schema
- feedback schema, when supported

### 3. Python runtime

The runtime lives under:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/`

It resolves files, parses contracts, renders state, resolves adapters, and
assembles the final prompt.

### 4. Tests

Tests live under:
- `/Users/canzheng/Work/sandbox/truth-seek/tests/question_generator/`

The test suite verifies pathing, contract parsing, state resolution, state
rendering, adapter resolution, adapter rendering, prompt assembly, CLI
behavior, and the worked example.

## Runtime Modules

### `pathing.py`

File:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/pathing.py`

Responsibilities:
- resolve repository root
- resolve prompt root
- map canonical stage names to stage template files
- map canonical stage names to contract files
- map adapter dimensions and routed values to module files
- normalize stage names and routed values

Key implementation choices:
- The repo root is computed from the module location rather than the current
  working directory. This makes the runtime less fragile when called from
  different directories.
- Stage names are normalized into canonical identifiers like
  `question_generation` and `signal_translation`.
- Stage template naming and contract naming are intentionally separate because
  two contracts use legacy file names:
  - `09-monitoring-layer.contract.json`
  - `10-renderer.contract.json`

### `models.py`

File:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/models.py`

Responsibilities:
- define the typed dataclasses used by the runtime

Current models:
- `OptionalRead`
- `Feedback`
- `OutputSchema`
- `StageContract`
- `ResolvedModule`

Key implementation choice:
- The runtime uses simple frozen dataclasses instead of a heavier validation
  library. The current target is dependency-light and fully compatible with the
  `truth-seek` Conda environment without extra packages.

### `contracts.py`

File:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/contracts.py`

Responsibilities:
- load stage contracts from disk
- validate required top-level keys
- parse contract JSON into `StageContract`

Key implementation choices:
- Contracts are validated for required top-level keys at load time:
  - `stage`
  - `depends_on`
  - `writes`
  - `output_format`
  - `feedback`
  - `output_schema`
- The parser keeps both typed fields and the raw payload.
- The loader is intentionally minimal right now. It validates structure that the
  assembler depends on directly, not every possible schema detail.

### `state_resolution.py`

File:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/state_resolution.py`

Responsibilities:
- convert stage-level dependencies into actual shared-state sections

The key map is `STAGE_TO_STATE_SECTIONS`.

Examples:
- `question_generation -> questions`
- `evidence_planning -> evidence_plan`, `uncertainty_map`
- `decision_logic -> decision_logic`, `synthesis`
- `signal_translation -> signals`

Key implementation choices:
- The assembler works in terms of stage dependencies, but the shared state is
  organized by owned entities. This module is the bridge between those two
  models.
- Required and optional reads are handled separately.
- Optional reads are included only if the caller explicitly selects them.
- `Render` is treated as a special case and receives the full state.

Why this mapping exists:
- Contracts describe workflow dependencies in stage terms.
- Prompt rendering needs concrete state entities.
- Keeping the translation in one place avoids spreading stage-to-state logic
  across the assembler.

### `state_rendering.py`

File:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/state_rendering.py`

Responsibilities:
- render resolved state sections into readable markdown blocks

Current format:
- one `## Relevant Context` section
- one section renderer per top-level shared-state section when available
- JSON fallback for sections without a specialized renderer

Key implementation choices:
- The renderer is registry-driven through
  `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/renderers/registry.py`.
- Specialized section renderers summarize the most useful fields first while
  keeping headings stable and prompt-friendly.
- Unknown sections still fall back to the legacy JSON block rendering so new
  sections can be added incrementally.

Tradeoff:
- Specialized summaries are easier for the model to scan and reason over.
- JSON fallback preserves transparency and keeps rollout incremental where a
  custom summary is not worth the complexity yet.

### `adapter_resolution.py`

File:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/adapter_resolution.py`

Responsibilities:
- resolve the contract's adapter-dimension dependencies into concrete files
  using the `routing` block

Key implementation choices:
- `depends_on` stores adapter dimensions, not resolved file paths.
- The actual routed values come from `state["routing"]`.
- `Routing` itself resolves no modules, because routing defines the adapter
  selections rather than consuming them.
- `output_mode` is resolved from `output-modes/`, while the other dimensions are
  resolved from `adapters/`.

This separation matters:
- contracts define what a stage depends on in general
- routing defines what this specific run selected

### `adapter_rendering.py`

File:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/adapter_rendering.py`

Responsibilities:
- render active module steering for the current stage

Current format:
- one `## Stage Guidance` section
- one wrapper heading per resolved adapter dimension
- one stage-specific extracted steering block

Key implementation choices:
- Wrapper headings are generated by code, not stored redundantly in each
  adapter.
- Adapter files remain responsible for the substantive stage guidance.
- The renderer extracts the correct stage block from the adapter's
  `## Stage Relevance` section.
- Output-mode files are treated differently:
  - `Render` receives the full output-mode document
  - non-render stages receive a short modulating note that keeps them aligned to
    the eventual deliverable without pulling final-format section outlines into
    upstream analysis stages

Why output mode is special:
- output modes are authored as deliverable definitions rather than stage-style
  relevance adapters
- we still want them available during assembly, especially for `Render` and
  decision-oriented stages

Tradeoff:
- full output-mode injection remains simple and transparent for `Render`
- upstream stages avoid prompt confusion from seeing final-deliverable section
  lists in the middle of analytical work

### `assembler.py`

File:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/assembler.py`

Responsibilities:
- orchestrate the full prompt assembly for one stage

Current assembly flow:
1. load the stage template
2. resolve required and selected optional state sections
3. resolve the routed modules
4. render prompt blocks:
   - topic
   - relevant context
   - stage guidance, if any
   - required output schema
   - feedback schema, if supported
5. interpolate any matching placeholders in the stage template
6. append any unplaced blocks in legacy order
7. return one markdown prompt string

Key implementation choices:
- The assembler is intentionally a renderer, not a workflow executor.
- It does not call the model.
- It does not validate model output.
- It does not merge state updates.
- Placeholder support is intentionally lightweight and uses a small fixed set of
  supported tokens rather than a general templating engine.

Those behaviors are left to a future orchestrator.

Why this split was chosen:
- prompt assembly and workflow execution are different concerns
- prompt debugging is easier when assembly can be run independently
- it keeps the current implementation testable without introducing model or API
  dependencies

Supported placeholders:
- `{{topic}}` -> markdown-safe rendered topic block
- `{{current_state}}` -> rendered `Relevant Context` block
- `{{active_steering}}` -> rendered `Stage Guidance` block
- `{{required_output}}` -> rendered output-schema block with `$ref` entries expanded
- `{{feedback}}` -> rendered feedback-schema block with `$ref` entries expanded when supported

Backward-compatibility rule:
- when a template explicitly places a block placeholder, that block is rendered
  there and not appended again
- when a template omits a block placeholder, the assembler appends that block
  after the template using the legacy order

### `cli.py`

File:
- `/Users/canzheng/Work/sandbox/truth-seek/tools/question_generator/cli.py`

Responsibilities:
- expose prompt assembly from the command line

Parameters:
- `--stage`
- `--state`
- `--include-optional` (repeatable)

Important behavioral note:
- the CLI assembles a prompt
- it does not run the stage

That means:
- input: current shared state JSON
- output: the assembled prompt for the requested stage

It is best understood as a stage prompt generator, not a full workflow runner.

## Data Model

## Shared State

The shared state template lives at:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/shared_state_schema.json`

It is the durable pre-render state for the workflow and now composes one schema
file per top-level section from
`/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/state-sections/`.

Main sections:
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

Key implementation choice:
- `rendered_output` was removed from durable state

Why:
- render is a terminal formatting stage
- render should consume state, not write new analysis state back into it

## Routing Block

The `routing` block serves two jobs:
- formalize the raw user input into a normalized problem frame
- hold the routed values used for adapter resolution

This is why `routing` contains both:
- user/problem framing fields:
  - `question`
  - `explicit_constraints`
  - `desired_output`
  - `risk_tolerance`
  - `decision_context`
  - `time_horizon`
  - `unit_of_analysis`
  - `assumptions`
- routed classifications:
  - `task`
  - `secondary_task`
  - `domain`
  - `secondary_domain`
  - `output_mode`
  - `secondary_output_mode`
  - `evidence_mode`
  - `secondary_evidence_mode`
  - `uncertainty_mode`
  - `secondary_uncertainty_mode`
  - `decision_mode`
  - `secondary_decision_mode`
  - `classification_rationales`

Key implementation choice:
- routed adapter dependencies are not stored separately in state

Why:
- contracts already define which adapter dimensions each stage depends on
- state only needs to store the resolved routed values

## Contract Design

Each stage contract contains:
- `stage`
- `reads_required`
- `reads_optional`
- `depends_on`
- `writes`
- `output_format`
- `feedback`
- `output_schema`

Implementation note:
- non-render stage contracts keep an inline outer `output_schema` object but
  now reuse shared section schemas inside `properties` via `$ref`

### `reads_required`

Required upstream stage dependencies.

Example:
- `Decision Logic` requires `routing`, `scenarios`, and `evidence_planning`

### `reads_optional`

Optional upstream stage dependencies that may be included by the caller.

Each optional read has:
- `stage`
- `kind`
- `when`

Current `kind` values:
- `user_requirement`
- `situation`

Why optional reads exist:
- some stages can work with a minimal upstream set
- some stages become stronger when more context is explicitly included
- feedback loops can make downstream context relevant during stage re-entry

### `depends_on`

Adapter-dimension dependencies for the stage.

Important design decision:
- `depends_on` stores dimensions, not resolved adapter files

Example:
```json
["task", "domain", "output_mode", "evidence_mode", "uncertainty_mode", "decision_mode"]
```

At runtime:
- the contract says what dimensions matter
- the routing block supplies the selected values
- the resolver finds the actual files

### `writes`

Top-level state entities owned by the stage.

### `output_schema`

The required JSON output shape for the stage.

Key implementation choice:
- contracts, not deleted guidance files, are now the source of truth for output
  shape

Why:
- the assembler needs machine-readable output requirements
- validation belongs closer to the contract than to prose documentation

## Prompt Assembly Flow

For a stage like `decision_logic`, the runtime currently does this:

1. load `07-decision-logic.contract.json`
2. load `07-decision-logic.md`
3. resolve required and selected optional state sections
4. resolve routed modules from `routing`
5. render prompt blocks for:
   - topic
   - current state
   - active steering
   - required output
   - feedback, if supported
6. interpolate any matching placeholders in the template
7. append any remaining unplaced blocks in legacy order
8. return one markdown prompt string

This gives a prompt shaped like:
- stage instructions with optional explicit placeholders
- current state, either interpolated or appended
- active steering, either interpolated or appended
- required output, either interpolated or appended
- feedback, if needed and either interpolated or appended

## Why We Chose Markdown Templates Plus Code

We considered a heavier templating or IR approach. The current implementation
uses document templates plus Python rendering logic instead.

Reasons:
- the authored prompt assets already exist as markdown documents
- contracts already provide structured machine-readable metadata
- state is already structured JSON
- a separate prompt IR would add abstraction without solving a concrete current
  problem

So the implementation treats prompt assembly as:
- render structured inputs into a markdown prompt
- optionally interpolate them into authored placeholder locations

not:
- compile a new intermediate language first

## Design Decisions and Tradeoffs

### Contracts are the assembly authority

Decision:
- use contracts, not prose docs, to drive dependency resolution and output
  expectations

Why:
- machine-readable
- testable
- usable by the assembler directly
- easier to keep synchronized with runtime behavior

Tradeoff:
- requires discipline to keep contracts current when stage semantics change

### State is durable and pre-render

Decision:
- keep only durable research state in the shared state schema

Why:
- downstream stages need reusable structured outputs
- render should not write new analysis state

Tradeoff:
- the shared state schema must evolve when stage outputs grow richer

### Optional reads are caller-selected

Decision:
- the assembler does not interpret `reads_optional[].when`

Why:
- those fields are explanatory metadata
- deciding which optional reads to include is orchestration policy

Tradeoff:
- a future orchestrator must make those choices explicitly

### Adapter headings are rendered in code

Decision:
- keep wrapper phrasing in code
- keep substantive steering in adapter documents

Why:
- avoids duplicated framing text across adapter files
- gives consistent prompt wording across dimensions

Tradeoff:
- if we want more stage-specific heading nuance later, the renderer logic will
  need to grow

### State is rendered as JSON blocks

Decision:
- render current state as readable headings plus JSON

Why:
- transparent
- faithful to the actual state shape
- easy to debug during development

Tradeoff:
- less polished than a prose summarizer

## Current Limitations

The current implementation does not yet include:
- a full orchestrator that calls the model
- output validation against the contract after model execution
- state merge logic
- automatic feedback-loop execution
- stage-aware output-mode extraction comparable to adapter stage extraction
- richer prose summarization of state sections

This means the current runtime is best described as:
- a stage prompt assembler

not:
- a complete end-to-end workflow runner

## How To Use It

Environment:
```bash
conda activate truth-seek
```

Assemble a stage prompt:
```bash
python -m tools.question_generator.cli \
  --stage routing \
  --state /Users/canzheng/Work/sandbox/truth-seek/research-state/problems/iran_war.json
```

Include optional stage dependencies:
```bash
python -m tools.question_generator.cli \
  --stage decision_logic \
  --state /Users/canzheng/Work/sandbox/truth-seek/tests/question_generator/fixtures/minimal_state.json \
  --include-optional structure \
  --include-optional question_generation
```

What happens:
- the CLI prints the assembled prompt to stdout

What does not happen yet:
- no model call
- no response parsing
- no contract validation of model output
- no state merge

## Testing

Run the suite in the intended environment:

```bash
conda run -n truth-seek python -m unittest discover -s tests -p 'test_*.py' -v
```

The tests currently cover:
- path resolution
- contract loading
- state resolution
- state rendering
- adapter resolution
- adapter rendering
- assembled prompt shape
- CLI behavior
- example prompt consistency

## Recommended Next Step

The next major piece should be an orchestrator that:
- assembles the prompt for a stage
- calls the model
- validates output against the contract
- merges the returned state update
- manages feedback loops

That layer should sit on top of the current assembler rather than replacing it.
