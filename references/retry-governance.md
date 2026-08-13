# Tool Failure & Retry Governance

Single-file owner of agent-level tool-failure classification, bounded retry, loop prevention, and workaround discipline. Apply it to every failed tool call: command execution, HTTP/API calls, file edits, and arbitrary tool output.

## Table of Contents

1. [Purpose and Scope](#purpose-and-scope)
2. [Failure Classification](#failure-classification)
3. [Bounded Retry Policy](#bounded-retry-policy)
4. [Loop Guard](#loop-guard)
5. [Halt-and-Report Contract](#halt-and-report-contract)
6. [Workaround Discipline](#workaround-discipline)
7. [System-Level Reinforcement](#system-level-reinforcement)

## Purpose and Scope

- Governs the agent's response to tool-use failures at the agent level: classification, retry budget, loop guard, halt-and-report, and workaround discipline
- Complements, does not replace: pre-edit-safety.md (Failure and Rollback), context-drift-governance.md (Mode A iteration caps), edit-cas-gate.md (edit-tool race handling), approval-briefing.md (approval pipeline)
- Prompt-level rules in this file are a soft constraint; prefer matching system-level retry settings of the host agent framework (Section 7)

## Failure Classification

Classify error-code-first, then HTTP status. Never classify by status code alone.

| Class | Signals (examples) | Retry decision |
|---|---|---|
| Transient | HTTP 500/502/503/504; network timeout, connection reset, DNS failure | Same-shape retry allowed, bounded (Section 3) |
| Throttling | HTTP 429 or 503 with Retry-After; rate-limit or quota codes | Same-shape retry allowed, honor Retry-After |
| Deterministic (fatal) | 4xx default (400/401/403/404/422); schema or validation errors; DB structural errors (missing column or table); missing or invalid tool; authorization denial; any unclassifiable failure | No retry; halt-and-report (Section 5) |
| LLM-recoverable | Malformed tool arguments, parse failures, bad tool output | Feed the error back to the model at most once; never same-shape retry |
| User-fixable | Missing information, unclear instructions | Pause and ask; human-in-the-loop |

Notes:
- A 400 paired with a transient error code (for example RequestTimeout) is retried; a 400 with a validation error is not. Error code wins.
- A 409 Conflict is retried only when idempotency proves the effect or the resource is temporarily locked; otherwise treat it as deterministic.
- A 503 with Retry-After is classified as throttling (server-directed wait); a 503 without Retry-After is transient.
- When classification is uncertain, treat the failure as deterministic. When in doubt, halt-and-report rather than retry.

## Bounded Retry Policy

- Only transient and throttling failures are eligible for same-shape retries
- Use exponential backoff with jitter: delay = random(0, 1) × min(20s, base × 2^attempt), with base 50ms for transient and 1s for throttling
- Honor Retry-After when present (429 or 503); it takes precedence over the computed delay
- Hard cap: max 3 attempts (initial plus 2 retries) per failing call
- Never retry: deterministic failures, permission denials, user cancellations, edit-tool races (edit-cas-gate.md), or any classification that is fatal
- A retry that changes the tool call or its arguments is not a retry: it is a deviation and follows Section 6

## Loop Guard

- Consecutive tool-failure cap: 3 failures in a row terminates the failing path
- Identical-call detection: same tool name plus same arguments repeated beyond the threshold (default 3-5) signals a loop; stop immediately
- Compose with context-drift-governance.md Mode A iteration caps and bounded verification (max 2 refinement rounds); the tightest cap wins
- On loop-guard exhaustion, apply the Halt-and-Report Contract (Section 5)

## Halt-and-Report Contract

- Deterministic failures and exhausted retry or loop budgets require immediate halt-and-report
- Report what failed, the classification evidence, attempts made, current state, and recovery information
- Preserve session state and registered backups; never auto-rollback (pre-edit-safety.md Failure and Rollback)
- Subagent workers report BLOCKED or NEEDS_CONTEXT per subagent-orchestration.md; the main session owns escalation

## Workaround Discipline

- No auto-deviation: after a failed or denied tool call, never silently switch to an alternative tool, route, or workaround
- If alternatives exist, route them through the currently implemented approval policy and pipeline (approval-briefing.md)
- A denied or blocked tool is not a license to find a bypass; escalating tool use requires explicit approval (interrupt-recovery.md)
- Fallbacks are allowed only when the original mandate explicitly authorized them (for example a model fallback named in the mandate)

## System-Level Reinforcement

- Prompt-level retry discipline degrades over long contexts; prefer host-framework system-level settings
- Generate a framework-specific tuning guide by feeding the attachment prompt (agent-framework-retry-tuning-prompt.md in the user home directory) to the agent
- At minimum configure: model-call retry cap, tool-execution retry cap, loop or turn limit, rate-limit backoff, and permission hooks
