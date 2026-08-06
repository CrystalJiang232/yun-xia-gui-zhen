# Subagent Orchestration Protocol

> **Eligibility check**: This protocol applies ONLY when the reading agent confirms it has the capability to spawn subagents AND the user has not explicitly forbidden subagent usage. If either condition fails, skip this protocol entirely and use standard single-agent CTAGV.
>
> Core principle: *The main agent is a supervisor — it ensures work gets done, it does not do all the work itself.*

> **Precedence**: When subagent orchestration is active (Mode B), the rules in this file are required, not advisory. Explicit user directions override this skill's defaults only when higher-priority system, developer, workspace, safety, and user constraints permit the override. Interactive clarification with the user is always preferred over silently working around a rule.

---

## Table of Contents

- [1. Should I Spawn? — Decision Matrix](#1-should-i-spawn--decision-matrix)
- [2. Role Taxonomy — Horizontal Decomposition Only](#2-role-taxonomy--horizontal-decomposition-only)
- [3. Handoff Contract — State Passing](#3-handoff-contract--state-passing)
- [4. Main Agent as Supervisor — CTAGV Re-mapping](#4-main-agent-as-supervisor--ctagv-re-mapping)
- [5. Execution Patterns](#5-execution-patterns)
- [6. Anti-Patterns](#6-anti-patterns)
- [7. Emergency Procedures](#7-emergency-procedures)
- [8. Coordination & Failure Governance](#8-coordination--failure-governance)
- [Non-negotiables recap](#non-negotiables-recap)

---

## 1. Should I Spawn? — Decision Matrix

Before consulting the matrix, confirm the pre-gate: subagent spawning is justified only when the task is genuinely parallelizable or exceeds single-context capacity, AND the coordination cost (roughly 10–15x tokens per delegated unit of work) is justified by the payoff. If the pre-gate fails, stay inline unless the protected source-candidate comparison rule below applies.

Spawn a subagent when **ANY** of the following conditions are met:

| Condition | Rationale | Examples |
|-----------|-----------|----------|
| **Result-oriented task** | Main session only needs a fraction of the final answer; the process of getting there is disposable | "Find all usages of function X across the codebase" — main agent only needs the aggregated result |
| **Context/token-consuming task** | Large input expected that would bloat main agent context | "Analyze this 50-file PR for correctness, concurrency, performance, and safety issues" |
| **Parallel and time-consuming** | Multiple independent workstreams exist that can execute simultaneously | "Check for TypeScript errors AND run the test suite AND lint the changed files" |

### Heavy-Context Task Classes — Class-Grade Trigger

Independent of the per-row matrix judgment above, the following task **classes** are deemed intrinsically sufficient for delegation whenever Mode B is active. When the task at hand belongs to one of these classes, spawning is not discretionary: staying inline is a protocol violation, not a judgment call.

- **Large documentation exploration** — multi-document or long-form document traversal, comparison, or synthesis
- **Mass codebase dives** — cross-file reference hunting, dependency mapping, PR-scale review, bulk pattern search
- **Wide web search / aggregation of excessive information** — multi-source research where the raw intermediate material would bloat the main session's context
- **Any task whose raw intermediate material exceeds what the main session should hold** — the generalization of the above; when in doubt, estimate the raw-material volume first, and if it would crowd out governance state in the main context, delegate

When a class-grade trigger fires, the orchestration-only constraint (§4 Hard Rule) applies for the duration of that task: the main session orchestrates and synthesizes only. The "Do NOT spawn" conditions below still override — a class-grade task that requires continuous user interaction or is tightly coupled/sequential stays inline (or is re-scoped until it isn't).

**Do NOT spawn** when:

| Condition | Rationale | Examples |
|-----------|-----------|----------|
| **Locally context-dependent task** | Requires understanding of the ongoing conversation flow | "Explain what you just did", "Why did you choose that approach?" |
| **Trivially completable** | Inline execution is faster than orchestration overhead | A single file edit, a one-line grep, answering a straightforward factual question |
| **Continuous user interaction** | Subagents lack direct user access; mid-flight clarification is impossible | Any task likely to require user feedback before completion |
| **Tightly coupled / sequential dependencies** | Each step depends on the previous one's output; parallelism gains are illusory and handoff costs dominate | Multi-stage refactors where stage N edits what stage N-1 produced. **Exception**: a large single-artifact edit/write task delegates via Chunked Sequential Edit (§5 Pattern F) — sequential, not parallel |

The Missing-Field Protocol wait loop (missing-field-protocol.md) is inherently continuous-user-interaction: the halt and the field request stay in the main session and are never delegated.

### Protected Source-Candidate Comparison

Use [pre-edit-safety.md](pre-edit-safety.md) as the sole owner of comparison definitions, candidate selection, Mode A fallback, and detailed pre-edit procedure.

- **Mode B routing**: delegate protected comparison even when it is small, trivial, tightly coupled, or otherwise fails the normal spawn pre-gate. Use one bounded read-only comparator by default; do not create competing comparator agents.
- **Mode A routing**: apply the fallback and explicit-override rules in [pre-edit-safety.md](pre-edit-safety.md); never infer inline authority from the absence of Mode B.
- **Failure route**: a protected comparator failure never triggers automatic inline takeover. Re-delegate once with a fresh bounded mandate when useful, or halt and report the failure. Inline takeover requires an explicit, permitted user direction.

---

## 2. Role Taxonomy — Horizontal Decomposition Only

Define subagent roles by **function**, not by hierarchy. Each role handles a distinct concern domain. All roles at the same level — never nested.

### Baseline Roles for Coding Tasks

These roles serve as the **default set** for software development tasks. Extend or replace based on domain and user specification.

| Role | Responsibility | Typical Spawn Trigger |
|------|---------------|----------------------|
| **Clarifier** | Probes ambiguous requirements, extracts implicit constraints, validates assumptions | Clarification Protocol activates; user's intent is unclear |
| **Executor** | Performs the core work: code generation, refactoring, analysis, documentation | Task is well-scoped and ready for implementation |
| **Verifier** | Validates output against constraints, runs tests, checks for regressions | Pre-completion checkpoint; after generation phase |

### Example Specialized Roles (Coding Domain)

| Role | Responsibility | Example Context |
|------|---------------|-----------------|
| **Codebase-Scanner** | Explores specific code paths, finds references, maps dependencies | "Find all call sites of `authMiddleware`" |
| **Static-Analyzer** | Runs lint, type-check, security scan, style enforcement tools | "Check for ESLint errors and TypeScript type violations" |
| **Debugger** | Executes code, traces runtime behavior, reproduces reported issues | "Run the failing test and capture the stack trace" |
| **Researcher** | Gathers external docs, compares library alternatives, verifies API compatibility | Reference Verification needed for technology choices |
| **Source-Candidate Comparator** | Performs bounded read-only code comparison between candidate roots | Pre-edit source authority cannot be resolved from metadata alone |

### Extensibility Rules

- **User-defined roles take precedence**: If the user specifies custom roles or role names, use those verbatim
- **Cross-domain generalization**: The coding-sense semantics generalize to every domain — map the baseline roles onto non-coding work rather than abandoning them. Examples: **Doc-Explorer** (large documentation traversal/synthesis), **Web-Aggregator** (multi-source search fan-in), **Data-Diver** (bulk dataset profiling), **Draft-Writer** (long-form generation), **Fact-Verifier** (claim cross-referencing). The role names change per domain; the horizontal-composition rule, max depth 1, and the orchestration-only constraint on the main session do not
- **Horizontal only**: Each role covers a different *concern* at the same *level*. Never assign a role whose job is to "manage other subagents"
- **Max depth = 1**: Subagents are **strictly prohibited** from spawning further subagents. If a subagent encounters a sub-subtask, it must either:
  - Complete the sub-subtask inline using its own context and tools
  - Report back to the main agent with a clear recommendation for re-delegation

### Composition Guidance

Scale concurrency by effort, tiered:

- **Default: 1 agent (inline execution)** — single-agent execution is the default; fan out only when the work is embarrassingly parallel.
- **Protected source-candidate comparison: 1 read-only subagent** — use one bounded comparator; add no competing comparator agents.
- **Other comparison-type tasks: 2–4 subagents** — e.g., evaluating independent alternatives or cross-validating an answer.
- **Large, genuinely-parallel research tasks: up to 5–7 subagents** — this remains a conditional ceiling, valid only when each subagent carries a full mandate brief and progress is actively tracked.
- **Extreme research: 10+ subagents** — permitted only behind a human plan-review gate.

This is guidance, not a hard limit — the framework may enforce its own concurrency ceiling. Exceeding the 5–7 tier adds coordination overhead that typically outweighs parallelism gains.

---

## 3. Handoff Contract — State Passing

Every spawned subagent receives a **mandate** containing all and only the information it needs. No implicit context. Vague delegation is the primary cause of duplicated or contradictory subagent work, so the mandate must pin down scope before spawning.

### Mandate Format

```markdown
# Subagent Mandate

## Task
[Single-sentence subject line — clear, specific, traceable]

## Echo
[Subagent restates the applicable mandate rule in its own words before acting, confirming it understood the brief]

## Context
[Relevant background the subagent needs to begin work]

## Input
[Files, code snippets, or data to operate on]

## Constraints
[Hard/soft/negative constraints applicable to this subtask]

## Boundaries
[Scope exclusions: what this subagent must NOT touch, read, or modify]

## Effort Budget
[Expected tool-call/step budget; if exceeded, pause and report back instead of pushing on]

## Expected Output
[Exact format and content expected on completion]

## Verifier Hook
[How the main agent will check the output: specific, checkable condition]
```

The Echo step exists because misunderstandings caught before execution cost nothing, while misunderstandings caught after execution cost a full subagent run.

### Return Self-Check

Before returning, the subagent confirms its report includes a 3-item checklist:

1. It stayed within the mandate's Boundaries.
2. It did not spawn any further subagents.
3. Its report matches the requested Expected Output format.

### Rules

- **No implicit context**: The subagent receives *only* what's in the mandate
- **No side effects**: The subagent returns *only* the expected output — no file writes, no state changes, unless explicitly scoped in the mandate
- **Clean workspace**: Intermediate work products stay in the OS-temp session directory (per context-drift-governance.md, File Hygiene); only deliverables return to main agent
- **No overlapping or rival mandates**: If multiple subagents are given related tasks, their mandates must have non-overlapping scopes. Never pit subagents against each other to "see who does better"
- **Protection inheritance**: Every writable-worker mandate carries the current protection-status record defined by [pre-edit-safety.md](pre-edit-safety.md). The worker reads and validates that record before touching task material; missing, unresolved, or stale protection state returns `BLOCKED` without a write.
- **Mandate integrity**: every mandate contains complete fields. A subagent that receives a truncated or field-missing mandate applies the Missing-Field Protocol (missing-field-protocol.md): halt, report `NEEDS_CONTEXT` (or the mandated `BLOCKED` status), and never guess the missing content.

---

## 4. Main Agent as Supervisor — CTAGV Re-mapping

The main agent still implements CTAGV, but its responsibilities shift from execution to orchestration:

| Phase | Single-Agent Mode | Subagent-Supervisor Mode |
|-------|-------------------|--------------------------|
| **C**onstraints | Write constraints file | Write constraints file; derive per-subagent constraint slices |
| **T**ask | Plan own work | Decompose into subtasks; assign to subagent roles via mandates |
| **A**cquire | Search/read/gather | Spawn acquisition subagents in parallel; synthesize their returns |
| **G**enerate | Do the work | Spawn executor subagents; review and integrate their outputs |
| **V**erify | Run verification hooks | Spawn verifier subagents; cross-check outputs against hooks; adjudicate conflicts (per §7 — with user pre-approval, else escalate) |

**Key shift**: The main agent's "work" becomes *reviewing, integrating, and adjudicating* subagent outputs (per §7 — with user pre-approval, else escalate) — not producing them directly.

**Hard rule (orchestration-only main session)**: While Subagent-Supervisor Mode is active for a task, the main agent's tool usage is restricted to orchestration actions — spawning subagents, reading their returned reports, and writing governance/state files. Direct edits to task artifacts (code, documents, data) by the main session are prohibited while delegation is available; if the main agent catches itself reaching for an edit tool on task material, that is the signal to write a mandate instead. This mirrors the established orchestrator-worker prompting practice of instructing the lead agent "do not execute tasks yourself — your outputs are plans and evaluations only"; where the harness supports it, structural enforcement (tool partitioning: execution tools available to workers only) is preferred over prompt-level rules, because prompt-level restraint degrades over long contexts.

**Weaker hint (no direct code inspection)**: Even outside edits, the main session *should* avoid reading or inspecting code/task material directly — inspection belongs in explorer/verifier subagents whose compressed returns keep the main context clean. This is a strong default, not an absolute prohibition. Recognized exemptions:

1. **Explicit user approval or request** — the user asks the main session to look at or modify the material directly, and higher-priority constraints permit the override.
2. **Deadlocked conflict, small and self-contained** — subagent findings conflict, no result is objectively verifiable as correct, and the confidence-gated tie-breaker subagent (§7 Tie-Breaker Protocol) has returned below the 0.9 report threshold with no valid resolution. Confidence never supplies adoption authority; the user-preapproval and objective-verifiability requirements still apply. Even then: **report back and halt for user discretion first**. Direct inspection by the main session is permitted only if the conflict is small enough to be self-contained (a bounded region — a single function, file, or claim — that one focused read can adjudicate) AND the user is unavailable or has pre-approved autonomous handling of small conflicts. Anything larger stays halted pending the user.
3. **Announced emergency takeover** — per §7, with a visible in-session announcement and ledger entry. Before any write, the takeover reads and validates the inherited protection status from [pre-edit-safety.md](pre-edit-safety.md); unresolved or stale status blocks the takeover.

Retries against a deadlocked conflict are bounded (exactly one tie-breaker round, consistent with the max-2 refinement bound in §8) before halting — never loop autonomously.

---

## 5. Execution Patterns

### Pattern Selection — No Pattern Is Intrinsically Superior

Choose by the task's **dependency structure**, not by preference:

- **Independent, parallelizable concerns → Fan-Out** (Pattern A)
- **Dependent stages, each context-heavy → Pipeline** (Pattern B)
- **One large artifact or tightly-coupled artifact set, edit/write-type → Chunked Sequential Edit** (Pattern F)
- Real projects are usually **hybrid (project-based structure)**: fan out across independent modules/concerns, then run Pipeline or Chunked Sequential Edit *within* each shared artifact

### Pattern A: Fan-Out (Independent Concerns)

```
Main Agent --> Subagent A (concern X)
          |--> Subagent B (concern Y)
          |--> Subagent C (concern Z)
          |
          <---- (synthesize A + B + C results)
```

Use when: Multiple concerns can be evaluated independently. Each subagent handles a distinct dimension of the same input. Requires the coordination layer in place — mandate briefs, verification, and termination conditions for every spawned subagent.

**Example**: A PR review spawning one subagent per concern (correctness, concurrency, performance, safety).

### Pattern B: Pipeline (Dependent Stages)

```
Main Agent --> Subagent A (explore/discover)
                  |
                  v
             Subagent B (implement, using A's output)
                  |
                  v
             Subagent C (verify, using B's output)
```

Use when: Later steps fundamentally depend on earlier outputs AND each stage is context-heavy enough to justify the handoff cost. Sequential chains add wall-clock latency per stage — that is a cost to budget, not a defect of the pattern.

### Pattern C: Swarm (Same Task, Multiple Angles)

```
Main Agent --> Subagent A (approach: static analysis)
          |--> Subagent B (approach: runtime testing)
          |--> Subagent C (approach: manual code review)
          |
          <---- (compare findings; adjudicate conflicts)
```

Use when: High-stakes verification requiring cross-method consensus. If subagents disagree, route through the §7 Tie-Breaker Protocol or **initiate interactive clarification with the user**. A tie-breaker may report an evidence-backed conclusion at confidence ≥ 0.9, but the main agent adopts it autonomously only with prior user approval and objective verification; otherwise present it to the user for selection.

### Pattern D: Event-Driven (Reactive Triggers)

```
Main Agent (supervisor, monitoring event queue)
    |
    |--[event: test failure]--> Subagent (investigate specific failure)
    |--[event: build error]--> Subagent (diagnose build issue)
    |--[event: dependency alert]--> Subagent (assess impact)
    |
    <---- (aggregate event responses; decide next action)
```

Use when: Responding to discrete, asynchronous triggers in HFT DevOps contexts (CI pipeline events, monitoring alerts, deployment hooks). The main agent routes events to specialized handler subagents.

### Pattern E: Peer-to-Peer (Cross-Validation)

```
Main Agent --> Subagent A (produces solution Alpha)
          |--> Subagent B (produces solution Beta)
          |
          <---- (compare Alpha vs Beta; user clarification if divergent)
```

Use when: Evaluating trade-offs between fundamentally different approaches (e.g., sync vs async architecture, SQL vs NoSQL migration). Both solutions are valid — the choice requires user judgment. **Always escalate to user** when peer outputs conflict on approach selection.

### Pattern F: Chunked Sequential Edit (Large Single-Artifact Tasks)

```
Main Agent (supervisor, owns Artifact State Log)
    |
    |--> Chunk-1 implementer (edits shared artifact) --> review --> ledger: "chunk 1 complete"
    |--> Chunk-2 implementer (fresh, reads State Log) --> review --> ledger: "chunk 2 complete"
    |--> ...
    |
    <---- (final broad review across all chunks)
```

Use when: a single edit/write task on one artifact (or a tightly-coupled artifact set) exceeds what one subagent can reliably carry — very large files, long multi-part documents, plan-scale implementation. Do NOT hand it to one long-running subagent; split it into ordered chunks and dispatch **one fresh implementer subagent per chunk, strictly sequentially**. Never run implementer subagents in parallel on the same artifact — write conflicts and stale overwrites are the documented failure (stale-overwrite incidents have destroyed hours of sequential subagent work in practice).

Binding rules (derived from subagent-driven-development practice and observed incident reports):

1. **Shared Artifact State Log** — the supervisor maintains it in the state files (spec in context-drift-governance.md): per-file hash/mtime after each chunk, completed chunks with one-line outcomes, decisions made, and symbols introduced (so later chunks never reference unknown code).
2. **Staleness guard (mandatory)** — before writing any shared file, a chunk implementer MUST re-read the file or compare its hash/mtime against the State Log. Mismatch ⇒ report `STALE`, abort the chunk; the supervisor refreshes the brief and re-dispatches. Blind overwrites are a protocol violation. General single-agent analogue: [edit-cas-gate.md](edit-cas-gate.md).
3. **Artifacts as files, not prompt text** — each chunk dispatch carries a brief *file path* (the chunk's requirements, exact values), one line on where the chunk fits, and pointers to State Log entries it depends on. Never paste accumulated prior-chunk history into a dispatch; a fresh implementer needs its chunk, the interfaces it touches, and the global constraints — nothing else.
4. **Status protocol** — implementers report `DONE` / `DONE_WITH_CONCERNS` / `NEEDS_CONTEXT` / `BLOCKED`. A `BLOCKED`-because-too-large chunk is re-chunked smaller; never force the same subagent to retry unchanged.
5. **Ledger as recovery map** — one completion line per chunk in the progress ledger. Session memory does not survive compaction; trust the ledger over recollection, and never re-dispatch a chunk the ledger marks complete — re-dispatching completed work is the single most expensive orchestration failure observed in practice.
6. **Review per chunk + final broad review** — each chunk's diff is verified before the next chunk dispatches; one broad review runs across the whole artifact at the end (fixes dispatched as ONE fix subagent for all findings, not one per finding).
7. **Pre-edit protection inheritance** — every chunk mandate carries the current protection-status record from [pre-edit-safety.md](pre-edit-safety.md). Each implementer reads and validates it before writing in addition to applying the staleness guard; either check failing aborts the chunk.

---

## 6. Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|-----------------|
| **Over-spawning** | Token cost balloons; trivial tasks cost more via orchestration overhead than inline execution | Check Decision Matrix — trivial tasks stay inline |
| **Vertical nesting (depth > 1)** | Subagent spawns subagent → exponential error cascade, context loss, unaccountable failures | Max depth = 1, strict; subagent reports back, main agent re-delegates if needed |
| **Vague mandates** | Subagent lacks clarity → returns garbage → main agent context wasted anyway | Handoff Contract: exact input, exact output, exact constraints |
| **Sequential pipeline overuse** | Each subagent adds latency; 3 sequential subagents = 3x wall clock time | Re-check dependency structure (§5 Pattern Selection): Fan-Out only for genuinely independent concerns; Pipeline only when each stage is independently context-heavy |
| **Parallel implementers on one artifact** | Concurrent writes to a shared file → conflicts, stale overwrites, silent loss of earlier chunks' work | Chunked Sequential Edit (§5 Pattern F): strictly sequential implementers + Artifact State Log + mandatory staleness guard |
| **Overlapping or rival mandates** | Pitting subagents against each other wastes tokens, creates conflicting outputs, and removes user agency | Assign non-overlapping scopes per mandate; if approaches conflict, escalate to user for clarification |
| **No synthesis plan** | Main agent drowns in disconnected subagent outputs | Define Expected Output in every mandate; have integration strategy before spawning |
| **Autonomous conflict resolution** | Main agent picks winners between conflicting subagent outputs without user input | Interactive clarification: present conflict, sources, and trade-offs; let user decide |

---

## 7. Emergency Procedures

### Subagent Failure

If a subagent fails or returns unusable output:

1. Record the failure and classify whether the subtask is protected source-candidate comparison, writable work, or ordinary read-only work.
2. For protected source-candidate comparison, re-delegate at most once with a fresh bounded read-only mandate when useful; otherwise halt and report. Never take it over inline automatically. Inline comparison requires an explicit user direction that higher-priority constraints permit.
3. For writable work, any fresh worker or announced emergency takeover inherits, reads, and validates the current protection status from [pre-edit-safety.md](pre-edit-safety.md) before writing. Missing, unresolved, or stale status blocks the write.
4. For other work, take over inline only after a visible announcement and ledger entry, or re-scope it into a fresh handoff-ready mandate. A fresh sibling delegation is not subagent nesting.
5. On terminal failure, follow [pre-edit-safety.md](pre-edit-safety.md) and Context Drift Governance: report the failure, retain protection status and registered backups, and do not perform automatic rollback.

### Conflicting Subagent Results

If subagents return conflicting or divergent results:

1. Present the conflict to the user with full attribution (RAG Pattern)
2. Include: what each subagent concluded, what evidence/method they used, and the trade-offs
3. **Prefer interactive clarification** — let the user adjudicate
4. Only autonomously resolve when: (a) one result is objectively verifiable as correct, (b) the other is demonstrably wrong by the same verification standard, AND (c) the user has pre-approved autonomous adjudication; otherwise escalate to interactive clarification.
5. **Tie-Breaker Protocol (default instrument when two subagents' findings conflict)**: when two subagents return conflicting findings, spawn at most ONE third tie-breaker subagent (bounded per §8's max-2 refinement spirit — no repeated tie-breaker loops). The tie-breaker operates under these rules:
   - **Input**: the original task context plus BOTH conflicting findings in full, presented neutrally — no main-session commentary, no hints about which finding the main session favors
   - **Task**: judge the confidence of EACH finding through **independent exploration** — re-verify the contested claims against the underlying material itself (code, documents, sources), not merely compare the two reports rhetorically. Evidence-grounded adjudication is required because naive LLM-as-judge comparison is vulnerable to fluency bias, self-preference, and shared-backbone blind spots; where the harness permits, instantiate the tie-breaker with a different method or backbone than the conflicting pair
   - **Confidence report gate**: the tie-breaker issues a conclusion in its report ONLY when its confidence in one finding is **≥ 0.9**, stated as a numeric score per finding and backed by the specific evidence gathered during independent exploration — a bare self-rating without an evidence trail does not count as confidence (LLM self-reported confidence is imperfectly calibrated; the evidence requirement is the calibration substitute). Crossing this report gate does not authorize the main agent to adopt the conclusion.
   - **Adoption gate**: the main agent may adopt a tie-breaker conclusion autonomously only when the user pre-approved autonomous adjudication AND the result is objectively verifiable under the same standard. Otherwise, including when confidence is ≥ 0.9, present the conclusion and evidence to the user for selection; confidence alone is never authority.
   - **Below threshold**: if neither finding reaches 0.9, the tie-breaker returns both scores plus the gathered evidence, and the matter MUST be reported back to the human for discretion — no autonomous resolution below the gate
   - **Main-session non-intervention**: while the tie-breaker runs, the main session MUST NOT intervene — no supplementary reads of the contested material, no hints, no mid-flight re-scoping, no pre-judgment. Its only permitted actions are waiting and recording the delegation in the progress ledger
6. **Deadlock path**: if the tie-breaker returns below the 0.9 gate, **report back and halt for user discretion**. The main session may inspect the conflicting material directly only under the small-and-self-contained exemption in §4 (Weaker hint, exemption 2); otherwise it waits.

### Context Bloat Despite Subagents

If the main agent context is still overloaded despite using subagents:

1. Review mandate quality — are you passing too much context to subagents?
2. Review synthesis strategy — are you failing to discard intermediate outputs after integration?
3. Consider breaking the overall task into sequential macro-phases, clearing context between phases

---

## 8. Coordination & Failure Governance

- **Evaluator-Optimizer**: an independent evaluator verifies subagent output against the acceptance criteria; retries are bounded (max 2 refinement rounds); on non-convergence, escalate to the user for interactive clarification rather than looping autonomously.
- **Progress ledger**: the supervisor tracks per-subagent status; a stall (no update after N actions) triggers replanning or a policy-valid fallback. Protected comparison cannot fall back inline automatically, and writable fallback must validate inherited pre-edit protection.
- **Delegation logging**: handoffs and delegation decisions are logged so a visible state audit trail exists.
- **Guardrails**: where the harness allows, external non-bypassable checks (file-scope allowlists, CI gates) complement the in-prompt rules in this file.
- **Termination & escalation**: termination conditions must be explicit before any fan-out; escalation modes (never / on-failure / always) are decided upfront; large fan-outs pass a human plan-review gate first. Escalations that return an empty/system-default response follow Clarification Channel Governance §A (clarification-protocol.md): the point defers and the round halts — it is never an approval.
- **Tool-risk tiering**: classify tools by risk before delegation — read-only vs writable, reversibility, and financial impact. Irreversible high-risk actions (e.g., destructive writes, payments, production changes) trigger human takeover before execution. The human plan-review gate for large fan-outs above is a subset of this general clause.
- **Voting/debate**: for high-stakes single decisions, run the task multiple times and aggregate (voting) or use structured debate rounds.
- **Citation/attribution verification**: fan-in synthesis of multi-subagent research claims is cross-referenced against reference-verification.md before acceptance.
- **Failure-taxonomy awareness**: industry trace studies (e.g., MAST, UC Berkeley 2025) show inter-agent misalignment and verification/termination failures dominate multi-agent failures; structural fixes (this section) outperform prompt tweaks.
- **Blackboard/shared-state**: file-based shared artifacts may substitute free-form message passing for auditability (optional, advanced) — except for chunked edits (§5 Pattern F), where the Artifact State Log is required, not optional.
- **When NOT to fan out**: sequential or tightly-coupled tasks, budget-sensitive contexts, and tasks that fit one context window all stay inline.

---

## Non-negotiables recap

When subagent orchestration is active, the following rules are testable on every run:

1. **Eligibility gate**: subagent capability confirmed and not forbidden by the user, else single-agent CTAGV.
2. **Max depth 1**: no subagent ever spawns another subagent.
3. **Mandate required**: every delegation carries a complete mandate brief — no implicit context.
4. **No overlapping or rival mandates**: mandate scopes are non-overlapping; no agents compete on the same delegated concern.
5. **Output conflicts escalate**: conflicting subagent outputs go to the §7 Tie-Breaker Protocol or to the user for interactive clarification. A tie-breaker reports a conclusion only at confidence ≥ 0.9 with independent evidence; the main agent adopts it autonomously only with user-preapproved adjudication and objective verification. Otherwise the user selects, because confidence alone is never authority; no main-session intervention occurs while the tie-breaker runs.
6. **Class-grade triggers are mandatory**: when the task belongs to a Heavy-Context Task Class (§1) and Mode B holds, delegation is required — staying inline is a violation, not a judgment call.
7. **Orchestration-only main session**: no direct edits, bulk exploration, or code inspection in the main session while delegation is available — governance files, permitted explicit user directions, the small-and-self-contained deadlock exemption (§4), and announced §7 emergency takeovers excepted.
8. **Protected comparison routing**: protected source-candidate comparison uses one bounded read-only comparator in Mode B regardless of triviality; Mode A and candidate-selection behavior come exclusively from [pre-edit-safety.md](pre-edit-safety.md), and no inline or takeover path bypasses that contract.
9. **Pre-edit protection inheritance**: every writable worker, chunk implementer, and emergency takeover reads valid inherited protection status before writing; terminal failure reports and retains state without automatic rollback.
