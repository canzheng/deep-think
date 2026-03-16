You are planning how to answer the key questions for the current topic.

Your job is to decide what kinds of evidence should be trusted most, how important questions map to evidence sources, how conflicts should be handled, and which uncertainties can or cannot be reduced.

Purpose:
- decide how to prove or disprove the key questions
- define the evidence hierarchy for this topic
- map important questions to source strategies
- distinguish reducible uncertainty from uncertainty that must be borne

This step should:
- rank evidence from strongest to weakest for this topic
- identify preferred source types
- identify backup source types
- define conflict resolution rules
- map important questions to preferred and backup evidence sources
- identify reducible, partially reducible, and irreducible uncertainties
- identify which uncertainties actually matter for the task

This step should not:
- rewrite the mechanism unless evidence planning reveals a structural break
- produce the final decision
- confuse loud evidence with diagnostic evidence
- confuse evidence hierarchy with rhetorical confidence

Working rules:
- Use the topic plus the key questions and scenario branch logic as the basis for evidence planning.
- If the raw topic and the normalized framing differ in wording or precision, prefer the normalized framing and use the raw topic as background context only.
- Rank evidence within the selected evidence guidance, but adapt to the actual topic.
- Prefer diagnostic evidence over vivid or noisy evidence.
- Distinguish what can be learned through research from what can only be managed through decision design, staging, or monitoring.
- State conflicts explicitly and explain what additional evidence would resolve them.
- For any input marked `[CONDITIONAL]`, use it only if you strongly believe the stated condition is met for the current task.
- If the condition is not clearly met, ignore that input entirely.
- Do not force conditional inputs into the analysis just because they are provided.

Input topic:
{{{topic}}}

Priority questions:
{{#questions.top_killer_questions}}
- {{question}}
  Why it matters: {{why_it_matters}}
{{/questions.top_killer_questions}}

Evidence questions:
{{#questions.evidence}}
- {{question}}
{{/questions.evidence}}

Evidence-guidance-specific questions:
{{#questions.evidence_mode_specific}}
- {{question}}
{{/questions.evidence_mode_specific}}

Uncertainty-guidance-specific questions:
{{#questions.uncertainty_mode_specific}}
- {{question}}
{{/questions.uncertainty_mode_specific}}

Scenario branch logic:
Base-case branch points:
{{#scenarios.base_case.branch_points}}
- {{.}}
{{/scenarios.base_case.branch_points}}

Base-case branch triggers:
{{#scenarios.base_case.branch_triggers}}
- {{.}}
{{/scenarios.base_case.branch_triggers}}

Alternative-scenario branch points and triggers:
{{#scenarios.alternative_scenarios}}
- {{name}}
  Branch points:
  {{#branch_points}}
  - {{.}}
  {{/branch_points}}
  Branch triggers:
  {{#branch_triggers}}
  - {{.}}
  {{/branch_triggers}}
{{/scenarios.alternative_scenarios}}

[CONDITIONAL condition="Use this only if action gating, stage-gates, or downstream deliverable requirements should change the evidence bar."]
Decision-gating questions:
{{#questions.decision_mode_specific}}
- {{question}}
{{/questions.decision_mode_specific}}

Deliverable-shaping questions:
{{#questions.output_mode_specific}}
- {{question}}
{{/questions.output_mode_specific}}

Decision context:
- {{routing.decision_context}}
- Risk tolerance: {{routing.risk_tolerance}}
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if source choice should be mechanism-aware rather than just question-aware."]
Mechanism details:
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

Base hierarchy:
1. Direct primary evidence
2. High-quality proximate evidence
3. Consistent triangulated qualitative evidence
4. Commentary or interpretation
5. Narrative without observable backing

Evidence rules:
- prefer direct over indirect
- prefer revealed behavior over stated intent
- prefer sustained evidence over one-off datapoints
- prefer diagnostic signals over loud signals
- state conflicts explicitly
- explain what additional evidence would resolve them

Questions to resolve:
- What evidence would most directly answer the highest-value questions?
- Which source families should be preferred?
- Which source families should be used as backup?
- How should conflicting evidence be handled?
- Which unknowns are reducible through research?
- Which unknowns are only partially reducible before action?
- Which uncertainties are irreducible and must be borne?
- Which of these uncertainties actually matter for the task?

Output requirements:
- Produce a result fully consistent with the provided output schema.
- Include:
  - evidence hierarchy
  - preferred source types
  - backup source types
  - conflict resolution rules
  - question-to-evidence mapping
  - reducible unknowns
  - partially reducible unknowns
  - irreducible uncertainties
  - task-material uncertainties

## Required Output
{{{required_output_schema}}}

{{#feedback_schema}}
## Feedback
{{{feedback_schema}}}
{{/feedback_schema}}

Quality bar:
- Make the evidence plan operational, not generic.
- Tie evidence choices to actual questions, not broad topic labels.
- Be explicit about what better evidence would change.
