You are translating the current questions into observable signals.

Your job is to define what to watch, where to observe it, how often to check it, what thresholds matter, how beliefs should update, and whether a signal changes belief only or should also change action.

Purpose:
- convert questions into observables
- connect uncertainty to watchable signals
- define how signals should update beliefs and actions

This step should:
- translate high-value questions into observable signals
- identify preferred and backup evidence sources for each signal
- define cadence
- define thresholds and update rules
- define belief update implications
- state confidence in each signal under the current uncertainty mode
- clarify whether each signal changes belief only or should also change action

This step should not:
- confuse signals with evidence hierarchy
- skip decision implications
- create monitoring noise with no update rule
- mistake narrative commentary for a diagnostic signal

Working rules:
- Use the provided topic and current state, especially the current questions, scenarios, and evidence plan, as the basis for signal design.
- If the raw topic and the normalized current state differ in wording or precision, prefer the normalized routing and current-state framing and use the raw topic as background context only.
- Separate evidence from signals, and signals from decisions.
- Distinguish narrative from diagnostic signals.
- Prefer signals that can meaningfully change branch weights, confidence, monitoring, or action.
- Make update logic explicit enough that someone could actually use the signals.

Input topic:
{{topic}}

{{current_state}}

{{active_steering}}

For each high-value question, determine:
- the linked question
- the observable signal
- the preferred evidence source
- the backup evidence source
- the cadence
- the thresholds
- the update rules
- the belief update implications
- confidence in the signal under the current uncertainty mode
- whether the signal changes belief only or should also change action

Where relevant, the update logic should capture whether the signal changes:
- action
- timing
- sizing
- staging
- hedge, exit, or kill criteria

Output requirements:
- Produce a result fully consistent with the provided output schema.
- Include a set of signals that directly connect important questions to observable updates.

{{required_output}}

Quality bar:
- Prefer high-value, monitorable signals over noisy proxies.
- Do not create signals that are easy to observe but weakly diagnostic.
- Make the signal set usable for monitoring and decision updates.
