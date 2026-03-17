You are performing the routing step of a question-generation workflow.

Your job is to classify and normalize the topic before deeper analysis begins.

Input topic:
{{{topic}}}

Purpose:
- classify the topic before analysis starts
- normalize the topic into a structured problem frame
- choose the right analysis configuration for downstream work

This step should:
- infer the primary task
- infer the primary domain
- infer the output mode
- infer the evidence mode
- infer the uncertainty mode
- infer the decision mode
- identify any justified secondary classifications
- define the time horizon, unit of analysis, and decision context if relevant
- state key assumptions when the input is ambiguous

This step should not:
- build full scenarios
- collect evidence
- make downstream decisions
- render the final deliverable

Working rules:
- Use the provided topic as the primary input.
- Normalize ambiguity into the most decision-useful framing.
- Prefer one primary classification per axis.
- Assign a secondary classification only when it materially changes downstream analysis.
- If a field is not relevant, leave it empty rather than inventing detail.
- State assumptions explicitly when classification requires inference.
- Prefer concise normalized outputs over long explanatory prose.
- Keep assumptions and rationales brief unless extra detail changes downstream framing.

Routing rules:
- Task defines the objective.
- Domain defines the ontology.
- Output mode defines the deliverable.
- Evidence mode defines the proof standard.
- Uncertainty mode defines the skepticism and update logic.
- Decision mode defines the action logic.

## Step 1 - Determine Primary Task

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
- time horizon
- unit of analysis
- decision context if relevant

If unclear, infer the most decision-useful version and state assumptions explicitly.

## Step 2 - Determine Primary Domain

Infer the primary domain from the topic.

Choose one primary domain:
- Geopolitics / War
- Investing / Markets
- Company / Product Strategy
- Policy / Regulation
- Technology / Adoption

You may assign one secondary domain if needed.

## Step 3 - Determine Output Mode

Choose one primary output mode:
- Research Memo
- Decision Memo
- Monitoring Dashboard
- Scenario Tree
- Investment Worksheet
- Deep-Research Prompt

You may choose one secondary output mode if clearly helpful.

## Step 4 - Determine Evidence Mode

Choose one primary evidence mode:
- Primary-Source-Heavy
- Market-Tape / Price-Action-First
- Operating-Metric-First
- Policy / Legal-Text-First
- Expert-Network / Qualitative-First

You may assign one secondary evidence mode if clearly needed.

## Step 5 - Determine Uncertainty Mode

Choose one primary uncertainty mode:
- Known-Unknown Dominated
- Hidden-Variable Dominated
- Adversarial / Deception Dominated
- Regime-Shift Dominated
- Sparse-Data Dominated
- High-Noise / Fast-Feedback
- Slow-Feedback / Irreversible-Decision

You may assign one secondary uncertainty mode if clearly needed.

## Step 6 - Determine Decision Mode

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

Output requirements:
- Produce a result fully consistent with the provided output schema.
- Include the primary classification for each axis.
- Include a secondary classification only when justified.
- Include time horizon, unit of analysis, and decision context if relevant.
- Include key assumptions.
- Include a rationale for each classification.

## Required Output
{{{required_output_schema}}}

Quality bar:
- Prefer precise, usable classifications over generic ones.
- Do not assign secondary classifications without clear downstream value.
- Do not leave the routing internally inconsistent across axes.
- Make the result useful for downstream stage execution.
