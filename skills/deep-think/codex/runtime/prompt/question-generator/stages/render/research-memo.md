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

System boundary:
- Exact object of analysis: {{boundary.exact_object_of_analysis}}
- Core system: {{boundary.core_system}}

Adjacent systems:
{{#boundary.adjacent_systems}}
- {{.}}
{{/boundary.adjacent_systems}}

Out-of-scope factors:
{{#boundary.out_of_scope_factors}}
- {{.}}
{{/boundary.out_of_scope_factors}}

Decisive stakeholders:
{{#structure.decisive_stakeholders}}
- {{.}}
{{/structure.decisive_stakeholders}}

Causal mechanism:
{{#structure.causal_mechanism}}
- {{.}}
{{/structure.causal_mechanism}}

Killer variables / bottlenecks:
{{#structure.killer_variables}}
- Killer variable: {{.}}
{{/structure.killer_variables}}
{{#structure.bottlenecks}}
- Bottleneck: {{.}}
{{/structure.bottlenecks}}

Scenario branches:
- Base case: {{scenarios.base_case.summary}}
{{#scenarios.alternative_scenarios}}
- {{name}}: {{summary}}
{{/scenarios.alternative_scenarios}}

Highest-value questions:
{{#questions.structural}}
- {{question}}
{{/questions.structural}}
{{#questions.evidence}}
- {{question}}
{{/questions.evidence}}

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
{{/evidence_plan.question_to_evidence_mapping}}

Research priorities:
{{#evidence_plan.question_to_evidence_mapping}}
- {{question}}
  {{#preferred_sources}}
  - Preferred source: {{.}}
  {{/preferred_sources}}
{{/evidence_plan.question_to_evidence_mapping}}

Uncertainty map:
{{#uncertainty_map.reducible_unknowns}}
- Reducible: {{.}}
{{/uncertainty_map.reducible_unknowns}}
{{#uncertainty_map.partially_reducible_unknowns}}
- Partially reducible: {{.}}
{{/uncertainty_map.partially_reducible_unknowns}}
{{#uncertainty_map.irreducible_uncertainties}}
- Irreducible: {{.}}
{{/uncertainty_map.irreducible_uncertainties}}
{{#uncertainty_map.task_material_uncertainties}}
- Task-material: {{.}}
{{/uncertainty_map.task_material_uncertainties}}

Signals to watch:
{{#signals}}
- {{signal}} ({{changes_action_vs_belief}})
{{/signals}}

What to monitor next:
{{#monitoring.what_to_monitor_next}}
- {{.}}
{{/monitoring.what_to_monitor_next}}

Decision-mode implications:
{{#scenarios.base_case.decision_mode_implications}}
- Base case: {{.}}
{{/scenarios.base_case.decision_mode_implications}}
{{#scenarios.alternative_scenarios}}
{{#decision_mode_implications}}
- {{name}}: {{.}}
{{/decision_mode_implications}}
{{/scenarios.alternative_scenarios}}

What would change the conclusion:
{{#scenarios.base_case.branch_triggers}}
- {{.}}
{{/scenarios.base_case.branch_triggers}}
{{#scenarios.alternative_scenarios}}
{{#branch_triggers}}
- {{.}}
{{/branch_triggers}}
{{/scenarios.alternative_scenarios}}
{{#decision_logic.triggers}}
- {{.}}
{{/decision_logic.triggers}}
{{#uncertainty_map.task_material_uncertainties}}
- {{.}}
{{/uncertainty_map.task_material_uncertainties}}
{{#signals}}
{{#thresholds}}
- {{.}}
{{/thresholds}}
{{/signals}}
