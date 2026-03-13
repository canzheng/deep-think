You are building the structural model for the current topic.

Your job is to produce a working model of how the system operates: who matters, what they want, what constrains them, how the system moves, and which variables dominate outcomes.

Purpose:
- build the world model
- separate actors, incentives, constraints, and mechanisms
- create the structural foundation for scenarios, questions, signals, and decisions

This step should:
- identify stakeholders
- identify decisive stakeholders
- infer incentives
- infer constraints
- map the causal mechanism
- identify killer variables
- identify bottlenecks
- identify threshold variables
- identify scarce resources

This step should not:
- obsess over formatting
- render the final memo
- choose final portfolio sizing
- convert structure directly into prose deliverables

Working rules:
- Use the topic, the stabilized boundary, the time horizon, and the unit of analysis as the basis for structural analysis.
- If the raw topic and the normalized framing differ in wording or precision, prefer the normalized framing and use the raw topic as background context only.
- Focus on the actors, forces, and mechanisms that materially shape the outcome.
- Distinguish decisive actors from actors that are merely visible, loud, or narratively prominent.
- Distinguish incentives from constraints, and constraints from mechanisms.
- Build a model of how the system actually moves, not just who is present.
- For any input marked `[CONDITIONAL]`, use it only if you strongly believe the stated condition is met for the current task.
- If the condition is not clearly met, ignore that input entirely.
- Do not force conditional inputs into the analysis just because they are provided.

Input topic:
{{{topic}}}

Scope anchors:
- Time horizon: {{routing.time_horizon}}
- Unit of analysis: {{routing.unit_of_analysis}}

Boundary already established:
- Exact object of analysis: {{boundary.exact_object_of_analysis}}
- Core system: {{boundary.core_system}}

[CONDITIONAL condition="Use this only if fragile assumptions, hidden drivers, or scope ambiguity could change which structure matters."]
Inherited scope discipline:
Assumptions:
{{#routing.assumptions}}
- {{.}}
{{/routing.assumptions}}

Scope assumptions:
{{#boundary.scope_assumptions}}
- {{.}}
{{/boundary.scope_assumptions}}

Out-of-scope factors:
{{#boundary.out_of_scope_factors}}
- {{.}}
{{/boundary.out_of_scope_factors}}
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if cross-system spillovers matter to the mechanism, bottlenecks, or decisive actors."]
Adjacent systems:
{{#boundary.adjacent_systems}}
- {{.}}
{{/boundary.adjacent_systems}}
[/CONDITIONAL]

{{#active_steering}}
## Stage Guidance
{{{active_steering}}}
{{/active_steering}}

## Step 1 - Stakeholder Mapping

Identify:
- primary actors
- secondary actors
- structural actors or forces
- decisive actors

For each decisive actor, determine:
- what this actor can actually change
- how direct the influence is
- whether the actor is causal, decisive, payoff-relevant, or signal-relevant

## Step 2 - Objectives and Incentives

For each decisive actor, determine:
- the primary objective
- secondary objectives
- what is public versus what is revealed by behavior
- whether short-term and long-term incentives are aligned
- whether there are internal factions or split incentives

## Step 3 - Constraints

For each decisive actor, determine:
- political constraints
- financial constraints
- operational constraints
- time constraints
- institutional, legal, or coalition constraints
- which actions are theoretically possible but practically too costly

## Step 4 - Causal Mechanism

Map:
- the main mechanism
- intermediate links
- weak links
- feedback loops
- fragile assumptions

Questions to resolve:
- Through what mechanism would X lead to Y?
- What are the intermediate steps?
- What link matters most?
- What link is most likely to fail?
- What would have to be true for the mechanism to break?

## Step 5 - Killer Variables and Bottlenecks

Identify:
- killer variables
- bottlenecks
- threshold variables
- scarce resources

Questions to resolve:
- Which variables most determine path outcomes?
- Which variables have threshold effects?
- What is the true bottleneck?
- What variable, if it moved sharply, would change the whole topic?

Output requirements:
- Produce a result fully consistent with the provided output schema.
- Include:
  - stakeholders
  - decisive stakeholders
  - incentives
  - constraints
  - causal mechanism
  - killer variables
  - bottlenecks
  - threshold variables
  - scarce resources

## Required Output
{{{required_output_schema}}}

Quality bar:
- Prefer causal relevance over descriptive completeness.
- Prefer mechanisms, incentives, and constraints over background trivia.
- Make the structure usable by downstream scenario, question, and decision work.
