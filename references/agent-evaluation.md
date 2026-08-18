# Agent Evaluation

## Table of Contents

- Overview
- Metrics Catalog
- Offline vs Online Evaluation
- Shadow Testing
- Hooking into Verification
- Anti-Patterns

## Overview

Evaluation quantifies an agent's performance so changes are measurable, not anecdotal. The skill's Verification Hooks (binary PASS/FAIL) establish *whether* an output is correct; this reference adds *how well* the agent performs across runs. Apply it when introducing, changing, or comparing agent behavior, and before any cutover to a new configuration.

## Metrics Catalog

Measure the core metric set per run and aggregate over a dataset or live traffic:

| Metric | Definition | What it signals |
|---|---|---|
| Task success rate | Fraction of runs reaching the Definition of Done | Overall capability |
| Tool-call accuracy | Fraction of tool calls that were correct/well-formed | Function-calling reliability |
| Average steps | Mean steps (loop iterations / tool calls) per task | Efficiency |
| Latency | Time-to-completion (and per-step) | Responsiveness |
| Cost | Tokens/currency consumed per run | Economics |
| User satisfaction | Human rating or proxy (e.g., approval/follow-ups) | Perceived quality |

Record these per run; aggregate over the evaluation set. Per-metric thresholds are task- and org-specific (mark them as tunable, not authoritative).

## Offline vs Online Evaluation

- **Offline** — evaluate on a curated dataset or recorded replay **before deployment**; acts as a regression gate. Deterministic where ground truth exists.
- **Online** — evaluate on **live production traffic** using an LLM-as-judge or human feedback when no ground truth is available.
- Use offline as the gate before release; use online for continuous monitoring after release. A change that passes offline but regresses online is a signal to inspect for environment/test-set mismatch.

## Shadow Testing

- Run the **candidate agent against the incumbent on mirrored live traffic**, without affecting users.
- Compare success rate, latency, and cost **before cutover** (A/B against the incumbent).
- Treat the shadow fraction and rollout schedule as tunable policy; start small and increase only as evidence supports it.

## Hooking into Verification

- The Verification Hook for any change is: define the metric set for the task, run the evaluation (offline or shadow), and state the observed values versus the target.
- Keep evaluation evidence in-session and record the metric set + source of the baseline (offline dataset / live traffic / shadow).

## Anti-Patterns

- **No metrics**: evaluating only on "it looks right" without the metric catalog.
- **Silent single run**: judging success on one favorable run rather than an aggregate.
- **Unmeasured regression**: shipping a change without an offline baseline.
- **Ground-truth confusion**: applying LLM-as-judge where objective ground truth exists, or vice versa.
