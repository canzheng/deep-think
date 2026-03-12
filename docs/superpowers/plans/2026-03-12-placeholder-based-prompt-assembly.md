# Placeholder-Based Prompt Assembly Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add placeholder-aware prompt assembly so stage templates can control where topic, current state, steering, required output, and feedback appear in the final assembled prompt.

**Architecture:** Extend the current append-only assembler with a small placeholder rendering layer in `tools/question_generator/assembler.py`. Support explicit placeholders in markdown templates, preserve backward compatibility by appending blocks that are not explicitly placed, and update docs, tests, and examples to reflect the new assembly model.

**Tech Stack:** Python 3 standard library (`json`, `re`, `argparse`, `pathlib`, `unittest`), markdown prompt assets, JSON contracts, existing question-generator runtime.

---

## Chunk 1: Define Placeholder Semantics And Lock In Test Coverage

### Task 1: Specify the placeholder contract in tests before changing assembly behavior

**Files:**
- Modify: `tests/question_generator/test_assembler.py`
- Test: `tests/question_generator/test_cli.py`

- [ ] **Step 1: Add a focused placeholder assembly test**

Extend `tests/question_generator/test_assembler.py` with a test that uses a temporary template string containing:

```md
Intro

{{topic}}

{{current_state}}

{{active_steering}}

{{required_output}}

{{feedback}}
```

and asserts that:
- `{{topic}}` is replaced with the raw topic string
- `{{current_state}}` is replaced with the rendered current state block
- `{{active_steering}}` is replaced with the rendered steering block when modules exist
- `{{required_output}}` is replaced with the rendered output schema block
- `{{feedback}}` is replaced with the rendered feedback block when supported
- no raw placeholder strings remain in the final prompt

- [ ] **Step 2: Add a backward-compatibility test**

Add a second test that uses a template with no placeholders and asserts the current append order still works:
- template first
- current state next
- steering next when present
- required output next
- feedback last when present

- [ ] **Step 3: Update existing brittle assertions**

Replace assertions that require the old stage-header wording, such as:

```python
self.assertIn("## Stage 5 - Question Generation", prompt)
```

with assertions tied to durable prompt structure:
- the current template opening line
- `## Current State`
- `## Active Steering`
- `## Required Output`
- `## Feedback`

This avoids breaking tests just because prompt wording changes.

- [ ] **Step 4: Add or update CLI coverage**

Adjust `tests/question_generator/test_cli.py` so the CLI-level test verifies the assembled prompt still includes the rendered blocks for a placeholder-free template and still prints the full assembled prompt to stdout.

- [ ] **Step 5: Run tests to verify failure before implementation**

Run:

```bash
python -m unittest tests.question_generator.test_assembler tests.question_generator.test_cli -v
```

Expected: FAIL because placeholder interpolation does not exist yet.

- [ ] **Step 6: Commit**

```bash
git add tests/question_generator/test_assembler.py tests/question_generator/test_cli.py
git commit -m "test: define placeholder-based prompt assembly behavior"
```

## Chunk 2: Implement Placeholder Rendering In The Assembler

### Task 2: Add placeholder-aware assembly with append-only fallback

**Files:**
- Modify: `tools/question_generator/assembler.py`
- Test: `tests/question_generator/test_assembler.py`

- [ ] **Step 1: Add a placeholder map in the assembler**

In `tools/question_generator/assembler.py`, build a dictionary like:

```python
placeholder_values = {
    "topic": state.get("topic", ""),
    "current_state": state_block,
    "active_steering": steering_block,
    "required_output": output_block,
    "feedback": feedback_block,
}
```

Keep names stable and lower-case:
- `{{topic}}`
- `{{current_state}}`
- `{{active_steering}}`
- `{{required_output}}`
- `{{feedback}}`

- [ ] **Step 2: Implement minimal placeholder substitution**

Add a helper such as:

```python
def _render_template_placeholders(template: str, values: dict[str, str]) -> tuple[str, set[str]]:
    ...
```

Requirements:
- replace exact placeholder tokens like `{{topic}}`
- treat missing or empty values as empty string
- return both the rendered template and the set of placeholders actually used
- do not introduce a heavy templating engine

Use a strict pattern so the implementation is predictable:

```python
r"\{\{\s*([a-z_]+)\s*\}\}"
```

- [ ] **Step 3: Preserve backward compatibility**

After rendering placeholders:
- if a block placeholder was already used in the template, do not append that block again
- if a block placeholder was not used, append that block in the legacy order

Expected behavior:
- new templates can control prompt layout
- old templates continue working without edits

- [ ] **Step 4: Define treatment for empty optional blocks**

For `active_steering` and `feedback`:
- if the rendered block is empty, substitute an empty string
- do not append an empty block later

This keeps prompts clean for stages that have no steering or no feedback schema.

- [ ] **Step 5: Keep `topic` simple**

Do not treat `topic` as a rendered markdown section. `{{topic}}` should inject the raw topic string only.

This keeps template phrasing natural and avoids forcing the template to embed a JSON block just to reference the input topic.

- [ ] **Step 6: Re-run assembler tests**

Run:

```bash
python -m unittest tests.question_generator.test_assembler -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add tools/question_generator/assembler.py tests/question_generator/test_assembler.py
git commit -m "feat: add placeholder-aware stage prompt assembly"
```

## Chunk 3: Make Placeholder Placement A First-Class Authoring Pattern

### Task 3: Update templates to explicitly place assembled blocks where needed

**Files:**
- Modify: `prompt/question-generator/stages/01-routing.md`
- Modify: `prompt/question-generator/stages/02-boundary.md`
- Modify: `prompt/question-generator/stages/03-structure.md`
- Modify: `prompt/question-generator/stages/04-scenarios.md`
- Modify: `prompt/question-generator/stages/05-question-generation.md`
- Modify: `prompt/question-generator/stages/06-evidence-planning.md`
- Modify: `prompt/question-generator/stages/07-decision-logic.md`
- Modify: `prompt/question-generator/stages/08-signal-translation.md`
- Modify: `prompt/question-generator/stages/09-monitoring.md`
- Optionally modify: `prompt/question-generator/stages/10-render.md`

- [ ] **Step 1: Decide the default block order for new-style templates**

Use this default layout unless a specific stage benefits from a different order:

```md
[stage instructions]

Input:
- Topic: `{{topic}}`

{{current_state}}

{{active_steering}}

{{required_output}}

{{feedback}}
```

Notes:
- `{{feedback}}` can be omitted from stages that never support feedback
- `Render` may choose a different structure because it consumes full state

- [ ] **Step 2: Update routing to use explicit placement**

Review `prompt/question-generator/stages/01-routing.md` and keep `{{topic}}`, then add:
- `{{current_state}}` if you want the raw topic block visible as rendered state too
- or omit it deliberately if routing should rely on the direct input line only

Make a conscious choice here. Do not accidentally include the topic twice unless the duplication is clearly beneficial.

- [ ] **Step 3: Update stages 02-09 to use block placeholders**

For each of the non-render stage templates:
- place `{{current_state}}` where the model should read accumulated state
- place `{{active_steering}}` where stage-specific steering belongs
- place `{{required_output}}` near the end, after instructions
- place `{{feedback}}` only where feedback is supported by the contract

- [ ] **Step 4: Decide whether render should opt in**

For `prompt/question-generator/stages/10-render.md`, choose one of:
- leave it legacy-style for now and rely on append fallback
- or explicitly place `{{current_state}}`, `{{active_steering}}`, and `{{required_output}}`

Recommendation:
- update `Render` in the same pass so every template follows one authoring model

- [ ] **Step 5: Add a short authoring note if needed**

If the templates start using placeholders broadly, add one short note near the top of each file or in docs that these placeholders are assembler-provided blocks, not model-generated content.

- [ ] **Step 6: Re-run assembler and CLI tests**

Run:

```bash
python -m unittest tests.question_generator.test_assembler tests.question_generator.test_cli -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add prompt/question-generator/stages/*.md tests/question_generator/test_assembler.py tests/question_generator/test_cli.py
git commit -m "refactor: place assembled prompt blocks with template placeholders"
```

## Chunk 4: Update Supporting Docs And Examples To Match Reality

### Task 4: Bring implementation docs and examples in line with placeholder-based assembly

**Files:**
- Modify: `prompt/question-generator/IMPLEMENTATION.md`
- Modify: `prompt/question-generator/README.md`
- Modify: `prompt/question-generator/examples/07-decision-logic.assembled.example.md`
- Optionally modify: other files under `prompt/question-generator/examples/` if present

- [ ] **Step 1: Update the implementation narrative**

Revise `prompt/question-generator/IMPLEMENTATION.md` to describe:
- templates may contain assembler placeholders
- the assembler renders current state, steering, output schema, and feedback into named blocks
- the assembler interpolates those blocks into the template when placeholders are present
- otherwise it appends blocks in legacy order

Be explicit that the current implementation now supports both:
- placeholder-driven structure
- append-only backward compatibility

- [ ] **Step 2: Update the stated assembly order**

Replace the hardcoded “template then append everything” description with:

1. load template
2. resolve state reads
3. resolve routed modules
4. render prompt blocks
5. interpolate placeholders found in the template
6. append any non-placed blocks in legacy order
7. return one markdown prompt string

- [ ] **Step 3: Update README authoring guidance**

Add a short section in `prompt/question-generator/README.md` explaining the supported placeholders:
- `{{topic}}`
- `{{current_state}}`
- `{{active_steering}}`
- `{{required_output}}`
- `{{feedback}}`

Also document the fallback rule:
- if a placeholder is absent, the assembler appends that block after the template

- [ ] **Step 4: Refresh at least one assembled example**

Regenerate or manually update `prompt/question-generator/examples/07-decision-logic.assembled.example.md` so it reflects the new prompt layout and terminology.

If examples are intended as golden references, update any others that are now misleading.

- [ ] **Step 5: Commit**

```bash
git add prompt/question-generator/IMPLEMENTATION.md prompt/question-generator/README.md prompt/question-generator/examples/*.md
git commit -m "docs: describe placeholder-based prompt assembly"
```

## Chunk 5: Verify End-To-End Prompt Shape And Guard Against Regression

### Task 5: Run the relevant test suite and inspect one real assembled prompt

**Files:**
- Verify: `tools/question_generator/assembler.py`
- Verify: `tests/question_generator/test_assembler.py`
- Verify: `tests/question_generator/test_cli.py`
- Verify: `tests/question_generator/test_examples.py`
- Verify: `tests/question_generator/test_state_rendering.py`

- [ ] **Step 1: Run focused unit tests**

Run:

```bash
python -m unittest \
  tests.question_generator.test_assembler \
  tests.question_generator.test_cli \
  tests.question_generator.test_examples \
  tests.question_generator.test_state_rendering -v
```

Expected: PASS.

- [ ] **Step 2: Assemble a real prompt through the CLI**

Run:

```bash
python -m tools.question_generator.cli \
  --stage decision_logic \
  --state tests/question_generator/fixtures/minimal_state.json \
  --include-optional structure \
  --include-optional question_generation
```

Inspect the output manually and confirm:
- placeholder tokens do not appear literally
- the topic is injected where the template expects it
- current state appears exactly once where intended
- steering appears exactly once where intended
- required output appears exactly once
- feedback appears only for stages whose contract supports it

- [ ] **Step 3: Check one legacy-style template path**

Temporarily assemble a stage template that still lacks placeholders, or simulate one in a test fixture, and confirm the old append behavior still works.

This is the key regression guard for mixed migration states.

- [ ] **Step 4: Commit**

```bash
git add tools/question_generator/assembler.py prompt/question-generator/stages/*.md prompt/question-generator/IMPLEMENTATION.md prompt/question-generator/README.md tests/question_generator/*.py prompt/question-generator/examples/*.md
git commit -m "test: verify placeholder prompt assembly end to end"
```

## Implementation Notes

- Keep the placeholder system deliberately small. This does not need a full templating engine.
- Prefer explicit block names over magical behavior.
- Do not change contracts or shared state shape as part of this work.
- Do not rename `topic`; placeholder support is an assembly concern, not a schema migration.
- Avoid introducing duplicate prompt blocks when both placeholders and append fallback are active.
- If a template accidentally uses an unknown placeholder, fail loudly in tests and decide whether runtime should raise or leave the token untouched. Recommendation: leave unknown placeholders untouched for now, but add a test so this behavior is explicit.

## Suggested Execution Order

1. Lock behavior in tests.
2. Add placeholder substitution to the assembler with backward compatibility.
3. Migrate templates to explicit placement.
4. Update docs and examples.
5. Verify with unit tests and one CLI-assembled prompt.

Plan complete and saved to `docs/superpowers/plans/2026-03-12-placeholder-based-prompt-assembly.md`. Ready to execute?
