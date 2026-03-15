# Question Generator Stage Assembler Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a stage prompt assembler that renders a full task-specific prompt from stage templates, current shared state, routed adapter steering, and stage contracts.

**Architecture:** Keep prompt assets as documents under `prompt/question-generator/`, and implement the assembler as Python code under `tools/question_generator/`. The assembler should treat contracts as the assembly authority, render stage-aware state sections and dimension-aware adapter steering into markdown, and return a final prompt string for one stage at a time. Before guidance removal, move the rich output expectations into contract-level output schemas so the assembler can rely on contracts without a hidden dependency on guidance files.

**Tech Stack:** Python 3 standard library (`json`, `pathlib`, `dataclasses`, `argparse`, `unittest`), Conda environment management, Markdown prompt assets, JSON contracts.

---

## Chunk 1: Bootstrap Python Environment Artifacts

### Task 1: Add environment and dependency management files

**Files:**
- Create: `environment.yml`
- Create: `requirements.txt`
- Modify: `prompt/question-generator/README.md`

- [ ] **Step 1: Add the environment manifest**

Create `environment.yml` with:
- env name `truth-seek`
- a pinned Python version
- `pip`
- a `pip:` section that installs `-r requirements.txt`

- [ ] **Step 2: Add the dependency manifest**

Create `requirements.txt`. Since the initial assembler is standard-library-only,
the file can start empty or comment-only, but it must exist so future runtime
dependencies have one canonical place to land.

- [ ] **Step 3: Document environment setup**

Update `prompt/question-generator/README.md` with setup commands:

```bash
conda env create -f environment.yml
conda activate truth-seek
```

and note that the first implementation target is dependency-light and uses the
Python standard library plus `unittest`.

- [ ] **Step 4: Commit**

```bash
git add environment.yml requirements.txt prompt/question-generator/README.md
git commit -m "chore: add python environment and dependency manifests"
```

## Chunk 2: Make Contracts Complete Enough To Drive Assembly

### Task 2: Add explicit output schemas to contracts

**Files:**
- Modify: `prompt/question-generator/contracts/01-routing.contract.json`
- Modify: `prompt/question-generator/contracts/02-boundary.contract.json`
- Modify: `prompt/question-generator/contracts/03-structure.contract.json`
- Modify: `prompt/question-generator/contracts/04-scenarios.contract.json`
- Modify: `prompt/question-generator/contracts/05-question-generation.contract.json`
- Modify: `prompt/question-generator/contracts/06-evidence-planning.contract.json`
- Modify: `prompt/question-generator/contracts/07-decision-logic.contract.json`
- Modify: `prompt/question-generator/contracts/08-signal-translation.contract.json`
- Modify: `prompt/question-generator/contracts/09-monitoring.contract.json`
- Modify: `prompt/question-generator/contracts/10-render.contract.json`
- Modify: `prompt/question-generator/contracts/implementation-notes.md`
- Test: `tests/question_generator/test_contract_loading.py`

- [ ] **Step 1: Write the failing contract-schema tests**

Create `tests/question_generator/test_contract_loading.py` with tests that assert:
- every stage contract has `stage`, `depends_on`, `writes`, `output_format`, and `feedback`
- non-render stage contracts have `reads_required` and `reads_optional`
- stages 1-9 have an `output_schema`
- stages 5 and 6 have a `feedback.schema`

Run:

```bash
python -m unittest tests.question_generator.test_contract_loading -v
```

Expected: FAIL because `output_schema` is missing in current contracts.

- [ ] **Step 2: Add the minimal contract output schemas**

For each contract, add an `output_schema` section that mirrors the durable state fields for that stage. Keep it aligned to:
- `prompt/question-generator/contracts/shared_state_schema.json`
- the stage-owned entity or entities in `writes`

Specific shape requirements:
- `routing` schema should describe `routing`
- `boundary` schema should describe `boundary`
- `structure` schema should describe `structure`
- `scenarios` schema should describe `scenarios`
- `question_generation` schema should describe `questions`
- `evidence_planning` schema should describe both `evidence_plan` and `uncertainty_map`
- `decision_logic` schema should describe both `decision_logic` and `synthesis`
- `signal_translation` schema should describe `signals`
- `monitoring` schema should describe `monitoring`
- `render` schema should describe deliverable expectations instead of state writes

- [ ] **Step 3: Update implementation notes**

Amend `prompt/question-generator/contracts/implementation-notes.md` to record that contracts now carry the detailed output expectations that were formerly guidance-only.

- [ ] **Step 4: Re-run the contract tests**

Run:

```bash
python -m unittest tests.question_generator.test_contract_loading -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add prompt/question-generator/contracts/*.json prompt/question-generator/contracts/implementation-notes.md tests/question_generator/test_contract_loading.py
git commit -m "feat: add contract output schemas for stage assembly"
```

## Chunk 3: Implement Contract And Asset Loaders

### Task 3: Build filesystem and contract loading utilities

**Files:**
- Create: `tools/question_generator/__init__.py`
- Create: `tools/question_generator/pathing.py`
- Create: `tools/question_generator/contracts.py`
- Create: `tools/question_generator/models.py`
- Test: `tests/question_generator/test_pathing.py`
- Test: `tests/question_generator/test_contract_loading.py`

- [ ] **Step 1: Write the failing loader tests**

Create tests that verify:
- stage names resolve to the correct contract file
- stage names resolve to the correct stage template file
- adapter dimensions resolve from routing values to adapter file paths
- contract loading returns parsed JSON with the expected keys

Run:

```bash
python -m unittest tests.question_generator.test_pathing tests.question_generator.test_contract_loading -v
```

Expected: FAIL because the loader modules do not exist yet.

- [ ] **Step 2: Implement path resolution**

Create `tools/question_generator/pathing.py` with constants and helpers for:
- repo root resolution
- contract directory resolution
- stage template resolution
- adapter family directory resolution
- output-mode module resolution

Include a canonical stage-name map:

```python
{
    "routing": "01-routing",
    "boundary": "02-boundary",
    "structure": "03-structure",
    "scenarios": "04-scenarios",
    "question_generation": "05-question-generation",
    "evidence_planning": "06-evidence-planning",
    "decision_logic": "07-decision-logic",
    "signal_translation": "08-signal-translation",
    "monitoring": "09-monitoring",
    "render": "10-render",
}
```

- [ ] **Step 3: Implement contract and model loading**

Create `tools/question_generator/contracts.py` and `tools/question_generator/models.py` to:
- parse contract JSON
- validate required keys
- expose dataclasses for required reads, optional reads, adapter dependencies, feedback, and output schema

- [ ] **Step 4: Re-run loader tests**

Run:

```bash
python -m unittest tests.question_generator.test_pathing tests.question_generator.test_contract_loading -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/question_generator/__init__.py tools/question_generator/pathing.py tools/question_generator/contracts.py tools/question_generator/models.py tests/question_generator/test_pathing.py tests/question_generator/test_contract_loading.py
git commit -m "feat: add stage contract and asset loaders"
```

## Chunk 4: Implement State Resolution And Rendering

### Task 4: Map contract stage dependencies to shared state sections

**Files:**
- Create: `tools/question_generator/state_resolution.py`
- Create: `tools/question_generator/state_rendering.py`
- Test: `tests/question_generator/test_state_resolution.py`
- Test: `tests/question_generator/test_state_rendering.py`

- [ ] **Step 1: Write the failing state tests**

Create tests that assert:
- required stage reads are converted into the correct state sections
- optional stage reads are only included when explicitly requested
- render is treated as special and receives the full accumulated state
- stage-to-state mappings are correct for:
  - `question_generation -> questions`
  - `evidence_planning -> evidence_plan` and `uncertainty_map`
  - `signal_translation -> signals`

Run:

```bash
python -m unittest tests.question_generator.test_state_resolution tests.question_generator.test_state_rendering -v
```

Expected: FAIL because the state resolution modules do not exist yet.

- [ ] **Step 2: Implement state resolution**

Create `tools/question_generator/state_resolution.py` with:
- a stage-to-state-section map for upstream stage outputs
- a resolver that takes:
  - contract
  - current shared state
  - selected optional reads
- and returns the state sections to render for the current stage

Use these mappings:
- `routing -> routing`
- `boundary -> boundary`
- `structure -> structure`
- `scenarios -> scenarios`
- `question_generation -> questions`
- `evidence_planning -> evidence_plan` and `uncertainty_map`
- `decision_logic -> decision_logic` and `synthesis`
- `signal_translation -> signals`
- `monitoring -> monitoring`
- `render -> full state`

- [ ] **Step 3: Implement readable state rendering**

Create `tools/question_generator/state_rendering.py` that turns resolved state sections into markdown blocks with stage-aware headings, for example:
- `### The current boundary for this problem is:`
- `### The current structural view of the system is:`
- `### The current scenario map suggests these paths:`

Do not dump raw top-level JSON blindly. Render readable JSON blocks or compact bullet summaries under clear headings.

- [ ] **Step 4: Re-run state tests**

Run:

```bash
python -m unittest tests.question_generator.test_state_resolution tests.question_generator.test_state_rendering -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/question_generator/state_resolution.py tools/question_generator/state_rendering.py tests/question_generator/test_state_resolution.py tests/question_generator/test_state_rendering.py
git commit -m "feat: add state resolution and rendering for stage assembly"
```

## Chunk 5: Implement Adapter Resolution And Rendering

### Task 5: Resolve routed adapters and render stage-specific steering

**Files:**
- Create: `tools/question_generator/adapter_resolution.py`
- Create: `tools/question_generator/adapter_rendering.py`
- Test: `tests/question_generator/test_adapter_resolution.py`
- Test: `tests/question_generator/test_adapter_rendering.py`

- [ ] **Step 1: Write the failing adapter tests**

Create tests that verify:
- `depends_on` dimensions resolve from `routing`
- missing optional secondary routing fields do not break resolution
- output mode resolves from `output_mode`
- each resolved adapter can be rendered for a target stage
- stage wrappers are dimension-aware, not generic

Run:

```bash
python -m unittest tests.question_generator.test_adapter_resolution tests.question_generator.test_adapter_rendering -v
```

Expected: FAIL because the adapter modules do not exist yet.

- [ ] **Step 2: Implement adapter resolution**

Create `tools/question_generator/adapter_resolution.py` with functions that:
- read `depends_on` from the contract
- read the current routing block
- resolve concrete adapter paths for:
  - `task`
  - `domain`
  - `output_mode`
  - `evidence_mode`
  - `uncertainty_mode`
  - `decision_mode`

Routing should resolve no adapters for the `routing` stage itself.

- [ ] **Step 3: Implement adapter rendering**

Create `tools/question_generator/adapter_rendering.py` that:
- extracts the current stage steering from each adapter file
- wraps it in dimension-aware headings

Examples of wrapper style:
- `Because this is a Decide task, ...`
- `Because this problem sits in Investing / Markets, ...`
- `Because the dominant uncertainty is Hidden-Variable Dominated, ...`
- `Because the deliverable is a Decision Memo, ...`

The wrapper phrasing belongs in code. The adapter files remain the source of the stage-specific substance.

- [ ] **Step 4: Re-run adapter tests**

Run:

```bash
python -m unittest tests.question_generator.test_adapter_resolution tests.question_generator.test_adapter_rendering -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/question_generator/adapter_resolution.py tools/question_generator/adapter_rendering.py tests/question_generator/test_adapter_resolution.py tests/question_generator/test_adapter_rendering.py
git commit -m "feat: add routed adapter resolution and rendering"
```

## Chunk 6: Assemble Final Stage Prompts

### Task 6: Implement the prompt assembler

**Files:**
- Create: `tools/question_generator/assembler.py`
- Test: `tests/question_generator/test_assembler.py`
- Test: `tests/question_generator/test_examples.py`

- [ ] **Step 1: Write the failing assembler tests**

Create tests that assert assembled prompts:
- include the stage template body
- include rendered required state sections
- include selected optional sections only when requested
- include rendered adapter steering from `depends_on`
- include the contract output schema
- treat `render` as a special final stage

Add one golden-style example test for `07-decision-logic` using a small fixture state.

Run:

```bash
python -m unittest tests.question_generator.test_assembler tests.question_generator.test_examples -v
```

Expected: FAIL because the assembler does not exist yet.

- [ ] **Step 2: Implement the assembler**

Create `tools/question_generator/assembler.py` with one public function:

```python
def assemble_stage_prompt(
    stage: str,
    state: dict,
    optional_reads: list[str] | None = None,
) -> str:
    ...
```

The function should:
1. load the stage contract
2. load the stage template
3. resolve required and selected optional state sections
4. resolve concrete adapters from routing and `depends_on`
5. render state blocks
6. render adapter blocks
7. render the output contract section
8. compose a final markdown prompt in a stable order

Stable order:
1. stage template
2. current state
3. active steering
4. required output
5. feedback contract if supported

- [ ] **Step 3: Re-run assembler tests**

Run:

```bash
python -m unittest tests.question_generator.test_assembler tests.question_generator.test_examples -v
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add tools/question_generator/assembler.py tests/question_generator/test_assembler.py tests/question_generator/test_examples.py
git commit -m "feat: assemble stage prompts from templates state and adapters"
```

## Chunk 7: Add A CLI And End-To-End Verification

### Task 7: Build a small command-line entry point

**Files:**
- Create: `tools/question_generator/cli.py`
- Create: `tests/question_generator/fixtures/minimal_state.json`
- Create: `tests/question_generator/test_cli.py`
- Modify: `prompt/question-generator/README.md`

- [ ] **Step 1: Write the failing CLI test**

Create a test that runs the CLI for one stage with fixture state and checks that stdout contains:
- the stage heading content
- a state section
- an adapter steering section
- the output contract section

Run:

```bash
python -m unittest tests.question_generator.test_cli -v
```

Expected: FAIL because the CLI does not exist yet.

- [ ] **Step 2: Implement the CLI**

Create `tools/question_generator/cli.py` with a command like:

```bash
python -m tools.question_generator.cli \
  --stage decision_logic \
  --state tests/question_generator/fixtures/minimal_state.json \
  --include-optional structure \
  --include-optional question_generation
```

CLI behavior:
- load state JSON
- call `assemble_stage_prompt`
- print markdown prompt to stdout
- exit non-zero on unknown stage, missing contract, or invalid JSON

- [ ] **Step 3: Document usage**

Update `prompt/question-generator/README.md` with:
- assembler code location
- CLI invocation examples
- note that guidance is temporary until contract output schemas fully replace it

- [ ] **Step 4: Run full verification**

Run:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/question_generator/cli.py tests/question_generator/fixtures/minimal_state.json tests/question_generator/test_cli.py prompt/question-generator/README.md
git commit -m "feat: add stage prompt assembler cli"
```

## Chunk 8: Remove Guidance From The Assembly Path

### Task 8: Delete guidance files once contracts fully replace them

**Files:**
- Modify: `guidelines/question-generator-workflow.md`
- Modify: `prompt/question-generator/question-generator-modular.md`
- Modify: `prompt/question-generator/README.md`
- Modify: `AGENTS.md`
- Delete: `prompt/question-generator/stages/01-routing-guidance.md`
- Delete: `prompt/question-generator/stages/02-boundary-guidance.md`
- Delete: `prompt/question-generator/stages/03-structure-guidance.md`
- Delete: `prompt/question-generator/stages/04-scenarios-guidance.md`
- Delete: `prompt/question-generator/stages/05-question-generation-guidance.md`
- Delete: `prompt/question-generator/stages/06-evidence-planning-guidance.md`
- Delete: `prompt/question-generator/stages/07-decision-logic-guidance.md`
- Delete: `prompt/question-generator/stages/08-signal-translation-guidance.md`
- Delete: `prompt/question-generator/stages/09-monitoring-guidance.md`
- Delete: `prompt/question-generator/stages/10-render-guidance.md`
- Test: `tests/question_generator/test_examples.py`

- [ ] **Step 1: Write the failing documentation/reference checks**

Add or extend tests so they fail if:
- docs still reference guidance as assembly input
- examples still assume guidance-only output detail

Run:

```bash
python -m unittest tests.question_generator.test_examples -v
```

Expected: FAIL until docs and examples are updated.

- [ ] **Step 2: Remove guidance references from docs**

Update docs to make the assembly story explicit:
- stage templates + contracts + state + adapters
- no guidance dependency in runtime assembly

- [ ] **Step 3: Delete the guidance files**

Delete the `*-guidance.md` files under `prompt/question-generator/stages/`.

- [ ] **Step 4: Re-run verification**

Run:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add guidelines/question-generator-workflow.md prompt/question-generator/question-generator-modular.md prompt/question-generator/README.md AGENTS.md tests/question_generator/test_examples.py
git rm prompt/question-generator/stages/*-guidance.md
git commit -m "chore: remove stage guidance after contract consolidation"
```

## Notes For Execution

- Treat `render` as a special terminal stage throughout implementation.
- Assume work runs inside the Conda environment `truth-seek`.
- Do not make the assembler interpret the prose in `reads_optional[].when`; the caller should decide which optional reads to include.
- Keep the assembly order stable so prompt diffs are easy to review.
- Keep the implementation dependency-free unless a clear need emerges.
- Prefer readable markdown rendering over raw JSON dumps.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-03-12-question-generator-stage-assembler.md`. Ready to execute?
