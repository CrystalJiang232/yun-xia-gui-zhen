# Missing-Field Protocol (Instruction Integrity)

## Table of Contents

- Overview
- When to Activate
- When Not to Activate
- Protocol Behavior
- Mid-Work Activation
- State Management
- Subagent Orchestration Interaction
- Precedence and Composition

## Overview

Protects workflow control against instructions that were stripped or truncated in transit (network loss, keyboard mistakes, system-message corruption). When the instruction's conveyance is damaged, the agent must NOT reconstruct the meaning. It halts, states which field is missing, and requests completion — repeatedly, without guessing — until valid semantics arrive or an explicit waiver applies.

## When to Activate

Activate at instruction intake (user prompt or system/structured message) when ANY of these signals are present:

- **Incomplete words or sentences** — text ends mid-word, mid-clause, or in a way that leaves the conveyed meaning unrecoverable
- **Invalid structured payloads** — malformed JSON or structurally broken system/structured messages
- **Missing parameters** — a required parameter of the instruction's own grammar is absent (e.g., review request without a target, edit request without a path)
- **Parameters far outside valid range** — a value that cannot be a plausible value of its field (e.g., negative Merge Request ID), indicating the field was stripped or corrupted

**Exclusions** — this protocol does NOT activate for:
- Typos, misspellings, grammar mistakes, or stylistic oddities in natural language
- Genuine ambiguity in an otherwise intact instruction (that is Clarification Protocol territory)

The gap must be **semantic**: the meaning or information the user conveys is incomplete, not merely imperfectly expressed. When classification is uncertain, treat the instruction as suspected-missing and ask the plain field request (below); do not silently choose a reading.

## When Not to Activate (and what to do instead)

- Intact prompt with genuine ambiguity → **Clarification Protocol** (options, trade-offs, recommended default)
- Missing dimension in an intact prompt → RTCF missing-dimension question (prompt-patterns.md)
- Mid-work barrier that is not truncation → Mid-Work Barrier Detection (clarification-protocol.md)

## Protocol Behavior

### Phase 1: Halt

1. STOP all task work immediately — no Acquire, no Generate, no plan synthesis
2. Do NOT infer the missing content; do NOT offer options, plan briefs, cascading changes, or a recommended default
3. Do NOT proceed to mode selection (Mode A/B) or any other protocol until this point resolves or an explicit waiver applies

### Phase 2: Plain Field Request

State plainly and completely, with evidence:

```text
Instruction appears incomplete: field <some_field> is missing/invalid.
Evidence: <signal(s) observed>.
Please provide the missing field.
```

No guesses about content. No "did you mean X?" No Option A/B. The only question is the request for the field itself.

Replace `<some_field>` with the actual field name(s). If more than one field is missing or invalid, name them all in a single request.

### Phase 3: Wait Loop

- After every user response, re-run the same screen on the identical field
- If the response still lacks the required semantics (e.g., the "clarification" is vague or repeats the gap), repeat the plain field request; do not escalate, do not assume
- A generic "just proceed" or "do what you think is best" does NOT exit the loop; the waiver requires the explicit no-interrupt mode or an explicit statement that the absence is normal
- Record each attempt in the Missing-Field Log (context-drift-governance.md)
- An empty, system-default, or timeout response is a **deferral**, not an answer: follow Clarification Channel Governance §A — mark deferred, halt the round, persist decisions and an UNEXECUTED next-round proposal, and await the user
- The loop exits ONLY when (a) valid semantics for the field arrive, or (b) an explicit waiver applies

### Phase 4: Waiver Branch (rare)

Exit the loop only when one of these is true:
- The user **pre-initiated a no-interrupt/YOLO-like mode** covering this round (explicit direction, recorded)
- The user **explicitly states the absence of the field is normal/expected**

Before proceeding, disclose all three, visibly and in-session:
1. **Interpreted semantic** — what the agent understood the user to mean
2. **Suggested missing field** — which field the agent believes is missing, with evidence
3. **Completed semantic** — the missing content the agent filled in via most-likelihood self-deduction, marked `assumed` (not verified)

Record the waiver wording, its scope, and the disclosure in session state (constraints file + Missing-Field Log). The completed field remains assumed and must be re-verified with the user at the next natural checkpoint (and before any irreversible action). This waiver is interpretive only: it does not waive source approval, dirty-state acceptance, or backup decisions (pre-edit-safety.md).

## Mid-Work Activation

If a truncated/corrupted message arrives during execution, or a parameter turns out missing mid-task, pause immediately, enter Phase 1, and follow this protocol. This overrides in-progress protocol selection without discarding completed, verified work; record the pause and the field in the Missing-Field Log.

## State Management — Missing-Field Log

Persist per activation in session state (see context-drift-governance.md):

```markdown
## Missing-Field Log — Activation <id>
Field: <name or description>
Signals: incomplete sentence | invalid JSON/structured payload | missing parameter | out-of-range value
Status: awaiting | deferred | restored | waived
Attempts: <N> — one line per round (response summary + still-missing evidence)
Waiver: none | <exact wording + scope + mode>
Disclosure: interpreted semantic / suggested missing field / completed semantic (assumed)
```

Reference this log in every output until the activation is restored or waived.

## Subagent Orchestration Interaction (Mode B)

- The halt and the wait loop are continuous-user-interaction by nature: they stay in the **main session** ("Do NOT spawn" condition, subagent-orchestration.md §1)
- A pre-clarification explorer may independently verify the classification (genuinely missing vs. mistyped) but must NOT propose completions or generate options
- **Mandate integrity**: every handoff contract must contain complete fields. A subagent that receives a truncated or field-missing mandate applies this protocol, reports `NEEDS_CONTEXT` (or the mandated `BLOCKED` status), and never guesses
- If YOLO completion is authorized, most-likelihood analysis may be delegated to an explorer, but the three-part disclosure is authored and delivered by the main session

## Precedence and Composition

- Missing-Field Protocol **outranks** Clarification Protocol for the missing field itself
- After the field is restored, remaining genuine ambiguity returns to the standard Clarification Protocol
- Clarification Channel Governance §A (defer/persist/halt) applies to the wait loop unchanged
- This protocol never authorizes guessing at the user's expense, and never converts a missing field into an implicit constraint
