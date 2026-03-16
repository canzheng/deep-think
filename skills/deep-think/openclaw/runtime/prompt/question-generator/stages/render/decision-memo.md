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

Recommendation frame:
- {{synthesis.recommendation_or_action_frame}}

Why now / why not now:
- {{synthesis.why_now_or_why_not_now}}

What must be true:
{{#synthesis.what_must_be_true}}
- {{.}}
{{/synthesis.what_must_be_true}}

Key risks / failure modes:
{{#synthesis.key_risks_and_failure_modes}}
- {{.}}
{{/synthesis.key_risks_and_failure_modes}}

Evidence standard required to act:
- {{decision_logic.appropriate_evidence_threshold}}

Uncertainty that can be reduced before acting:
{{#uncertainty_map.reducible_unknowns}}
- {{.}}
{{/uncertainty_map.reducible_unknowns}}
{{#uncertainty_map.partially_reducible_unknowns}}
- {{.}}
{{/uncertainty_map.partially_reducible_unknowns}}

Uncertainty that must be accepted:
{{#uncertainty_map.irreducible_uncertainties}}
- {{.}}
{{/uncertainty_map.irreducible_uncertainties}}

What is most likely to change the path:
- Base case probability logic: {{scenarios.base_case.probability_logic}}
- Base case reversibility: {{scenarios.base_case.reversibility}}

Competing path triggers:
{{#scenarios.base_case.branch_triggers}}
- {{.}}
{{/scenarios.base_case.branch_triggers}}
{{#scenarios.alternative_scenarios}}
- {{name}}:
  {{#branch_triggers}}
  - {{.}}
  {{/branch_triggers}}
{{/scenarios.alternative_scenarios}}

Reversibility / sizing / staging logic:
- Reversibility logic: {{decision_logic.reversibility_logic}}
- Sizing logic: {{decision_logic.sizing_logic}}
- Staging logic: {{decision_logic.staging_logic}}

What must be known before acting:
{{#decision_logic.must_know_before_action}}
- {{.}}
{{/decision_logic.must_know_before_action}}

What can be learned after acting:
{{#decision_logic.can_learn_after_action}}
- {{.}}
{{/decision_logic.can_learn_after_action}}

Triggers:
{{#decision_logic.triggers}}
- {{.}}
{{/decision_logic.triggers}}

Hedge / exit / kill criteria:
{{#decision_logic.hedge_exit_kill_criteria}}
- {{.}}
{{/decision_logic.hedge_exit_kill_criteria}}

Top killer questions:
{{#questions.top_killer_questions}}
- {{question}}
  Why it matters: {{why_it_matters}}
{{/questions.top_killer_questions}}

Evidence plan:
{{#evidence_plan.evidence_hierarchy}}
- {{.}}
{{/evidence_plan.evidence_hierarchy}}
{{#evidence_plan.question_to_evidence_mapping}}
- {{question}}
  {{#preferred_sources}}
  - Preferred source: {{.}}
  {{/preferred_sources}}
{{/evidence_plan.question_to_evidence_mapping}}

What to monitor next:
{{#monitoring.what_to_monitor_next}}
- {{.}}
{{/monitoring.what_to_monitor_next}}

What would change the conclusion:
{{#decision_logic.triggers}}
- {{.}}
{{/decision_logic.triggers}}
{{#decision_logic.hedge_exit_kill_criteria}}
- {{.}}
{{/decision_logic.hedge_exit_kill_criteria}}
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
