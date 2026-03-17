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
- Do not drift into essay form.

What is being monitored:
- {{boundary.exact_object_of_analysis}}
- Core system: {{boundary.core_system}}

Core thesis / competing paths:
- Base case: {{scenarios.base_case.summary}}
{{#scenarios.alternative_scenarios}}
- {{name}}: {{summary}}
{{/scenarios.alternative_scenarios}}

Signal table:
{{#signals}}
- Signal: {{signal}}
  Linked question: {{linked_question}}
  Preferred evidence source: {{preferred_evidence_source}}
  Backup evidence source: {{backup_evidence_source}}
  Cadence: {{cadence}}
  Changes action vs belief: {{changes_action_vs_belief}}
  Thresholds:
  {{#thresholds}}
  - {{.}}
  {{/thresholds}}
  Update rules:
  {{#update_rules}}
  - {{.}}
  {{/update_rules}}
{{/signals}}

What to watch:
{{#monitoring.what_to_watch}}
- {{item}}
  Why it matters: {{why_it_matters}}
  Escalation triggers:
  {{#escalation_triggers}}
  - {{.}}
  {{/escalation_triggers}}
  Action triggers:
  {{#action_triggers}}
  - {{.}}
  {{/action_triggers}}
  Noise to ignore:
  {{#noise_to_ignore}}
  - {{.}}
  {{/noise_to_ignore}}
  Update cadence: {{update_cadence}}
{{/monitoring.what_to_watch}}

Evidence plan:
{{#evidence_plan.evidence_hierarchy}}
- {{.}}
{{/evidence_plan.evidence_hierarchy}}

Most useful signals:
- Most reducing dominant uncertainty: {{monitoring.signal_most_reducing_dominant_uncertainty}}
- Most likely to change action: {{monitoring.signal_most_likely_to_change_action}}

Dominant uncertainty mode:
- {{routing.uncertainty_mode}}

Dominant decision mode:
- {{routing.decision_mode}}

Decision-mode implications:
What must be known before acting:
{{#decision_logic.must_know_before_action}}
- {{.}}
{{/decision_logic.must_know_before_action}}

What can be learned after acting:
{{#decision_logic.can_learn_after_action}}
- {{.}}
{{/decision_logic.can_learn_after_action}}

Appropriate evidence threshold:
- {{decision_logic.appropriate_evidence_threshold}}
- Reversibility logic: {{decision_logic.reversibility_logic}}
- Sizing logic: {{decision_logic.sizing_logic}}
- Staging logic: {{decision_logic.staging_logic}}

Action thresholds:
{{#decision_logic.triggers}}
- {{.}}
{{/decision_logic.triggers}}
{{#decision_logic.hedge_exit_kill_criteria}}
- {{.}}
{{/decision_logic.hedge_exit_kill_criteria}}

Top killer questions:
{{#questions.top_killer_questions}}
- {{question}}
{{/questions.top_killer_questions}}

What would change the conclusion:
{{#uncertainty_map.task_material_uncertainties}}
- {{.}}
{{/uncertainty_map.task_material_uncertainties}}
{{#scenarios.base_case.branch_triggers}}
- {{.}}
{{/scenarios.base_case.branch_triggers}}
{{#scenarios.alternative_scenarios}}
{{#branch_triggers}}
- {{.}}
{{/branch_triggers}}
{{/scenarios.alternative_scenarios}}

What to monitor next:
{{#monitoring.what_to_monitor_next}}
- {{.}}
{{/monitoring.what_to_monitor_next}}
