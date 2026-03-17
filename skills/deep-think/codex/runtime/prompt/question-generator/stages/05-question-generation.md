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
- Use the topic plus the current scope anchors, structure, and scenario picture as the basis for question generation.
- If the raw topic and the normalized framing differ in wording or precision, prefer the normalized framing and use the raw topic as background context only.
- Generate questions that emerge from structure, incentives, constraints, scenarios, and decision needs.
- Prefer questions that can change the explanation, forecast, decision, monitoring framework, investment view, or downstream research instructions.
- Deprioritize questions that are merely interesting, historical, or descriptive.
- If a question cannot change the answer, reduce uncertainty, identify a branch point, create a signal, or change action, timing, sizing, staging, or monitoring, deprioritize it.
- For any input marked `[CONDITIONAL]`, use it only if you strongly believe the stated condition is met for the current task.
- If the condition is not clearly met, ignore that input entirely.
- Do not force conditional inputs into the analysis just because they are provided.

Input topic:
{{{topic}}}

Scope anchors:
- Time horizon: {{routing.time_horizon}}
- Unit of analysis: {{routing.unit_of_analysis}}

Structural model:
Decisive stakeholders:
{{#structure.decisive_stakeholders}}
- {{.}}
{{/structure.decisive_stakeholders}}

Constraints:
{{#structure.constraints}}
- {{.}}
{{/structure.constraints}}

Causal mechanism:
{{#structure.causal_mechanism}}
- {{.}}
{{/structure.causal_mechanism}}

Killer variables:
{{#structure.killer_variables}}
- {{.}}
{{/structure.killer_variables}}

Bottlenecks:
{{#structure.bottlenecks}}
- {{.}}
{{/structure.bottlenecks}}

Scenario framing:
- Base case summary: {{scenarios.base_case.summary}}
Base-case branch points:
{{#scenarios.base_case.branch_points}}
- {{.}}
{{/scenarios.base_case.branch_points}}

Base-case branch triggers:
{{#scenarios.base_case.branch_triggers}}
- {{.}}
{{/scenarios.base_case.branch_triggers}}

Alternative scenarios:
{{#scenarios.alternative_scenarios}}
- {{name}}: {{summary}}
  Branch points:
  {{#branch_points}}
  - {{.}}
  {{/branch_points}}
  Branch triggers:
  {{#branch_triggers}}
  - {{.}}
  {{/branch_triggers}}
{{/scenarios.alternative_scenarios}}

[CONDITIONAL condition="Use this only if scope drift or ambiguous framing would change which questions matter most."]
Boundary anchors:
- Exact object of analysis: {{boundary.exact_object_of_analysis}}
- Core system: {{boundary.core_system}}
Scope assumptions:
{{#boundary.scope_assumptions}}
- {{.}}
{{/boundary.scope_assumptions}}
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if threshold effects, endurance limits, or broader stakeholder coverage would materially change the question set."]
Threshold variables:
{{#structure.threshold_variables}}
- {{.}}
{{/structure.threshold_variables}}

Scarce resources:
{{#structure.scarce_resources}}
- {{.}}
{{/structure.scarce_resources}}

Broader stakeholder set:
{{#structure.stakeholders}}
- {{.}}
{{/structure.stakeholders}}
[/CONDITIONAL]

## Stage Guidance
Each guidance item includes an importance label that indicates how strongly it should shape the result of this stage.
{{#stage_guidance.required}}
- {{importance}}: {{guidance}}
{{/stage_guidance.required}}
{{#stage_guidance.conditional}}
[CONDITIONAL condition="{{condition}}"]
- {{importance}}: {{guidance}}
[/CONDITIONAL]
{{/stage_guidance.conditional}}

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

## Required Output
{{{required_output_schema}}}

{{#feedback_schema}}
## Feedback
{{{feedback_schema}}}
{{/feedback_schema}}

Quality bar:
- Do not generate generic filler questions.
- Do not generate background, history, or profile questions unless they directly affect the task.
- Make the question set sharp enough to guide evidence planning and signal design.
