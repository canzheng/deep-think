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

Base case:
- Name: {{scenarios.base_case.name}}
- Summary: {{scenarios.base_case.summary}}
- Probability logic: {{scenarios.base_case.probability_logic}}
- Reversibility: {{scenarios.base_case.reversibility}}

Branch points:
{{#scenarios.base_case.branch_points}}
- {{.}}
{{/scenarios.base_case.branch_points}}

Branch triggers:
{{#scenarios.base_case.branch_triggers}}
- {{.}}
{{/scenarios.base_case.branch_triggers}}

Alternative scenarios:
{{#scenarios.alternative_scenarios}}
- {{name}}
  Summary: {{summary}}
  Probability logic: {{probability_logic}}
  Reversibility: {{reversibility}}
  Branch points:
  {{#branch_points}}
  - {{.}}
  {{/branch_points}}
  Branch triggers:
  {{#branch_triggers}}
  - {{.}}
  {{/branch_triggers}}
  Decision implications:
  {{#decision_mode_implications}}
  - {{.}}
  {{/decision_mode_implications}}
{{/scenarios.alternative_scenarios}}

Mechanisms to watch:
{{#structure.causal_mechanism}}
- {{.}}
{{/structure.causal_mechanism}}

Threshold variables:
{{#structure.threshold_variables}}
- {{.}}
{{/structure.threshold_variables}}

Killer variables:
{{#structure.killer_variables}}
- {{.}}
{{/structure.killer_variables}}

Top killer questions:
{{#questions.top_killer_questions}}
- {{question}}
{{/questions.top_killer_questions}}

Signals to watch:
{{#signals}}
- {{signal}}
  {{#thresholds}}
  - {{.}}
  {{/thresholds}}
{{/signals}}

Evidence and signals that would shift scenario confidence:
{{#evidence_plan.question_to_evidence_mapping}}
- {{question}}
  {{#preferred_sources}}
  - Preferred source: {{.}}
  {{/preferred_sources}}
{{/evidence_plan.question_to_evidence_mapping}}
{{#signals}}
- {{signal}}
  {{#belief_update_implications}}
  - {{.}}
  {{/belief_update_implications}}
{{/signals}}

Confidence and key unknowns:
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
- {{.}}
{{/uncertainty_map.task_material_uncertainties}}

What would change the conclusion:
{{#scenarios.base_case.branch_triggers}}
- {{.}}
{{/scenarios.base_case.branch_triggers}}
{{#scenarios.alternative_scenarios}}
{{#branch_triggers}}
- {{.}}
{{/branch_triggers}}
{{/scenarios.alternative_scenarios}}
{{#uncertainty_map.task_material_uncertainties}}
- {{.}}
{{/uncertainty_map.task_material_uncertainties}}

What to monitor next:
{{#monitoring.what_to_monitor_next}}
- {{.}}
{{/monitoring.what_to_monitor_next}}
