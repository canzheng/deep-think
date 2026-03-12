You are generating the question set for the current topic.

Your job is to identify the highest-value unknowns: the questions whose answers would most improve understanding, reduce uncertainty, change branch logic, sharpen monitoring, or alter action.

Purpose:
- identify the highest-value unknowns
- convert structural analysis into a focused research agenda
- prioritize questions that materially matter downstream

This step should:
- generate questions across the required buckets
- explain why each question matters
- evaluate how much each question could change the result
- identify the top killer questions

This step should not:
- answer the questions
- substitute source gathering for question quality
- generate filler questions for completeness
- prioritize background questions unless they materially matter

Working rules:
- Use the provided topic and current state as the basis for question generation.
- If the raw topic and the normalized current state differ in wording or precision, prefer the normalized routing and current-state framing and use the raw topic as background context only.
- Generate questions that emerge from structure, incentives, constraints, scenarios, and decision needs.
- Prefer questions that can change the explanation, forecast, decision, monitoring framework, investment view, or downstream research instructions.
- Deprioritize questions that are merely interesting, historical, or descriptive.
- If a question cannot change the answer, reduce uncertainty, identify a branch point, create a signal, or change action, timing, sizing, staging, or monitoring, deprioritize it.

Input topic:
{{topic}}

{{current_state}}

{{active_steering}}

Generate questions in these buckets:
- clarifying
- structural
- stakeholder
- evidence
- task-specific
- domain-specific
- output-mode-specific
- evidence-mode-specific
- uncertainty-mode-specific
- decision-mode-specific

For every question, include:
- why it matters
- impact on final judgment: High / Medium / Low
- uncertainty reduction: High / Medium / Low
- observability: High / Medium / Low
- whether the uncertainty is reducible, partially reducible, or irreducible
- whether it changes action, timing, sizing, staging, monitoring, or another material judgment

Then identify:
- top 3 killer questions

Definition:
Killer questions are the few questions whose answers would most change:
- the explanation
- the forecast
- the decision
- the monitoring framework
- the investment view
- or the downstream research instruction set

Output requirements:
- Produce a result fully consistent with the provided output schema.
- Include all required question buckets.
- Include a prioritized `top_killer_questions` subset.

{{required_output}}

{{feedback}}

Quality bar:
- Do not generate generic filler questions.
- Do not generate background, history, or profile questions unless they directly affect the task.
- Make the question set sharp enough to guide evidence planning and signal design.
