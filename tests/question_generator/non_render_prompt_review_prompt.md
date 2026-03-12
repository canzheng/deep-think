You are reviewing a prompt that will be given to an analysis model.

Imagine you are the model who must do the work.

The prompt you are reviewing may contain:
- an original topic the user wants analyzed
- prior analysis outputs that should be treated as context, guidance, or constraints
- instructions for what analysis to perform now
- a required output shape

Your job is to judge whether you could perform the requested analysis correctly
and confidently from the prompt alone.

Do not evaluate whether the analysis itself is true or correct.
Do not evaluate the internal workflow of the system that produced the prompt.
Evaluate only whether this prompt is a strong working prompt for the analyst who
will receive it.

## Review Perspective

Review the prompt as if you are about to begin the task yourself.

Ask:
- Do I understand what I am being asked to do now?
- Do I understand what prior context I should rely on?
- If the original topic and prior analysis differ, do I know which one should dominate?
- Do I understand the rules, constraints, and expectations?
- Do I understand exactly what kind of output I am supposed to produce?
- Could I start the work confidently without making avoidable guesses?

## Hard Gates

Apply these hard gates first.

1. Instruction Coherence
Pass only if the prompt has no conflicting instructions, no confusing overlaps,
and no internal contradictions that would make the analyst unsure how to
proceed.

2. Input Precedence Clarity
Pass only if the prompt makes clear how to treat:
- the original topic
- prior analysis or prior outputs
- current instructions
- guidance or constraints

especially when they point in slightly different directions.

3. Output Requirement Clarity
Pass only if the prompt makes it unambiguous what output the analyst is
expected to produce, in what shape, and under what constraints.

4. Sufficient Starting Context
Pass only if the prompt gives enough context for the analyst to begin the task
without making major avoidable guesses about what the task means.

If any hard gate fails, the prompt should be marked as needing revision.

## Scored Dimensions

Score each dimension from 1 to 5.

Scoring anchors:
- 5 = excellent, very easy to act on
- 4 = strong, only minor weaknesses
- 3 = workable, but noticeably weak or incomplete in places
- 2 = difficult to use well
- 1 = seriously problematic

1. Task Clarity
Do you clearly understand what you are supposed to do now?

2. Context Usefulness
Does the provided context help you do the task, or does it mostly feel like raw
information with limited guidance value?

3. Guidance And Constraint Clarity
Do you understand the guidance, assumptions, and constraints you are expected
to follow?

4. Readability
Is the prompt easy to read, follow, and mentally parse?

5. Output Readiness
Do you understand exactly what kind of answer you are supposed to produce?

6. Confidence To Execute
If you were given this prompt as the analyst, how confidently could you begin
without guessing?

7. Context Efficiency
Does the prompt provide enough useful information without wasting attention on
unnecessary or low-signal material?

8. Risk Of Misinterpretation
How likely is it that a reasonable analyst would misunderstand the task or
produce the wrong kind of answer?
Score this dimension as:
- 5 = very low risk of misinterpretation
- 4 = low risk
- 3 = moderate risk
- 2 = high risk
- 1 = very high risk

## Review Instructions

- Be concrete and practical.
- Review from the point of view of someone who must actually do the work.
- Point out where you would hesitate, guess, or potentially misread the instructions.
- Prefer prompt-level problems over stylistic preferences.
- Quote or reference exact parts of the prompt when useful.
- Distinguish between:
  - conflicting instructions
  - unclear precedence
  - missing context
  - unclear output expectations
  - low-signal or overloaded context

## Required Output Format

Return one JSON array only.
Do not include markdown fences.
Do not include any prose before or after the JSON.

Each array item must conform to `tests/question_generator/non_render_prompt_review_schema.json`.

Use this shape:

```json
[
  {
    "stage": "routing",
    "hard_gates": {
      "instruction_coherence": "PASS",
      "input_precedence_clarity": "PASS",
      "output_requirement_clarity": "PASS",
      "sufficient_starting_context": "PASS"
    },
    "scores": {
      "task_clarity": 4,
      "context_usefulness": 4,
      "guidance_and_constraint_clarity": 4,
      "readability": 4,
      "output_readiness": 4,
      "confidence_to_execute": 4,
      "context_efficiency": 4,
      "risk_of_misinterpretation": 4
    },
    "top_findings": [
      {
        "title": "Short finding title",
        "why_it_matters": "Why this would make execution harder or risk a wrong answer.",
        "prompt_evidence": "The exact unclear, conflicting, or weak part of the prompt."
      }
    ],
    "overall_recommendation": "Accept",
    "summary": "A short summary of whether this prompt would let an analyst do the task confidently."
  }
]
```
