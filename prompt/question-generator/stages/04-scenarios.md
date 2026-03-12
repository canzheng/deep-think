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
- Use the provided topic and current state, especially structure, as the basis for scenario design.
- If the raw topic and the normalized current state differ in wording or precision, prefer the normalized routing and current-state framing and use the raw topic as background context only.
- Build scenarios from actor choices, causal mechanisms, constraints, and threshold variables.
- Prefer a small number of meaningful branches over many shallow ones.
- Make each scenario meaningfully distinct in logic, not just tone.
- Include only scenarios that could materially change understanding, monitoring, or action.

Input topic:
{{topic}}

{{current_state}}

{{active_steering}}

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

{{required_output}}

Quality bar:
- Make branches structurally meaningful, not cosmetically different.
- Do not confuse what is likely with what is merely easy to describe.
- Make the scenarios useful for later questions, signals, and decisions.
