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
placeholder
```

Action frame:
- Decision context: Whether to launch a staged pilot before full rollout
- Risk tolerance: Moderate
- Time horizon: next 2 quarters

Base-case scenario logic:
- Probability logic: Most plausible if product fit is good but expansion remains capacity-constrained.
- Reversibility: highly reversible
Decision implications from the base case:
- expand only after pilot thresholds are met

Base-case branch triggers:
- pilot usage sustains after onboarding
- no major compliance blockers emerge

Alternative scenarios:
- Compliance drag stalls rollout
  Probability logic: Plausible if buyers like the product but the operating environment is slow-moving.
  Reversibility: partially reversible
  Decision implications:
  - delay expansion and narrow scope
  Branch triggers:
  - extended review requests
  - data handling objections
- Weak workflow fit
  Probability logic: Plausible if the product solves a visible but not decisive workflow pain point.
  Reversibility: highly reversible
  Decision implications:
  - stop rollout and rework product
  Branch triggers:
  - low repeat usage
  - limited operational impact

Evidence plan:
Evidence hierarchy:
- pilot operating metrics
- workflow retention behavior
- customer implementation evidence
- compliance review outcomes
- executive narrative

Preferred source types:
- pilot usage logs
- workflow outcome metrics
- implementation reports

Conflict-resolution rules:
- Prefer observed workflow behavior over executive interpretation
- Treat single-customer anecdotes as weak unless supported by metrics

Question-to-evidence mapping:
- What milestone should gate moving from pilot to broader rollout?
  Preferred sources:
  - pilot usage logs
  - workflow outcome metrics
  Backup sources:
  - customer interviews

Uncertainty map:
Reducible unknowns:
- pilot usage quality
- implementation cycle time

Partially reducible unknowns:
- transferability of one pilot to a broader segment

Irreducible uncertainties:
- future policy shifts at customer institutions

Task-material uncertainties:
- whether pilot success will be strong and repeatable enough to justify expansion

[CONDITIONAL condition="Use this only if unresolved killer questions should explicitly gate action."]
Top killer questions:
- What milestone should gate moving from pilot to broader rollout?
  Why it matters: This determines whether the staged commitment logic is real or performative.
- Which bottleneck is more binding: compliance review or implementation bandwidth?
  Why it matters: The main bottleneck determines whether speed comes from policy work or operational narrowing.
- What operating metrics most credibly show workflow improvement during the pilot?
  Why it matters: These metrics determine what evidence should trigger expansion rather than optimism.
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if the exact action scope or inherited scope discipline is still ambiguous."]
Boundary anchors:
- Exact object of analysis: staged launch of Atlas forecasting into regulated healthcare operations teams
Scope assumptions:
- The first release is pilot-only and feature-limited.
- The launch decision is evaluated separately from full enterprise expansion.
[/CONDITIONAL]

[CONDITIONAL condition="Use this only if the action rule depends on mechanism details, bottlenecks, or decisive variables rather than scenario summaries alone."]
Mechanism details:
Killer variables:
- measured workflow improvement
- time-to-compliance approval
- pilot retention

Bottlenecks:
- compliance review capacity
- implementation bandwidth

Causal mechanism:
- Pilot adoption quality determines whether credible case studies emerge
- Credible case studies shape commercial confidence and expansion budget
- Compliance friction can delay or narrow the rollout path
[/CONDITIONAL]

## Stage Guidance
### Because this is a `Decide` task, follow this guidance with stated importance:
Relevance: Primary
- This is a core stage for the adapter and should make action thresholds explicit.
### Because this problem sits in `Company / Product Strategy`, follow this guidance with stated importance:
Relevance: Modulating
- Shapes what action means: resource allocation, sequencing, investment, pricing, or GTM change.
### Because the deliverable is `Decision Memo`, follow this guidance with stated importance:
Relevance: Modulating
- Keep this stage consistent with the eventual `Decision Memo` deliverable.
- Let the deliverable shape influence emphasis and prioritization, not final section formatting.
- Do not drift into writing the final artifact in this stage.
### Because the preferred evidence mode is `Operating-Metric-First`, follow this guidance with stated importance:
Relevance: Modulating
- Can support action when operating evidence is stronger than narrative but still incomplete.
### Because the dominant uncertainty is `Hidden-Variable Dominated`, follow this guidance with stated importance:
Relevance: Primary
- Pushes action logic toward staging, reversibility, and wider uncertainty bands.
### Because the action problem is `Optionality / Staged Commitment`, follow this guidance with stated importance:
Relevance: Primary
- Core stage: must define probe, scale, kill, and learning-before-commitment logic.

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
