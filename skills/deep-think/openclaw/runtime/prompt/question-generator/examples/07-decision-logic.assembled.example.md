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
- ignore the stage guidance when setting evidence thresholds
- hide behind generic balance on decision tasks
- drift into final deliverable formatting

Working rules:
- Use the topic plus the current decision context, scenario logic, evidence plan, and uncertainty map as the basis for decision logic.
- If the raw topic and the normalized framing differ in wording or precision, prefer the normalized framing and use the raw topic as background context only.
- Distinguish reducible uncertainty from uncertainty that must simply be borne.
- Be explicit about what would change the conclusion.
- Be explicit about when reversibility, staging, or diversification should lower commitment and when evidence strength should raise it.
- If the task is action-oriented, do not hide behind generic balance.
- For any input marked `[CONDITIONAL]`, use it only if you strongly believe the stated condition is met for the current task.
- If the condition is not clearly met, ignore that input entirely.
- Do not force conditional inputs into the analysis just because they are provided.

Input topic:
```text
Should we add to NVDA ahead of earnings?
```

Action frame:
- Decision context: 
- Risk tolerance: 
- Time horizon: 

Base-case scenario logic:
- Probability logic: 
- Reversibility: 
Decision implications from the base case:

Base-case branch triggers:

Alternative scenarios:

Evidence plan:
Evidence hierarchy:
- guidance
- revisions

Preferred source types:

Conflict-resolution rules:

Question-to-evidence mapping:

Uncertainty map:
Reducible unknowns:

Partially reducible unknowns:

Irreducible uncertainties:
- management tone

Task-material uncertainties:

[CONDITIONAL condition="Use this only if unresolved killer questions should explicitly gate action."]
Top killer questions:
- Is demand pull-forward?
  Why it matters: 
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if the exact action scope or inherited scope discipline is still ambiguous."]
Boundary anchors:
- Exact object of analysis: 
Scope assumptions:
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if the action rule depends on mechanism details, bottlenecks, or decisive variables rather than scenario summaries alone."]
Mechanism details:
Killer variables:

Bottlenecks:
- datacenter demand durability

Causal mechanism:
[/CONDITIONAL]

## Stage Guidance
Each guidance item includes an importance label that indicates how strongly it should shape the result of this stage.
### Because the dominant uncertainty is `Hidden-Variable Dominated`, follow this guidance:
Important: Pushes action logic toward staging, reversibility, and wider uncertainty bands.
### Because the action problem is `Portfolio Construction`, follow this guidance:
Important: Core stage: must define sizing, diversification, hedging, and substitution logic.
### Because this is a `Decide` task, follow this guidance:
[CONDITIONAL condition="Use this only if the task framing materially changes the action bar."]
Important: This is a core stage for the adapter and should make action thresholds explicit.
[/CONDITIONAL]
### Because this problem sits in `Investing / Markets`, follow this guidance:
[CONDITIONAL condition="Use this only if domain-specific action logic should shape timing, sizing, or hedging."]
Moderate: Shapes what action means: sizing, timing, hedge, add, trim, or avoid.
[/CONDITIONAL]
### Because the preferred evidence mode is `Market-Tape / Price-Action-First`, follow this guidance:
[CONDITIONAL condition="Use this only if the preferred proof style should change commitment thresholds."]
Moderate: Can justify action on tape confirmation even when direct evidence is incomplete.
[/CONDITIONAL]

Decision implications must include:
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
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "$id": "state-sections/decision_logic.schema.json",
      "title": "Decision Logic",
      "type": "object",
      "required": [
        "must_know_before_action",
        "can_learn_after_action",
        "appropriate_evidence_threshold",
        "reversibility_logic",
        "sizing_logic",
        "staging_logic",
        "hedge_exit_kill_criteria",
        "triggers"
      ],
      "properties": {
        "must_know_before_action": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "can_learn_after_action": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "appropriate_evidence_threshold": {
          "type": "string"
        },
        "reversibility_logic": {
          "type": "string"
        },
        "sizing_logic": {
          "type": "string"
        },
        "staging_logic": {
          "type": "string"
        },
        "hedge_exit_kill_criteria": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "triggers": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      },
      "additionalProperties": false
    },
    "synthesis": {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "$id": "state-sections/synthesis.schema.json",
      "title": "Synthesis",
      "type": "object",
      "required": [
        "recommendation_or_action_frame",
        "why_now_or_why_not_now",
        "what_must_be_true",
        "key_risks_and_failure_modes"
      ],
      "properties": {
        "recommendation_or_action_frame": {
          "type": "string"
        },
        "why_now_or_why_not_now": {
          "type": "string"
        },
        "what_must_be_true": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "key_risks_and_failure_modes": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

Quality bar:
- Make the decision logic operational rather than philosophical.
- Tie action guidance to the current uncertainty and the stage guidance.
- Be direct about what should happen, what should wait, and why.