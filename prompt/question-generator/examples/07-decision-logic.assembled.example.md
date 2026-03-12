# 07-Decision-Logic Assembled Prompt Example

Assumed routing for this example:
- Primary task: Decide
- Primary domain: Investing / Markets
- Primary output mode: Decision Memo
- Primary evidence mode: Market-Tape / Price-Action-First
- Primary uncertainty mode: Hidden-Variable Dominated
- Primary decision mode: Portfolio Construction

---

You are the Decision Logic stage worker for the modular question generator.

Your job in this stage is to convert the accumulated research into action logic.
You are not re-routing the problem. You are not redoing upstream analysis unless
a core assumption in the provided state is internally inconsistent.

You must produce only the state updates for:
- `decision_logic`
- `synthesis`

You must stay consistent with the modular generator source of truth and the
current routed modules included below.

## Stage Contract

```json
{
  "stage": "decision_logic",
  "reads_required": ["routing", "scenarios", "evidence_planning"],
  "reads_optional": [
    {
      "stage": "structure",
      "kind": "situation",
      "when": [
        "action depends on specific bottlenecks or mechanism details",
        "scenario summaries are too compressed",
        "portfolio or adversarial logic needs more structural detail"
      ]
    },
    {
      "stage": "question_generation",
      "kind": "situation",
      "when": [
        "killer questions are directly tied to action gating"
      ]
    },
    {
      "stage": "boundary",
      "kind": "situation",
      "when": [
        "action scope is still ambiguous"
      ]
    }
  ],
  "depends_on": ["task", "domain", "output_mode", "evidence_mode", "uncertainty_mode", "decision_mode"],
  "writes": ["decision_logic", "synthesis"],
  "output_format": "json_state_update",
  "feedback": {
    "supported": false
  }
}
```

## Current Shared State

```json
{
  "routing": {
    "primary_task": "Decide",
    "secondary_task": "Monitor",
    "task_rationale": "The user needs an action recommendation now, but the position will also require ongoing monitoring.",
    "primary_domain": "Investing / Markets",
    "secondary_domain": "",
    "domain_rationale": "The problem is whether to allocate capital to a public equity under uncertainty.",
    "primary_output_mode": "Decision Memo",
    "secondary_output_mode": "",
    "output_mode_rationale": "The user needs an action-oriented answer, not just a research map.",
    "primary_evidence_mode": "Market-Tape / Price-Action-First",
    "secondary_evidence_mode": "Operating-Metric-First",
    "evidence_mode_rationale": "Positioning, revisions, and market-implied expectations matter immediately, with operating metrics as a cross-check.",
    "primary_uncertainty_mode": "Hidden-Variable Dominated",
    "secondary_uncertainty_mode": "",
    "uncertainty_mode_rationale": "True demand durability and hyperscaler capex elasticity are only partially visible ahead of the next print.",
    "primary_decision_mode": "Portfolio Construction",
    "secondary_decision_mode": "",
    "decision_mode_rationale": "The real question is not whether the idea is good in isolation, but whether it improves the existing portfolio.",
    "time_horizon": "1-2 quarters",
    "unit_of_analysis": "portfolio allocation to a single equity position",
    "decision_context": "Whether to increase portfolio weight in NVIDIA ahead of earnings.",
    "key_assumptions": [
      "The portfolio already has meaningful AI infrastructure exposure.",
      "A new allocation would compete with other semiconductor and megacap positions.",
      "Short-term expectation risk matters as much as medium-term fundamental quality."
    ]
  },
  "structure": {
    "primary_actors": ["NVIDIA", "hyperscalers", "competitors", "buy-side investors"],
    "secondary_actors": ["suppliers", "enterprise customers", "sell-side analysts"],
    "structural_actors_or_forces": ["AI capex cycle", "valuation regime", "portfolio crowding", "supply availability"],
    "decisive_stakeholders": [
      {
        "name": "NVIDIA management",
        "actor_type": "company",
        "can_change": ["guidance", "capital allocation signaling", "narrative on demand durability"],
        "influence": "direct",
        "role_tags": ["causal", "signal-relevant"],
        "primary_objective": "sustain revenue growth and preserve premium valuation support",
        "secondary_objectives": ["expand supply", "maintain customer concentration balance"],
        "public_objectives": ["serve customer demand", "build long-term platform leadership"],
        "revealed_objectives": ["defend growth narrative", "support conviction in capex supercycle"],
        "incentive_alignment": "mostly aligned short and medium term",
        "internal_factions": [],
        "constraints": {
          "political": [],
          "financial": [],
          "operational": ["supply constraints", "product transition timing"],
          "time": ["earnings cadence"],
          "institutional_legal_coalition": [],
          "practically_too_costly_actions": ["materially sandbagging guidance without signaling cost"]
        }
      },
      {
        "name": "Hyperscaler customers",
        "actor_type": "customer",
        "can_change": ["AI capex pace", "order visibility", "cluster deployment timing"],
        "influence": "direct",
        "role_tags": ["causal", "decisive"],
        "primary_objective": "convert AI infrastructure spend into platform advantage",
        "secondary_objectives": ["avoid overbuilding", "preserve returns on capital"],
        "public_objectives": ["capture AI opportunity"],
        "revealed_objectives": ["spend aggressively where demand is visible, slow where ROI is uncertain"],
        "incentive_alignment": "mixed",
        "internal_factions": ["growth teams vs finance discipline"],
        "constraints": {
          "political": [],
          "financial": ["capex budget scrutiny"],
          "operational": ["power, networking, deployment bottlenecks"],
          "time": ["procurement and deployment cycles"],
          "institutional_legal_coalition": [],
          "practically_too_costly_actions": ["sustaining uneconomic capex indefinitely"]
        }
      },
      {
        "name": "Portfolio manager",
        "actor_type": "decision-maker",
        "can_change": ["position size", "timing", "hedging", "relative allocation"],
        "influence": "direct",
        "role_tags": ["payoff-relevant", "decisive"],
        "primary_objective": "improve portfolio expected return without increasing correlated downside excessively",
        "secondary_objectives": ["preserve liquidity", "avoid crowded exposure"],
        "public_objectives": [],
        "revealed_objectives": ["find asymmetric allocation decisions"],
        "incentive_alignment": "aligned",
        "internal_factions": [],
        "constraints": {
          "political": [],
          "financial": ["risk budget"],
          "operational": ["position limits"],
          "time": ["earnings timing"],
          "institutional_legal_coalition": [],
          "practically_too_costly_actions": ["oversizing into a crowded print without hedge"]
        }
      }
    ],
    "causal_mechanism": {
      "main_mechanism": "Allocation outcome depends on whether near-term expectations are still lower than the durable earnings power implied by hyperscaler AI capex and deployment throughput.",
      "intermediate_links": [
        "Hyperscaler AI demand drives order visibility",
        "Order visibility drives revenue/guidance confidence",
        "Revenue/guidance confidence drives expectation revision path",
        "Expectation revision path interacts with valuation and crowding"
      ],
      "weak_links": [
        "true ROI of customer AI spend",
        "sustainability of current capex intensity",
        "ability of market to absorb already-high expectations"
      ],
      "feedback_loops": [
        "strong prints reinforce capex confidence and valuation support",
        "crowded positioning can amplify downside if evidence disappoints"
      ],
      "fragile_assumptions": [
        "AI spend remains economically justified beyond current enthusiasm",
        "current valuation does not already discount most of the upside"
      ]
    },
    "killer_variables": [
      "hyperscaler capex durability",
      "guidance credibility",
      "expectation gap vs consensus",
      "portfolio correlation to existing AI exposure"
    ],
    "bottlenecks": [
      "deployment throughput",
      "power and networking constraints",
      "valuation compression risk",
      "crowded positioning"
    ],
    "threshold_variables": [
      "guidance above buyside expectations",
      "evidence of sustained customer ROI",
      "portfolio AI concentration limit"
    ],
    "scarce_resources": [
      "risk budget",
      "uncorrelated exposure slots"
    ]
  },
  "scenarios": [
    {
      "name": "Beat and raise, expectations still too low",
      "scenario_type": "bull",
      "description": "Demand and guidance remain strong enough to push estimates higher despite elevated expectations.",
      "branch_points": ["management guidance", "hyperscaler commentary"],
      "branch_triggers": ["guidance materially above buyside whisper numbers"],
      "reversible_elements": ["short-term post-print momentum"],
      "self_reinforcing_elements": ["capex confidence", "estimate revision cycle"],
      "probability_logic": "Plausible if customer capex remains constrained more by supply/deployment than by ROI skepticism.",
      "probability_estimate": "40%",
      "evidence_that_raises_probability": ["strong hyperscaler capex commentary", "stable gross margin despite scale"],
      "evidence_that_lowers_probability": ["customer optimization rhetoric", "weaker than expected guide"],
      "decision_mode_implications": ["May justify adding, but only if portfolio overlap remains tolerable."]
    },
    {
      "name": "Good business, fully priced stock",
      "scenario_type": "base",
      "description": "Fundamentals remain strong but incremental upside is limited because expectations and positioning are already rich.",
      "branch_points": ["magnitude of beat", "valuation response"],
      "branch_triggers": ["inline-to-modest beat with no major upside revision"],
      "reversible_elements": ["short-term post-print move"],
      "self_reinforcing_elements": ["multiple compression if enthusiasm fades"],
      "probability_logic": "Likely if business quality is intact but expectation gap is small.",
      "probability_estimate": "35%",
      "evidence_that_raises_probability": ["consensus already near realistic upside", "muted reaction to strong numbers"],
      "evidence_that_lowers_probability": ["large estimate revisions still needed"],
      "decision_mode_implications": ["Favors hold or modest sizing rather than aggressive add."]
    },
    {
      "name": "Expectation miss or capex durability concern",
      "scenario_type": "bear",
      "description": "Evidence emerges that demand durability or near-term monetization is weaker than the market assumed.",
      "branch_points": ["guidance tone", "customer ROI framing"],
      "branch_triggers": ["guide disappoints or customer commentary softens"],
      "reversible_elements": ["single-quarter noise if long-term thesis survives"],
      "self_reinforcing_elements": ["crowding unwind", "multiple compression"],
      "probability_logic": "Lower probability, but downside could be amplified by crowded ownership.",
      "probability_estimate": "25%",
      "evidence_that_raises_probability": ["softening orders", "optimization comments", "slower deployments"],
      "evidence_that_lowers_probability": ["clear evidence of sustained ROI and backlog visibility"],
      "decision_mode_implications": ["Argues against increasing weight pre-print without hedge."]
    }
  ],
  "questions": {
    "top_3_killer_questions": [
      {
        "id": "KQ-1",
        "question": "Is buy-side expectation still below what management can credibly guide to over the next two quarters?",
        "why_it_matters": "This determines whether there is still positive expectation gap.",
        "impact_on_final_judgment": "High",
        "uncertainty_reduction": "High",
        "observability": "Medium",
        "uncertainty_type": "partially reducible",
        "decision_change_types": ["action", "timing", "sizing"]
      },
      {
        "id": "KQ-2",
        "question": "How much correlated AI infrastructure exposure is already embedded in the portfolio?",
        "why_it_matters": "The right decision depends on marginal portfolio contribution, not standalone attractiveness.",
        "impact_on_final_judgment": "High",
        "uncertainty_reduction": "High",
        "observability": "High",
        "uncertainty_type": "reducible",
        "decision_change_types": ["action", "sizing", "hedging"]
      },
      {
        "id": "KQ-3",
        "question": "Are signs of hyperscaler capex fatigue still hidden, or already emerging in proxies?",
        "why_it_matters": "This determines whether current demand durability is more fragile than reported numbers imply.",
        "impact_on_final_judgment": "High",
        "uncertainty_reduction": "Medium",
        "observability": "Medium",
        "uncertainty_type": "partially reducible",
        "decision_change_types": ["timing", "sizing", "monitoring"]
      }
    ]
  },
  "evidence_plan": {
    "preferred_source_types": [
      "price action and relative reaction",
      "options skew",
      "estimate revisions",
      "company guidance",
      "hyperscaler capex commentary"
    ],
    "backup_source_types": [
      "channel checks",
      "supply-chain commentary",
      "usage and deployment proxies"
    ],
    "conflict_resolution_rules": [
      "Prefer revealed behavior over narrative.",
      "Prefer sustained revision patterns over one-off commentary.",
      "Treat anecdotal demand comments skeptically unless multiple proxies align."
    ],
    "question_to_evidence_map": [
      {
        "question_id": "KQ-1",
        "preferred_sources": ["management guidance", "estimate revisions", "post-earnings reaction"],
        "backup_sources": ["options-implied move", "sell-side expectation surveys"],
        "proof_target": "Determine whether expectation gap remains positive.",
        "what_would_resolve_conflict": ["clearer guide range", "consistent analyst revision wave"]
      },
      {
        "question_id": "KQ-2",
        "preferred_sources": ["portfolio holdings", "factor exposure report"],
        "backup_sources": ["sector exposure proxy", "correlation matrix"],
        "proof_target": "Determine marginal portfolio contribution and overlap.",
        "what_would_resolve_conflict": ["updated portfolio risk decomposition"]
      }
    ]
  },
  "uncertainty_map": {
    "reducible_unknowns": [
      "portfolio overlap",
      "consensus vs whisper expectation gap"
    ],
    "partially_reducible_unknowns": [
      "true durability of customer AI capex",
      "extent of hidden deployment bottlenecks"
    ],
    "irreducible_uncertainties": [
      "short-term market reaction path after earnings"
    ],
    "task_relevant_unknowns": [
      "expectation gap",
      "portfolio correlation",
      "capex durability proxies"
    ],
    "dominant_uncertainty": "Whether strong fundamentals are still underpriced on a portfolio-adjusted basis."
  }
}
```

## Active Task Module

```md
ROUTER C — DECIDE

Prioritize:
- action relevance
- payoff asymmetry
- timing
- triggers
- failure modes
- minimum sufficient evidence
```

## Active Domain Module

```md
DOMAIN ADAPTER — INVESTING / MARKETS

Typical ontology:
- assets
- securities
- sectors
- management teams
- customers
- competitors
- investors
- regulators
- market expectations
- positioning
- catalysts
- valuation regimes

Typical bottlenecks:
- growth durability
- margins
- liquidity
- customer budgets
- pricing power
- adoption rates
- multiple compression
- crowding

Typical signals:
- earnings/guidance
- bookings/RPO/NRR/churn
- revisions
- flows
- spreads
- usage indicators
- management commentary
- capex trends
- options skew
```

## Active Uncertainty Module

```md
UNCERTAINTY MODE — HIDDEN-VARIABLE DOMINATED

Research behavior:
- search for proxies
- triangulate aggressively
- widen the hypothesis set

Risk:
- overfitting to indirect clues
```

## Active Decision Module

```md
DECISION MODE — PORTFOLIO CONSTRUCTION

Use when:
- the choice is allocation across multiple opportunities
- diversification, concentration, and correlation matter
- the right question is marginal contribution, not standalone attractiveness

Research behavior:
- change unit of analysis from single idea to portfolio role
- identify common drivers and shared failure modes
- ask what this adds, replaces, hedges, or duplicates

Key questions:
- What role does this position play?
- What exposures does it share with the rest of the portfolio?
- Where is correlation hidden?
- What failure modes are duplicated?
- What is the marginal contribution to expected return and drawdown?

Action logic:
- standalone quality is insufficient
- evaluate fit, covariance, liquidity, and concentration

Monitoring style:
- portfolio-level and position-level

Failure mode:
- false diversification
```

## Active Output Mode Module

```md
OUTPUT MODE — DECISION MEMO

Required sections:
1. Routing
2. Decision to Be Made
3. Recommendation
4. Decision Mode and Why It Fits
5. Why Now / Why Not Now
6. What Must Be True
7. Key Risks / Failure Modes
8. Evidence Standard Required to Act
9. Uncertainty That Can Be Reduced Before Acting
10. Uncertainty That Must Be Accepted
11. Reversibility / Sizing / Staging Logic
12. Triggers
13. Top 3 Killer Questions
14. Evidence Plan
15. What to Monitor Next
16. What Would Change the Conclusion
```

## Decision Logic Instructions

Using the state and active modules above, convert the current analysis into
action logic.

Prioritize:
- action relevance over descriptive completeness
- portfolio role over standalone idea quality
- minimum sufficient evidence over impossible certainty
- reversibility, sizing, and timing discipline
- what would actually change the decision

You must determine:
- what must be known before acting
- what can be learned after acting
- the appropriate evidence threshold
- reversibility logic
- sizing logic
- staging logic
- hedge, exit, and kill criteria
- concrete triggers
- what must be true
- key risks and failure modes

You must also produce a concise synthesis that can later support rendering into
the selected output mode.

Do not:
- reopen routing casually
- ignore portfolio overlap
- confuse business quality with portfolio fit
- recommend aggressive action without stating the evidence threshold
- invent facts not supported by the provided state

## Output Requirements

Return a JSON object containing only:
- `decision_logic`
- `synthesis`

The output should be directly mergeable into the shared state.
