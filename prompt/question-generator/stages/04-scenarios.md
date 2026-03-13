You are turning the current structural analysis into scenario branches.

Your job is to map the plausible paths forward, identify what creates those branches, and explain how those branches matter for action and interpretation.

Purpose:
- turn structure into branches
- identify the plausible paths that compete with one another
- connect branch logic to decisions and updates

This step should:
- identify a base case
- generate alternative scenarios
- identify branch points
- identify branch triggers
- distinguish reversible branches from self-reinforcing ones
- explain why each branch is plausible
- note the decision implications of each branch

This step should not:
- overfit to source availability
- skip branch logic because the user wants a memo
- confuse scenarios with evidence
- collapse all uncertainty into one generic base case

Working rules:
- Use the topic, the stabilized boundary, the time horizon, and the structural model as the basis for scenario design.
- If the raw topic and the normalized framing differ in wording or precision, prefer the normalized framing and use the raw topic as background context only.
- Build scenarios from actor choices, causal mechanisms, constraints, bottlenecks, and threshold variables.
- Prefer a small number of meaningful branches over many shallow ones.
- Make each scenario meaningfully distinct in logic, not just tone.
- Include only scenarios that could materially change understanding, monitoring, or action.
- For any input marked `[CONDITIONAL]`, use it only if you strongly believe the stated condition is met for the current task.
- If the condition is not clearly met, ignore that input entirely.
- Do not force conditional inputs into the analysis just because they are provided.

Input topic:
{{{topic}}}

Scope anchors:
- Time horizon: {{routing.time_horizon}}

Boundary:
- Exact object of analysis: {{boundary.exact_object_of_analysis}}
- Core system: {{boundary.core_system}}

Structural model:
Decisive stakeholders:
{{#structure.decisive_stakeholders}}
- {{.}}
{{/structure.decisive_stakeholders}}

Incentives:
{{#structure.incentives}}
- {{.}}
{{/structure.incentives}}

Constraints:
{{#structure.constraints}}
- {{.}}
{{/structure.constraints}}

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

[CONDITIONAL condition="Use this only if scenario branches may spill into neighboring systems rather than staying inside the core system."]
Adjacent systems:
{{#boundary.adjacent_systems}}
- {{.}}
{{/boundary.adjacent_systems}}
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if branch logic depends on threshold effects, endurance limits, or non-decisive actors."]
Threshold variables:
{{#structure.threshold_variables}}
- {{.}}
{{/structure.threshold_variables}}

Scarce resources:
{{#structure.scarce_resources}}
- {{.}}
{{/structure.scarce_resources}}

Broader stakeholder set:
{{#structure.stakeholders}}
- {{.}}
{{/structure.stakeholders}}
[/CONDITIONAL]

{{#active_steering}}
## Stage Guidance
{{{active_steering}}}
{{/active_steering}}

Questions to resolve:
- What are the plausible paths from here?
- Which actor decisions create the branches?
- Which variable thresholds create the branches?
- Which triggers would move the system into a different branch?
- Which branches are reversible?
- Which branches are self-reinforcing once entered?

Output requirements:
- Produce a result fully consistent with the provided output schema.
- Define:
  - one base case
  - two to four plausible alternative scenarios when justified by the topic
- For each scenario, include:
  - name
  - summary
  - branch points
  - branch triggers
  - reversibility
  - probability logic
  - decision implications

## Required Output
{{{required_output_schema}}}

Quality bar:
- Make branches structurally meaningful, not cosmetically different.
- Do not confuse what is likely with what is merely easy to describe.
- Make the scenarios useful for later questions, signals, and decisions.
