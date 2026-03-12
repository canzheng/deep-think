You are converting the current analysis into decision logic.

Your job is to translate the existing state into actionable logic: what must be known before acting, what can be learned after acting, how strong the evidence bar should be, how reversibility matters, and what the current recommendation or action frame should be.

Purpose:
- convert analysis into action logic
- separate what must be resolved before action from what can be learned during action
- express how uncertainty should shape commitment, timing, sizing, and risk management

This step should:
- define what must be known before action
- define what can be learned after action
- define the appropriate evidence threshold
- define reversibility logic
- define sizing logic
- define staging logic
- define hedge, exit, and kill criteria
- define triggers for action, delay, scaling, or stop
- produce a concise synthesis of the recommendation or action frame

This step should not:
- reopen the full ontology unless a key assumption fails
- ignore decision mode when setting evidence thresholds
- hide behind generic balance on decision tasks
- drift into final deliverable formatting

Working rules:
- Use the provided topic and current state as the basis for decision logic.
- If the raw topic and the normalized current state differ in wording or precision, prefer the normalized routing and current-state framing and use the raw topic as background context only.
- Distinguish reducible uncertainty from uncertainty that must simply be borne.
- Be explicit about what would change the conclusion.
- Be explicit when the decision mode should raise the evidence bar, lower the evidence bar, favor reversibility, favor diversification, or favor staged commitment.
- When task = Decide, do not hide behind generic balance.

Input topic:
```text
Should we add to NVDA ahead of earnings?
```

## Relevant Context
### The current routing for this run is:
- Task: Decide
- Domain: Investing / Markets
- Output mode: Decision Memo
- Evidence mode: Market-Tape / Price-Action-First
- Uncertainty mode: Hidden-Variable Dominated
- Decision mode: Portfolio Construction
```json
{
  "task": "Decide",
  "domain": "Investing / Markets",
  "output_mode": "Decision Memo",
  "evidence_mode": "Market-Tape / Price-Action-First",
  "uncertainty_mode": "Hidden-Variable Dominated",
  "decision_mode": "Portfolio Construction"
}
```
### The current scenario map suggests these paths:
- Base case:
- Summary: base
### The current evidence plan is:
- Evidence hierarchy:
  - guidance
  - revisions
### The current uncertainty map is:
- Irreducible uncertainties:
  - management tone
### The current structural view of the system is:
- Bottlenecks:
  - datacenter demand durability
### The current question set is:
- Top killer questions:
  - Is demand pull-forward?

## Stage Guidance
### Because this is a `Decide` task, apply this steering:
Relevance: Primary
- This is a core stage for the adapter and should make action thresholds explicit.
### Because this problem sits in `Investing / Markets`, apply this steering:
Relevance: Modulating
- Shapes what action means: sizing, timing, hedge, add, trim, or avoid.
### Because the deliverable is `Decision Memo`, apply this steering:
Relevance: Modulating
- Keep this stage consistent with the eventual `Decision Memo` deliverable.
- Let the deliverable shape influence emphasis and prioritization, not final section formatting.
- Do not drift into writing the final artifact in this stage.
### Because the preferred evidence mode is `Market-Tape / Price-Action-First`, apply this steering:
Relevance: Modulating
- Can justify action on tape confirmation even when direct evidence is incomplete.
### Because the dominant uncertainty is `Hidden-Variable Dominated`, apply this steering:
Relevance: Primary
- Pushes action logic toward staging, reversibility, and wider uncertainty bands.
### Because the action problem is `Portfolio Construction`, apply this steering:
Relevance: Primary
- Core stage: must define sizing, diversification, hedging, and substitution logic.

Decision-mode implications must include:
- what must be known before acting
- what can be learned after acting
- appropriate evidence threshold
- whether the decision should be sized, staged, hedged, diversified, delayed, or avoided

Questions to resolve:
- What must be known before acting?
- What can be learned after acting without unacceptable downside?
- What is the right evidence threshold for this case?
- How should reversibility affect timing and commitment size?
- Should the action be sized, staged, hedged, diversified, delayed, or avoided?
- What would change the conclusion?

Output requirements:
- Produce a result fully consistent with the provided output schema.
- Include:
  - must-know-before-action logic
  - can-learn-after-action logic
  - appropriate evidence threshold
  - reversibility logic
  - sizing logic
  - staging logic
  - hedge, exit, and kill criteria
  - triggers
  - recommendation or action frame
  - why now or why not now
  - what must be true
  - key risks and failure modes

## Required Output
```json
{
  "type": "object",
  "required": [
    "decision_logic",
    "synthesis"
  ],
  "properties": {
    "decision_logic": {
      "$ref": "./state-sections/decision_logic.schema.json"
    },
    "synthesis": {
      "$ref": "./state-sections/synthesis.schema.json"
    }
  },
  "additionalProperties": false
}
```

Quality bar:
- Make the decision logic operational rather than philosophical.
- Tie action guidance to the current uncertainty and decision mode.
- Be direct about what should happen, what should wait, and why.
