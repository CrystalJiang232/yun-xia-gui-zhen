# 云霞归真 · yun-xia-gui-zhen

行到水穷处，坐看云起时。  
或许玲珑所寻的那些碎片，就藏于燕归谷的某级石阶下呢？

---

> *Defer to clarify. Verify to trust. Structure to persist.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A **task-agnostic governance skill** for AI coding agents. It does not tell an agent how to build software; it governs **whether and how the agent engages at all** — how it reads and interprets instructions, resolves conflicting directions, clarifies, protects files before editing, verifies claims, recovers from interruptions, budgets its context window, retries failed tools, and, where delegation is available, orchestrates subagents.

The methodology packs own spec → plan → TDD → review → ship (Superpowers, addyosmani/agent-skills, mattpocock/skills). YunXia sits one level above them: it decides whether to pick the tool up at all, and keeps the agent honest about its own instructions, its own edits, and its own claims. It composes with those packs rather than replacing them.

## The defensive-driving analogy

A coding agent is a fast car driven through traffic it cannot fully see. The other drivers are its own fluent-but-unreliable defaults, instructions that arrive damaged or contradictory, and an environment that changes underneath it. Nothing here assumes malice — only that a green light is not evidence the intersection is clear.

Three habits carry most of the skill:

| Defensive-driving habit                                              | Where it lands in YunXia                                                                                                                                    |
| -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scan before you move** — never trust one signal alone              | *Defer to clarify*: ambiguous requests open a clarification package; damaged instructions halt entirely instead of being guessed at                         |
| **Keep a safety margin** — leave room for the other driver's mistake | Pre-edit gate: resolve one authoritative source, classify the Git state, register a backup where required, and guard writes with a compare-and-swap re-hash |
| **Never assume you were seen** — no response is not a green light    | *Verify to trust*: an empty or default answer defers, never approves; a claim needs executed evidence before it is called done                              |

## Core philosophy

- **Defer to clarify.** No premature execution: requirements become explicit before work begins, and silence is never consent.
- **Verify to trust.** Claims carry executed evidence, not confidence — "seems right" is a hypothesis.
- **Structure to persist.** Session memory is unreliable; constraints, TODOs, verification hooks and protection state live in files.

## What makes it different

- **Instruction-integrity screening + Missing-Field Protocol.** Damaged instructions (truncated, structurally broken, missing a parameter) halt and are re-screened, never completed by guesswork. Peer skills stop an agent guessing at *vague* requests; this watches the *integrity* of the instruction itself.
- **An explicit conflict-resolution ladder.** Authority → polarity → scope, with recency applying only across rounds. A conflict the ladder cannot decide goes to clarification, never silent resolution.
- **Pre-edit safety engineered as a gate, not advice.** One authoritative source, a porcelain-classified Git state, a verified backup registry, and a write-time CAS guard. `yes.md` states the same spirit ("no backup = no edit, no test = no done") and enforces it with host hooks; YunXia's gate is host-agnostic, prompt-level, and adds authority resolution, dirty-tree deferral and the CAS guard.
- **Clarification channel governance: silence is never approval.** Decision-ownership semantics (`DO-1`…`DO-3`) make a default-identical answer still pending and procedural permission resolve nothing.
- **A tool-failure taxonomy.** Transient and throttling failures retry with backoff; deterministic failures halt and report; three consecutive failures stop the loop.
- **Reference verification as policy.** Web search is deny-by-default; the hierarchy is workspace files > system-scope files > web, with two independent sources per retained claim.
- **Interrupt recovery, context-budget governance, and delegation governed rather than merely executed.**
- **Mode discipline — knowing when NOT to run the machinery.** Quick Ask answers narrow questions without touching the workspace; Bootstrap Mode is an opt-in, read-only self-scan.

## What's inside

- **`SKILL.md`** (370 lines) — the entry point: mode selection, a 20-situation protocol-selection matrix, seven core protocols (`1`–`7`), two lettered siblings (`7a` Tool Failure & Retry Governance, `7b` Context Engineering), one conditional orchestration protocol (`8`), and seven prompt-engineering patterns.
- **`references/`** — 18 protocol files, loaded on demand by the active situation.
- **`bootstrap/`** — an opt-in, read-only configuration self-scan with 20 checks.

## How to use

Copy the folder into a skill directory the host loads — for Codex, `~/.codex/skills/yun-xia-gui-zhen`, carrying `SKILL.md`, `bootstrap/` and `references/` — or read `SKILL.md` directly. It is documentation-sized by design: it changes agent behaviour through loaded instructions, not a runtime library.

## Honest limits

- It does **not** encode domain engineering discipline — no TDD cycles, code review, or deployment runbooks. Pair it with a methodology pack.
- Rivals that ship executable hooks or a config compiler (for example `yes.md`, `crag`) can enforce things a prompt-level skill cannot guarantee on its own.
- Its distinctiveness claims rest on a dated ecosystem survey and are stated at mechanism level, not as category absence.

## Status

`SKILL.md` 370 lines · 18 references · 20 bootstrap checks.

## License

MIT © 2026 Hibiscus — see [LICENSE](LICENSE).
