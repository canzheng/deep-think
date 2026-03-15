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
- The final prompt must be directly executable.

Boundary:
- Exact object of analysis: {{boundary.exact_object_of_analysis}}
- Core system: {{boundary.core_system}}

Scope assumptions:
{{#boundary.scope_assumptions}}
- {{.}}
{{/boundary.scope_assumptions}}

Stakeholders to analyze:
{{#structure.stakeholders}}
- {{.}}
{{/structure.stakeholders}}

Mechanisms to test:
{{#structure.causal_mechanism}}
- {{.}}
{{/structure.causal_mechanism}}

Variables / bottlenecks to assess:
{{#structure.killer_variables}}
- Killer variable: {{.}}
{{/structure.killer_variables}}
{{#structure.bottlenecks}}
- Bottleneck: {{.}}
{{/structure.bottlenecks}}
{{#structure.threshold_variables}}
- Threshold variable: {{.}}
{{/structure.threshold_variables}}

Scenario map:
- Base case: {{scenarios.base_case.summary}}
{{#scenarios.alternative_scenarios}}
- {{name}}: {{summary}}
{{/scenarios.alternative_scenarios}}

Core questions:
{{#questions.top_killer_questions}}
- {{question}}
  Why it matters: {{why_it_matters}}
{{/questions.top_killer_questions}}
{{#questions.evidence}}
- {{question}}
{{/questions.evidence}}

Evidence mode and source priorities:
- Evidence mode: {{routing.evidence_mode}}
{{#evidence_plan.evidence_hierarchy}}
- {{.}}
{{/evidence_plan.evidence_hierarchy}}
{{#evidence_plan.preferred_source_types}}
- Preferred source type: {{.}}
{{/evidence_plan.preferred_source_types}}
{{#evidence_plan.backup_source_types}}
- Backup source type: {{.}}
{{/evidence_plan.backup_source_types}}

Uncertainty mode and what it implies:
- Uncertainty mode: {{routing.uncertainty_mode}}
{{#uncertainty_map.task_material_uncertainties}}
- {{.}}
{{/uncertainty_map.task_material_uncertainties}}
{{#uncertainty_map.reducible_unknowns}}
- Reducible unknown: {{.}}
{{/uncertainty_map.reducible_unknowns}}

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

Decision mode and what it implies:
- Decision mode: {{routing.decision_mode}}
{{#questions.decision_mode_specific}}
- {{question}}
{{/questions.decision_mode_specific}}

Rules:
{{#evidence_plan.conflict_resolution_rules}}
- {{.}}
{{/evidence_plan.conflict_resolution_rules}}

What to monitor next:
{{#monitoring.what_to_monitor_next}}
- {{.}}
{{/monitoring.what_to_monitor_next}}

What would change the conclusion:
{{#decision_logic.triggers}}
- {{.}}
{{/decision_logic.triggers}}
{{#uncertainty_map.task_material_uncertainties}}
- {{.}}
{{/uncertainty_map.task_material_uncertainties}}

Final prompt:
- Produce a deep research workflow that uses the objective, mechanisms, questions, evidence priorities, and uncertainty map above as the governing structure.
