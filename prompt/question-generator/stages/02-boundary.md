You are defining the analysis boundary for the current topic.

Your job is to specify exactly what is being analyzed, what belongs inside the frame, what stays outside it, and which assumptions keep the scope coherent.

Purpose:
- define what system is actually being analyzed
- stabilize scope before deeper structural analysis begins
- prevent drift, sprawl, and accidental topic expansion

This step should:
- define the exact object of analysis
- define the core system
- identify adjacent systems that matter but should not dominate
- identify out-of-scope factors
- state the assumptions required to keep the boundary stable

This step should not:
- drift into source collection
- produce final deliverable formatting
- collapse adjacent systems into the core system
- solve the full problem downstream

Working rules:
- Use the topic, the time horizon, the unit of analysis, and the working assumptions as the basis for scope definition.
- If the raw topic and the normalized framing differ in wording or precision, prefer the normalized framing and use the raw topic as background context only.
- Draw the boundary around the object that is most decision-useful or analytically useful to study.
- Keep adjacent systems visible only if they materially affect the core system.
- Exclude factors that are interesting but not necessary for this run.
- State scope assumptions explicitly when they are needed to keep the boundary workable.
- For any input marked `[CONDITIONAL]`, use it only if you strongly believe the stated condition is met for the current task.
- If the condition is not clearly met, ignore that input entirely.
- Do not force conditional inputs into the analysis just because they are provided.

Input topic:
{{{topic}}}

Scope anchors:
- Time horizon: {{routing.time_horizon}}
- Unit of analysis: {{routing.unit_of_analysis}}

Working assumptions:
{{#routing.assumptions}}
- {{.}}
{{/routing.assumptions}}

[CONDITIONAL condition="Use this only if the user has already fixed a deliverable shape tightly enough that the boundary should match it."]
Requested deliverable shape:
- {{routing.desired_output}}
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

Questions to resolve:
- What system are we actually analyzing?
- What exactly is the object of analysis?
- What belongs inside the frame?
- Which adjacent systems matter but should not dominate?
- Which factors are intentionally out of scope?
- What assumptions define and stabilize this scope?

Output requirements:
- Produce a result fully consistent with the provided output schema.
- Define:
  - exact object of analysis
  - core system
  - adjacent systems
  - out-of-scope factors
  - scope assumptions

## Required Output
{{{required_output_schema}}}

Quality bar:
- Make the boundary specific enough that downstream stages know what world they are reasoning about.
- Avoid vague scope language that could justify almost anything.
- Do not confuse neighboring systems with the core system under analysis.
