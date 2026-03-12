# Shared State Field Reference

This document explains the fields in:
- `/Users/canzheng/Work/sandbox/truth-seek/prompt/question-generator/contracts/shared_state_schema.json`

It is the human-readable companion to the schema. Use it when:
- authoring or reviewing contracts
- building the orchestrator
- debugging stage output shape
- understanding what each state field is meant to represent

The shared state is durable pre-render workflow state. It should capture
analysis that downstream stages need to consume, not presentation-only detail.

## Reading Guide

## `topic`

Meaning:
- The raw topic or problem statement as provided to the workflow.
- This is the least-normalized description of the problem.

Notes:
- Keep the original wording here even if `routing.question` later becomes a
  cleaner normalized version of the ask.

## `routing`

Meaning:
- The normalized problem frame for the run.
- This section does two jobs:
  - formalize the user input into a structured ask
  - store the routed values that resolve adapter and output-mode files

### `routing.question`

Meaning:
- The normalized research or decision question for the run.

Notes:
- This is usually more precise than `topic`.

### `routing.explicit_constraints`

Meaning:
- Constraints stated by the user or inferred as fixed boundaries for the run.

Examples:
- time limits
- source restrictions
- “focus on the next 1-3 months”

### `routing.desired_output`

Meaning:
- The user’s requested output framing before it is normalized into an
  `output_mode`.

Notes:
- This preserves the request wording even if the routed output mode is more
  canonical.

### `routing.risk_tolerance`

Meaning:
- The user’s explicit or inferred tolerance for acting under uncertainty.

### `routing.decision_context`

Meaning:
- The concrete action frame if the problem has a decision component.

Examples:
- whether to allocate
- whether to delay
- whether to escalate

Notes:
- This may be empty for pure explanation or monitoring asks.

### `routing.task`

Meaning:
- Primary task classification.

Allowed family:
- Explain
- Predict
- Decide
- Monitor
- Design / Influence

### `routing.secondary_task`

Meaning:
- Secondary task classification when a second task meaningfully shapes the run.

Notes:
- Optional. Omit when one task is sufficient.

### `routing.domain`

Meaning:
- Primary domain classification for the world the problem lives in.

Examples:
- Geopolitics / War
- Investing / Markets
- Policy / Regulation

### `routing.secondary_domain`

Meaning:
- Secondary domain classification when the problem spans two ontologies.

Notes:
- Optional. Omit when one domain is sufficient.

### `routing.output_mode`

Meaning:
- Primary output mode classification.

Examples:
- Research Memo
- Decision Memo
- Scenario Tree
- Monitoring Dashboard

### `routing.secondary_output_mode`

Meaning:
- Secondary output mode classification if the deliverable needs a second shape.

Notes:
- Optional. Omit when one output mode is sufficient.

### `routing.evidence_mode`

Meaning:
- Primary proof-style classification.

Examples:
- Primary-Source-Heavy
- Market-Tape / Price-Action-First
- Policy / Legal-Text-First

### `routing.secondary_evidence_mode`

Meaning:
- Secondary evidence mode if a second proof style materially matters.

Notes:
- Optional. Omit when one evidence mode is sufficient.

### `routing.uncertainty_mode`

Meaning:
- Primary uncertainty classification describing what kind of ignorance dominates
  the case.

Examples:
- Hidden-Variable Dominated
- Adversarial / Deception Dominated
- Regime-Shift Dominated

### `routing.secondary_uncertainty_mode`

Meaning:
- Secondary uncertainty mode if a second uncertainty pattern matters enough to
  shape the workflow.

Notes:
- Optional. Omit when one uncertainty pattern is sufficient.

### `routing.decision_mode`

Meaning:
- Primary action-problem classification.

Examples:
- Latent / No Immediate Commitment
- One-Shot High-Stakes
- Portfolio Construction
- Optionality / Staged Commitment

### `routing.secondary_decision_mode`

Meaning:
- Secondary decision mode when a second action pattern matters.

Notes:
- Optional. Omit when one decision mode is sufficient.

### `routing.classification_rationales`

Meaning:
- Per-axis explanation of why each primary or secondary classification fits.

Fields:
- `task`
- `secondary_task`
- `domain`
- `secondary_domain`
- `output_mode`
- `secondary_output_mode`
- `evidence_mode`
- `secondary_evidence_mode`
- `uncertainty_mode`
- `secondary_uncertainty_mode`
- `decision_mode`
- `secondary_decision_mode`

Notes:
- These are useful for auditability and for downstream stages that need to know
  why a route was chosen, not just what was chosen.
- Primary rationale fields are expected.
- Secondary rationale fields are optional and only need to be present when the
  corresponding `secondary_*` route is present.

### `routing.time_horizon`

Meaning:
- The effective time frame for the run after normalization.

Used by:
- `Boundary`
- `Scenarios`
- `Monitoring`
- `Render`

### `routing.unit_of_analysis`

Meaning:
- The object being analyzed.

Examples:
- one conflict
- one portfolio decision
- one product rollout

### `routing.assumptions`

Meaning:
- Explicit assumptions made during routing to make the problem tractable or
  decision-useful.

## `boundary`

Meaning:
- Defines what is inside the analysis frame and what is outside.

### `boundary.exact_object_of_analysis`

Meaning:
- The precise thing being analyzed.

Examples:
- “short-term escalation path of an Iran-Israel war”
- “marginal portfolio decision on NVDA into earnings”

### `boundary.core_system`

Meaning:
- The main system whose behavior the workflow is trying to understand.

### `boundary.adjacent_systems`

Meaning:
- Neighboring systems that materially affect the core system and should remain
  in view.

### `boundary.out_of_scope_factors`

Meaning:
- Factors intentionally excluded from direct analysis.

Notes:
- This helps prevent scope creep and later source drift.

### `boundary.scope_assumptions`

Meaning:
- Assumptions required to keep the boundary stable.

## `structure`

Meaning:
- The working model of how the system operates.

### `structure.stakeholders`

Meaning:
- The relevant actors, institutions, or forces in the system.

### `structure.decisive_stakeholders`

Meaning:
- The subset of stakeholders whose choices or constraints can materially shift
  outcomes.

Notes:
- This field is richer than the plain stakeholder list because later stages
  often care about decisive actors specifically.

### `structure.incentives`

Meaning:
- The motives, rewards, and penalties shaping actor behavior.

### `structure.constraints`

Meaning:
- The limits that bind action.

Examples:
- operational limits
- political limits
- time limits
- capital limits

### `structure.causal_mechanism`

Meaning:
- The working chain of cause and effect that explains how the system moves.

### `structure.killer_variables`

Meaning:
- Variables that could dominate the answer if they move or resolve differently
  than expected.

### `structure.bottlenecks`

Meaning:
- Constraints or chokepoints that govern system throughput or change.

### `structure.threshold_variables`

Meaning:
- Variables whose behavior matters mainly when they cross a meaningful
  threshold.

### `structure.scarce_resources`

Meaning:
- The limited resources that determine competition, sequencing, or failure.

## `scenarios`

Meaning:
- The structured branch map of plausible paths forward or alternative paths of
  explanation.

### `scenarios.base_case`

Meaning:
- The default or most central path used as the anchor branch.

Fields:
- `name`: short scenario label
- `summary`: compact description of the path
- `branch_points`: structural turning points that define the branch
- `branch_triggers`: observable or inferable triggers that push the system into
  this branch
- `reversibility`: whether the branch is easy to reverse, hard to reverse, or
  self-reinforcing
- `probability_logic`: rough explanation of why this branch is plausible
- `decision_mode_implications`: action implications if this branch plays out

### `scenarios.alternative_scenarios`

Meaning:
- Non-base branches that compete with the base case.

Item shape:
- same fields as `base_case`

Notes:
- The schema stores alternatives as a list because scenario count is variable.

## `questions`

Meaning:
- The research agenda for the workflow.
- Questions are grouped by purpose so downstream stages can use the right
  subset.

Question buckets:
- `clarifying`
- `structural`
- `stakeholder`
- `evidence`
- `task_specific`
- `domain_specific`
- `output_mode_specific`
- `evidence_mode_specific`
- `uncertainty_mode_specific`
- `decision_mode_specific`
- `top_killer_questions`

All question objects share the same fields.

### `question`

Meaning:
- The actual question being asked.

### `why_it_matters`

Meaning:
- Why the question matters for the workflow.

### `impact_on_final_judgment`

Meaning:
- How the answer would change the final conclusion, branch ranking, or action.

### `uncertainty_reduction`

Meaning:
- What uncertainty this question reduces and how materially it helps.

### `observability`

Meaning:
- Whether and how the answer can be observed or inferred.

### `reducibility`

Meaning:
- Whether the uncertainty behind the question is reducible, partially
  reducible, or largely irreducible.

### `decision_change_types`

Meaning:
- The kinds of actions or judgments this question could change.

Examples:
- sizing
- timing
- staging
- branch weighting

### `questions.top_killer_questions`

Meaning:
- The highest-value questions whose answers would most change the result.

Notes:
- This is a prioritized subset, not a different schema.

## `evidence_plan`

Meaning:
- The proof strategy for answering the generated questions.

### `evidence_plan.evidence_hierarchy`

Meaning:
- Ordered description of what kinds of evidence should be trusted most.

### `evidence_plan.preferred_source_types`

Meaning:
- Source families that best fit the selected evidence mode and problem.

### `evidence_plan.backup_source_types`

Meaning:
- Secondary or fallback source families when preferred sources are unavailable
  or conflicting.

### `evidence_plan.conflict_resolution_rules`

Meaning:
- Rules for handling disagreement across sources or evidence types.

### `evidence_plan.question_to_evidence_mapping`

Meaning:
- Direct mapping from important questions to preferred and backup sources.

Item fields:
- `question`
- `preferred_sources`
- `backup_sources`

## `uncertainty_map`

Meaning:
- Structured view of what uncertainty can and cannot be reduced.

### `uncertainty_map.reducible_unknowns`

Meaning:
- Unknowns that can plausibly be narrowed through research or observation.

### `uncertainty_map.partially_reducible_unknowns`

Meaning:
- Unknowns that can be narrowed but not resolved cleanly before action.

### `uncertainty_map.irreducible_uncertainties`

Meaning:
- Unknowns that must largely be borne rather than eliminated.

### `uncertainty_map.task_material_uncertainties`

Meaning:
- The uncertainties that actually matter for the task, rather than every
  uncertainty in the problem.

## `decision_logic`

Meaning:
- The operational action logic derived from the current state.

### `decision_logic.must_know_before_action`

Meaning:
- Facts or judgments that should be known before acting.

### `decision_logic.can_learn_after_action`

Meaning:
- Things that do not need to be resolved before the initial move.

### `decision_logic.appropriate_evidence_threshold`

Meaning:
- The standard of proof required for action in this case.

### `decision_logic.reversibility_logic`

Meaning:
- How reversibility should affect action timing and commitment size.

### `decision_logic.sizing_logic`

Meaning:
- How the action should be sized under the current evidence and uncertainty.

### `decision_logic.staging_logic`

Meaning:
- Whether the action should happen in phases and what those phases imply.

### `decision_logic.hedge_exit_kill_criteria`

Meaning:
- Conditions that justify hedging, exiting, or killing the decision path.

### `decision_logic.triggers`

Meaning:
- Signals or thresholds that should trigger action, scaling, delay, or stop.

## `synthesis`

Meaning:
- Concise conclusion framing that sits above detailed action logic.

### `synthesis.recommendation_or_action_frame`

Meaning:
- The core recommendation or action orientation.

### `synthesis.why_now_or_why_not_now`

Meaning:
- Time-sensitive reasoning for acting now, waiting, or staying latent.

### `synthesis.what_must_be_true`

Meaning:
- Conditions that must hold for the recommendation to remain valid.

### `synthesis.key_risks_and_failure_modes`

Meaning:
- The main ways the current recommendation can fail.

## `signals`

Meaning:
- The observable signals that connect questions and scenarios to update logic.

Each signal item has these fields.

### `signal`

Meaning:
- The actual thing to watch.

### `linked_question`

Meaning:
- The question this signal helps answer.

### `preferred_evidence_source`

Meaning:
- Best source for observing this signal.

### `backup_evidence_source`

Meaning:
- Fallback source if the preferred one is unavailable or noisy.

### `cadence`

Meaning:
- How often the signal should be checked.

### `thresholds`

Meaning:
- Quantitative or qualitative thresholds that make the signal meaningful.

### `update_rules`

Meaning:
- How the signal should change beliefs when it moves.

### `belief_update_implications`

Meaning:
- What shift in scenario weights, confidence, or narrative should follow.

### `confidence_under_current_uncertainty_mode`

Meaning:
- How much confidence should be placed in the signal under the routed
  uncertainty mode.

### `changes_action_vs_belief`

Meaning:
- Whether the signal only changes belief or should also change action.

## `monitoring`

Meaning:
- The operational watch layer built from the signal design.

### `monitoring.what_to_watch`

Meaning:
- The main watch items for ongoing tracking.

Item fields:
- `item`: the thing to watch
- `why_it_matters`: why this item matters
- `evidence_source_preference`: preferred sources for tracking it
- `escalation_triggers`: conditions that should raise urgency or review level
- `action_triggers`: conditions that should change action directly
- `noise_to_ignore`: misleading or low-signal behavior that should not trigger
  overreaction
- `update_cadence`: expected review frequency

### `monitoring.signal_most_reducing_dominant_uncertainty`

Meaning:
- The single signal most likely to reduce the main remaining uncertainty.

### `monitoring.signal_most_likely_to_change_action`

Meaning:
- The single signal most likely to change what should be done.

### `monitoring.what_to_monitor_next`

Meaning:
- Additional future watch items or next monitoring priorities once the current
  watch layer is in place.

## Design Notes

Why some fields are richer than older versions of the state:
- This schema was expanded so downstream stages could consume durable outputs
  directly rather than relying on deleted guidance files or reconstructing
  upstream work.

Why some presentation detail is absent:
- Output-mode-specific final formatting belongs in output-mode modules and the
  `Render` stage, not in pre-render state.

Why `Render` has no state section:
- `Render` is a terminal formatting stage.
- It consumes the accumulated state and produces a deliverable, but it does not
  write new analysis state back into the shared state file.
