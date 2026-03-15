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

Thesis fit:
- Recommendation frame: {{synthesis.recommendation_or_action_frame}}

Mechanism:
{{#structure.causal_mechanism}}
- {{.}}
{{/structure.causal_mechanism}}

Decisive stakeholders:
{{#structure.decisive_stakeholders}}
- {{.}}
{{/structure.decisive_stakeholders}}

Killer variables / bottlenecks:
{{#structure.killer_variables}}
- {{.}}
{{/structure.killer_variables}}
{{#structure.bottlenecks}}
- {{.}}
{{/structure.bottlenecks}}

Market-implied view:
- Base case probability logic: {{scenarios.base_case.probability_logic}}

Evidence mode rationale:
- Evidence mode: {{routing.evidence_mode}}
{{#evidence_plan.evidence_hierarchy}}
- {{.}}
{{/evidence_plan.evidence_hierarchy}}

Uncertainty mode rationale:
- {{routing.uncertainty_mode}}
{{#uncertainty_map.task_material_uncertainties}}
- {{.}}
{{/uncertainty_map.task_material_uncertainties}}

Decision mode rationale:
- Decision mode: {{routing.decision_mode}}
- Staging logic: {{decision_logic.staging_logic}}
- Sizing logic: {{decision_logic.sizing_logic}}

Catalysts:
{{#signals}}
- {{signal}}
{{/signals}}

Killer questions:
{{#questions.top_killer_questions}}
- {{question}}
{{/questions.top_killer_questions}}

Monitoring signals:
{{#signals}}
- {{signal}} ({{changes_action_vs_belief}})
{{/signals}}

What to monitor next:
{{#monitoring.what_to_monitor_next}}
- {{.}}
{{/monitoring.what_to_monitor_next}}

Portfolio role / sizing / staging:
{{#decision_logic.must_know_before_action}}
- {{.}}
{{/decision_logic.must_know_before_action}}
- Reversibility logic: {{decision_logic.reversibility_logic}}
- Sizing logic: {{decision_logic.sizing_logic}}
- Staging logic: {{decision_logic.staging_logic}}

Verdict:
- {{synthesis.why_now_or_why_not_now}}

Conviction:
{{#synthesis.what_must_be_true}}
- {{.}}
{{/synthesis.what_must_be_true}}

What would change the view:
{{#decision_logic.triggers}}
- {{.}}
{{/decision_logic.triggers}}
{{#uncertainty_map.task_material_uncertainties}}
- {{.}}
{{/uncertainty_map.task_material_uncertainties}}
