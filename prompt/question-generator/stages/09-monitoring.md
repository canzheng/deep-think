You are building the monitoring layer for the current topic.

Your job is to turn the existing analysis into an operational watchlist: what to monitor, why it matters, what would trigger escalation or action, what noise to ignore, and which signals matter most for uncertainty reduction and action change.

Purpose:
- bridge research into ongoing operations
- convert signal design into a practical watch layer
- make future updates disciplined rather than reactive

This step should:
- define what to watch
- explain why each watch item matters
- identify the preferred evidence sources for each watch item
- define escalation triggers
- define action triggers
- define noise to ignore
- define update cadence
- identify the single signal most likely to reduce the dominant uncertainty
- identify the single signal most likely to change action
- identify what should be monitored next

This step should not:
- drift into essay form
- duplicate the whole analysis
- monitor everything equally
- confuse narrative noise with diagnostic change

Working rules:
- Use the topic plus the current signals and task-material uncertainties as the basis for monitoring design.
- If the raw topic and the normalized framing differ in wording or precision, prefer the normalized framing and use the raw topic as background context only.
- Even if the requested output mode is not a dashboard, always produce a compact monitoring layer.
- Distinguish narrative from diagnostic signals.
- Focus on what would force an update in belief, branch weighting, or action.
- Prefer a small number of high-value watch items over a long unfocused list.
- For any input marked `[CONDITIONAL]`, use it only if you strongly believe the stated condition is met for the current task.
- If the condition is not clearly met, ignore that input entirely.
- Do not force conditional inputs into the analysis just because they are provided.

Input topic:
{{{topic}}}

Signals already identified:
{{#signals}}
- Signal: {{signal}}
  {{#linked_question}}Linked question: {{linked_question}}{{/linked_question}}
  Preferred evidence source: {{preferred_evidence_source}}
  Backup evidence source: {{backup_evidence_source}}
  Cadence: {{cadence}}
  Thresholds:
  {{#thresholds}}
  - {{.}}
  {{/thresholds}}

  Update rules:
  {{#update_rules}}
  - {{.}}
  {{/update_rules}}

  Belief update implications:
  {{#belief_update_implications}}
  - {{.}}
  {{/belief_update_implications}}
  Confidence under current uncertainty mode: {{confidence_under_current_uncertainty_mode}}
  Changes action vs belief: {{changes_action_vs_belief}}
{{/signals}}

Task-material uncertainties:
{{#uncertainty_map.task_material_uncertainties}}
- {{.}}
{{/uncertainty_map.task_material_uncertainties}}

[CONDITIONAL condition="Use this only if monitoring should trigger adds, trims, stops, or hedges rather than only update beliefs."]
Action-linked decision logic:
Triggers:
{{#decision_logic.triggers}}
- {{.}}
{{/decision_logic.triggers}}

Hedge, exit, and kill criteria:
{{#decision_logic.hedge_exit_kill_criteria}}
- {{.}}
{{/decision_logic.hedge_exit_kill_criteria}}
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if monitoring should explicitly track competing scenario paths."]
Scenario branch triggers:
Base case:
{{#scenarios.base_case.branch_triggers}}
- {{.}}
{{/scenarios.base_case.branch_triggers}}

Alternative scenarios:
{{#scenarios.alternative_scenarios}}
- {{name}}
  {{#branch_triggers}}
  - {{.}}
  {{/branch_triggers}}
{{/scenarios.alternative_scenarios}}
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if source hierarchy should influence monitoring cadence or escalation beyond the default signal-level source fields."]
Evidence source hierarchy:
Preferred source types:
{{#evidence_plan.preferred_source_types}}
- {{.}}
{{/evidence_plan.preferred_source_types}}

Backup source types:
{{#evidence_plan.backup_source_types}}
- {{.}}
{{/evidence_plan.backup_source_types}}
[/CONDITIONAL]

{{#active_steering}}
## Stage Guidance
{{{active_steering}}}
{{/active_steering}}

For the monitoring layer, determine:
- what to watch
- why it matters
- which evidence sources matter most
- what change would force an update
- what noise should be ignored
- what signal would most reduce the dominant uncertainty
- what signal would actually change action
- what should be monitored next

Output requirements:
- Produce a result fully consistent with the provided output schema.
- Include:
  - a `what_to_watch` list with operational tracking detail
  - the signal most reducing dominant uncertainty
  - the signal most likely to change action
  - what to monitor next

## Required Output
{{{required_output_schema}}}

Quality bar:
- Make the monitoring layer practical and selective.
- Do not monitor everything equally.
- Make it clear what should trigger attention, what should trigger action, and what should be ignored.
