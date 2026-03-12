You are building the monitoring layer for the current topic.

Your job is to turn the existing analysis into an operational watchlist: what to monitor, why it matters, what would trigger escalation or action, what noise to ignore, and which signals matter most for uncertainty reduction and action change.

Purpose:
- bridge research into ongoing operations
- convert signal design into a practical watch layer
- make future updates disciplined rather than reactive

This step should:
- define what to watch
- explain why each watch item matters
- identify the preferred evidence sources for each watch item
- define escalation triggers
- define action triggers
- define noise to ignore
- define update cadence
- identify the single signal most likely to reduce the dominant uncertainty
- identify the single signal most likely to change action
- identify what should be monitored next

This step should not:
- drift into essay form
- duplicate the whole analysis
- monitor everything equally
- confuse narrative noise with diagnostic change

Working rules:
- Use the provided topic and current state, especially the current signals and decision logic, as the basis for monitoring design.
- If the raw topic and the normalized current state differ in wording or precision, prefer the normalized routing and current-state framing and use the raw topic as background context only.
- Even if the requested output mode is not a dashboard, always produce a compact monitoring layer.
- Distinguish narrative from diagnostic signals.
- Focus on what would force an update in belief, branch weighting, or action.
- Prefer a small number of high-value watch items over a long unfocused list.

Input topic:
{{topic}}

{{current_state}}

{{active_steering}}

For the monitoring layer, determine:
- what to watch
- why it matters
- which evidence sources matter most
- what change would force an update
- what noise should be ignored
- what signal would most reduce the dominant uncertainty
- what signal would actually change action
- what should be monitored next

Output requirements:
- Produce a result fully consistent with the provided output schema.
- Include:
  - a `what_to_watch` list with operational tracking detail
  - the signal most reducing dominant uncertainty
  - the signal most likely to change action
  - what to monitor next

{{required_output}}

Quality bar:
- Make the monitoring layer practical and selective.
- Do not monitor everything equally.
- Make it clear what should trigger attention, what should trigger action, and what should be ignored.
