You are translating the current questions into observable signals.

Your job is to define what to watch, where to observe it, how often to check it, what thresholds matter, how beliefs should update, and whether a signal changes belief only or should also change action.

Purpose:
- convert questions into observables
- connect uncertainty to watchable signals
- define how signals should update beliefs and actions

This step should:
- translate high-value questions into observable signals
- identify preferred and backup evidence sources for each signal
- define cadence
- define thresholds and update rules
- define belief update implications
- state confidence in each signal under the current uncertainty mode
- clarify whether each signal changes belief only or should also change action

This step should not:
- confuse signals with evidence hierarchy
- skip decision implications
- create monitoring noise with no update rule
- mistake narrative commentary for a diagnostic signal

Working rules:
- Use the topic plus the current question set, scenario triggers, and evidence plan as the basis for signal design.
- If the raw topic and the normalized framing differ in wording or precision, prefer the normalized framing and use the raw topic as background context only.
- Separate evidence from signals, and signals from decisions.
- Distinguish narrative from diagnostic signals.
- Prefer signals that can meaningfully change branch weights, confidence, monitoring, or action.
- Prefer a compact set of high-value signals over broad coverage.
- Avoid repeating upstream evidence detail unless it changes signal design.
- Make update logic explicit enough that someone could actually use the signals.
- For any input marked `[CONDITIONAL]`, use it only if you strongly believe the stated condition is met for the current task.
- If the condition is not clearly met, ignore that input entirely.
- Do not force conditional inputs into the analysis just because they are provided.

Input topic:
{{{topic}}}

Top killer questions:
{{#questions.top_killer_questions}}
- {{question}}
  Why it matters: {{why_it_matters}}
{{/questions.top_killer_questions}}

Evidence plan inputs:
Preferred source types:
{{#evidence_plan.preferred_source_types}}
- {{.}}
{{/evidence_plan.preferred_source_types}}

Backup source types:
{{#evidence_plan.backup_source_types}}
- {{.}}
{{/evidence_plan.backup_source_types}}

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

Scenario triggers:
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

[CONDITIONAL condition="Use this only if the signals should change action, timing, sizing, staging, or stop conditions rather than only changing belief."]
Action-linked decision logic:
Triggers:
{{#decision_logic.triggers}}
- {{.}}
{{/decision_logic.triggers}}

Hedge, exit, and kill criteria:
{{#decision_logic.hedge_exit_kill_criteria}}
- {{.}}
{{/decision_logic.hedge_exit_kill_criteria}}

Appropriate evidence threshold:
- {{decision_logic.appropriate_evidence_threshold}}
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if signals should map directly to bottlenecks, threshold variables, or other structural choke points."]
Structural anchors:
Killer variables:
{{#structure.killer_variables}}
- {{.}}
{{/structure.killer_variables}}

Threshold variables:
{{#structure.threshold_variables}}
- {{.}}
{{/structure.threshold_variables}}

Bottlenecks:
{{#structure.bottlenecks}}
- {{.}}
{{/structure.bottlenecks}}
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if signals should explicitly target the dominant uncertainties rather than serve as general monitoring."]
Task-material uncertainties:
{{#uncertainty_map.task_material_uncertainties}}
- {{.}}
{{/uncertainty_map.task_material_uncertainties}}
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

For each high-value question, determine:
- the linked question
- the observable signal
- the preferred evidence source
- the backup evidence source
- the cadence
- the thresholds
- the update rules
- the belief update implications
- confidence in the signal under the current uncertainty mode
- whether the signal changes belief only or should also change action

Where relevant, the update logic should capture whether the signal changes:
- action
- timing
- sizing
- staging
- hedge, exit, or kill criteria

Output requirements:
- Produce a result fully consistent with the provided output schema.
- Include a set of signals that directly connect important questions to observable updates.

## Required Output
{{{required_output_schema}}}

Quality bar:
- Prefer high-value, monitorable signals over noisy proxies.
- Do not create signals that are easy to observe but weakly diagnostic.
- Make the signal set usable for monitoring and decision updates.
