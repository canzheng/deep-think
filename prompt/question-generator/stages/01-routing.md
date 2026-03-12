## Stage 1 - Routing

Purpose:
- classify the problem before analysis starts
- choose the active adapter set

Uses:
- routing layer from the modular source prompt
- adapter names and file paths

Should not:
- build full scenarios
- collect evidence
- make decisions
- render the final output

STEP 1 - DETERMINE PRIMARY TASK

Classify the primary task as one of:
- Explain
- Predict
- Decide
- Monitor
- Design / Influence

You may assign one secondary task if clearly needed.

Definitions:
- Explain = understand why something happened
- Predict = estimate what is likely to happen next
- Decide = determine what action should be taken under uncertainty
- Monitor = determine what signals to watch and when to update belief
- Design / Influence = determine how to shape outcomes through levers, interventions, or strategy

Also determine:
- Time horizon
- Unit of analysis
- Decision context if relevant

If unclear, infer the most decision-useful version and state assumptions explicitly.

Return:
- Primary task
- Secondary task if any
- Time horizon
- Unit of analysis
- Decision context
- Key assumptions

STEP 2 - DETERMINE PRIMARY DOMAIN

Infer the primary domain from the topic.

Choose one primary domain:
- Geopolitics / War
- Investing / Markets
- Company / Product Strategy
- Policy / Regulation
- Technology / Adoption

You may assign one secondary domain if needed.

Return:
- Primary domain
- Secondary domain if any
- Why the domain classification fits

STEP 3 - DETERMINE OUTPUT MODE

Choose one primary output mode:
- Research Memo
- Decision Memo
- Monitoring Dashboard
- Scenario Tree
- Investment Worksheet
- Deep-Research Prompt

You may choose one secondary output mode if clearly helpful.

Return:
- Primary output mode
- Secondary output mode if any
- Why this output mode fits

STEP 4 - DETERMINE EVIDENCE MODE

Choose one primary evidence mode:
- Primary-Source-Heavy
- Market-Tape / Price-Action-First
- Operating-Metric-First
- Policy / Legal-Text-First
- Expert-Network / Qualitative-First

You may assign one secondary evidence mode if clearly needed.

Return:
- Primary evidence mode
- Secondary evidence mode if any
- Why this evidence mode is appropriate

STEP 5 - DETERMINE UNCERTAINTY MODE

Choose one primary uncertainty mode:
- Known-Unknown Dominated
- Hidden-Variable Dominated
- Adversarial / Deception Dominated
- Regime-Shift Dominated
- Sparse-Data Dominated
- High-Noise / Fast-Feedback
- Slow-Feedback / Irreversible-Decision

You may assign one secondary uncertainty mode if clearly needed.

Return:
- Primary uncertainty mode
- Secondary uncertainty mode if any
- Why this uncertainty mode fits

STEP 6 - DETERMINE DECISION MODE

Choose one primary decision mode:
- Latent / No Immediate Commitment
- One-Shot High-Stakes
- Repeated Bets
- Portfolio Construction
- Optionality / Staged Commitment
- Adversarial Game
- Exploration vs Exploitation

You may assign one secondary decision mode if clearly needed.

Definitions:
- Latent / No Immediate Commitment = the user is mainly clarifying the problem or preparing for a future decision
- One-Shot High-Stakes = large downside, limited repetition, costly error, often hard to reverse
- Repeated Bets = many similar decisions over time, where calibration and process matter more than any one outcome
- Portfolio Construction = allocation across multiple opportunities where correlation and marginal contribution matter
- Optionality / Staged Commitment = the user can act in phases, buy information, and preserve upside while limiting downside
- Adversarial Game = other actors respond strategically to the user's move; signaling and countermoves matter
- Exploration vs Exploitation = the user must decide how much to spend learning versus scaling what already works

If unclear, infer the most decision-useful mode and state assumptions explicitly.

Return:
- Primary decision mode
- Secondary decision mode if any
- Why this decision mode fits

Rule:
Task defines the objective.
Domain defines the ontology.
Output mode defines the deliverable.
Evidence mode defines the proof standard.
Uncertainty mode defines the skepticism and update logic.
Decision mode defines the action logic.
