You are generating the final deliverable for the current topic.

Input topic:
{{{topic}}}

Final output mode
- {{render_mode}}

Your job is to turn the provided topic, framing, and analysis into the requested final output:
- produce the final deliverable in the selected output mode
- translate the accumulated analysis into a clear, useful final artifact
- preserve the most decision-relevant conclusions, uncertainties, and next-step implications

This step should:
- generate the final deliverable directly
- use the selected output mode to determine structure, section order, tone, and level of detail
- rely on the provided context rather than redoing the earlier analysis
- make the final artifact clear, coherent, and useful for the intended task

This step should not:
- redo upstream analysis from scratch
- invent missing evidence, scenarios, or decision logic that is not supported by the provided context
- ignore the selected output mode
- expose internal workflow mechanics or process notes in the final deliverable

Working rules:
- Use the provided topic as background context.
- If the raw topic and the normalized context differ in wording or precision, prefer the normalized context and use the raw topic only as supporting background.
- Use the provided framing and selected analysis slices as the full basis for the deliverable.
- Follow the selected output mode for the final deliverable structure.
- Include assumptions, unknowns, and what would change the conclusion when they materially help the final deliverable.
- Be explicit when the available context is incomplete instead of inventing certainty.
- Synthesize rather than recap upstream analysis.
- Include only the assumptions, uncertainties, signals, and next steps that materially improve the deliverable.
- Omit low-value detail that does not change the recommendation, interpretation, or usefulness of the artifact.

{{#output_language_instruction}}
Output language:
- {{output_language_instruction}}
{{/output_language_instruction}}


Working framing:
- Normalized question: {{routing.question}}
- Desired output: {{routing.desired_output}}
- Decision context: {{routing.decision_context}}
- Risk tolerance: {{routing.risk_tolerance}}
- Time horizon: {{routing.time_horizon}}
- Unit of analysis: {{routing.unit_of_analysis}}

Explicit constraints:
{{#routing.explicit_constraints}}
- {{.}}
{{/routing.explicit_constraints}}

Assumptions:
{{#routing.assumptions}}
- {{.}}
{{/routing.assumptions}}

{{{render_body}}}

Output requirements:
- Produce the final deliverable itself, not commentary about how to produce it.
- Use the selected output mode as the primary guide for organization.
- Return the final deliverable in clean Markdown.
- Use explicit structure that fits the selected output mode, such as headings, bullets, numbered lists, or tables when helpful.
- Do not use flat prose when the selected output mode calls for a more structured artifact.
- Surface the most important conclusions first when the selected output mode allows it.
- Preserve the most important open questions, uncertainties, monitoring signals, decision implications, and any subtemplate-specific guidance when they are relevant to the deliverable.
- Keep the final deliverable internally consistent with the provided context and guidance.


Quality bar:
- The final deliverable should read like a finished artifact for the user, not an intermediate stage output.
- The structure should feel natural for the selected output mode.
- The most important conclusions, assumptions, and uncertainties should be easy to find.
- Do not add filler, repetition, or generic framing.
