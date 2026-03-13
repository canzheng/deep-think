You are generating the final deliverable for the current topic.

Your job is to turn the provided topic, relevant context, and guidance into the requested final output.

Purpose:
- produce the final deliverable in the requested output mode
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
- Use the provided relevant context and stage guidance as the full basis for the deliverable.
- Follow the selected output mode for the final deliverable structure.
- Include assumptions, unknowns, and what would change the conclusion when they materially help the final deliverable.
- Be explicit when the available context is incomplete instead of inventing certainty.

Output-mode rules:
- When the output mode implies a memo, produce a complete memo rather than analysis notes.
- When the output mode implies a dashboard, keep the result structured, compact, and non-essay-like.
- When the output mode implies a scenario tree or worksheet, preserve the shape of that format instead of flattening it into prose.
- When the output mode is a deep-research prompt, the final prompt must be directly usable as written.

Input topic:
{{topic}}

{{current_state}}

{{active_steering}}

Output requirements:
- Produce the final deliverable itself, not commentary about how to produce it.
- Use the selected output mode as the primary guide for organization.
- Surface the most important conclusions first when the selected output mode allows it.
- Preserve the most important open questions, uncertainties, monitoring signals, and decision implications when they are relevant to the deliverable.
- Keep the final deliverable internally consistent with the provided context and guidance.

{{required_output}}

Quality bar:
- The final deliverable should read like a finished artifact for the user, not an intermediate stage output.
- The structure should feel natural for the selected output mode.
- The most important conclusions, assumptions, and uncertainties should be easy to find.
- Do not add filler, repetition, or generic framing.
