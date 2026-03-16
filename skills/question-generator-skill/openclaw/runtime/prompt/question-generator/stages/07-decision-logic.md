You are converting the current analysis into decision logic.

Your job is to translate the existing state into actionable logic: what must be known before acting, what can be learned after acting, how strong the evidence bar should be, how reversibility matters, and what the current recommendation or action frame should be.

Purpose:
- convert analysis into action logic
- separate what must be resolved before action from what can be learned during action
- express how uncertainty should shape commitment, timing, sizing, and risk management

This step should:
- define what must be known before action
- define what can be learned after action
- define the appropriate evidence threshold
- define reversibility logic
- define sizing logic
- define staging logic
- define hedge, exit, and kill criteria
- define triggers for action, delay, scaling, or stop
- produce a concise synthesis of the recommendation or action frame

This step should not:
- reopen the full ontology unless a key assumption fails
- ignore the stage guidance when setting evidence thresholds
- hide behind generic balance on decision tasks
- drift into final deliverable formatting

Working rules:
- Use the topic plus the current decision context, scenario logic, evidence plan, and uncertainty map as the basis for decision logic.
- If the raw topic and the normalized framing differ in wording or precision, prefer the normalized framing and use the raw topic as background context only.
- Distinguish reducible uncertainty from uncertainty that must simply be borne.
- Be explicit about what would change the conclusion.
- Be explicit about when reversibility, staging, or diversification should lower commitment and when evidence strength should raise it.
- If the task is action-oriented, do not hide behind generic balance.
- For any input marked `[CONDITIONAL]`, use it only if you strongly believe the stated condition is met for the current task.
- If the condition is not clearly met, ignore that input entirely.
- Do not force conditional inputs into the analysis just because they are provided.

Input topic:
{{{topic}}}

Action frame:
- Decision context: {{routing.decision_context}}
- Risk tolerance: {{routing.risk_tolerance}}
- Time horizon: {{routing.time_horizon}}

Base-case scenario logic:
- Probability logic: {{scenarios.base_case.probability_logic}}
- Reversibility: {{scenarios.base_case.reversibility}}
Decision implications from the base case:
{{#scenarios.base_case.decision_mode_implications}}
- {{.}}
{{/scenarios.base_case.decision_mode_implications}}

Base-case branch triggers:
{{#scenarios.base_case.branch_triggers}}
- {{.}}
{{/scenarios.base_case.branch_triggers}}

Alternative scenarios:
{{#scenarios.alternative_scenarios}}
- {{name}}
  Probability logic: {{probability_logic}}
  Reversibility: {{reversibility}}
  Decision implications:
  {{#decision_mode_implications}}
  - {{.}}
  {{/decision_mode_implications}}
  Branch triggers:
  {{#branch_triggers}}
  - {{.}}
  {{/branch_triggers}}
{{/scenarios.alternative_scenarios}}

Evidence plan:
Evidence hierarchy:
{{#evidence_plan.evidence_hierarchy}}
- {{.}}
{{/evidence_plan.evidence_hierarchy}}

Preferred source types:
{{#evidence_plan.preferred_source_types}}
- {{.}}
{{/evidence_plan.preferred_source_types}}

Conflict-resolution rules:
{{#evidence_plan.conflict_resolution_rules}}
- {{.}}
{{/evidence_plan.conflict_resolution_rules}}

Question-to-evidence mapping:
{{#evidence_plan.question_to_evidence_mapping}}
- {{question}}
  Preferred sources:
  {{#preferred_sources}}
  - {{.}}
  {{/preferred_sources}}
  Backup sources:
  {{#backup_sources}}
  - {{.}}
  {{/backup_sources}}
{{/evidence_plan.question_to_evidence_mapping}}

Uncertainty map:
Reducible unknowns:
{{#uncertainty_map.reducible_unknowns}}
- {{.}}
{{/uncertainty_map.reducible_unknowns}}

Partially reducible unknowns:
{{#uncertainty_map.partially_reducible_unknowns}}
- {{.}}
{{/uncertainty_map.partially_reducible_unknowns}}

Irreducible uncertainties:
{{#uncertainty_map.irreducible_uncertainties}}
- {{.}}
{{/uncertainty_map.irreducible_uncertainties}}

Task-material uncertainties:
{{#uncertainty_map.task_material_uncertainties}}
- {{.}}
{{/uncertainty_map.task_material_uncertainties}}

[CONDITIONAL condition="Use this only if unresolved killer questions should explicitly gate action."]
Top killer questions:
{{#questions.top_killer_questions}}
- {{question}}
  Why it matters: {{why_it_matters}}
{{/questions.top_killer_questions}}
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if the exact action scope or inherited scope discipline is still ambiguous."]
Boundary anchors:
- Exact object of analysis: {{boundary.exact_object_of_analysis}}
Scope assumptions:
{{#boundary.scope_assumptions}}
- {{.}}
{{/boundary.scope_assumptions}}
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if the action rule depends on mechanism details, bottlenecks, or decisive variables rather than scenario summaries alone."]
Mechanism details:
Killer variables:
{{#structure.killer_variables}}
- {{.}}
{{/structure.killer_variables}}

Bottlenecks:
{{#structure.bottlenecks}}
- {{.}}
{{/structure.bottlenecks}}

Causal mechanism:
{{#structure.causal_mechanism}}
- {{.}}
{{/structure.causal_mechanism}}
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

Decision implications must include:
- what must be known before acting
- what can be learned after acting
- appropriate evidence threshold
- whether the decision should be sized, staged, hedged, diversified, delayed, or avoided

Questions to resolve:
- What must be known before acting?
- What can be learned after acting without unacceptable downside?
- What is the right evidence threshold for this case?
- How should reversibility affect timing and commitment size?
- Should the action be sized, staged, hedged, diversified, delayed, or avoided?
- What would change the conclusion?

Output requirements:
- Produce a result fully consistent with the provided output schema.
- Include:
  - must-know-before-action logic
  - can-learn-after-action logic
  - appropriate evidence threshold
  - reversibility logic
  - sizing logic
  - staging logic
  - hedge, exit, and kill criteria
  - triggers
  - recommendation or action frame
  - why now or why not now
  - what must be true
  - key risks and failure modes

## Required Output
{{{required_output_schema}}}

Quality bar:
- Make the decision logic operational rather than philosophical.
- Tie action guidance to the current uncertainty and the stage guidance.
- Be direct about what should happen, what should wait, and why.
