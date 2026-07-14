# Subagent Orchestration Protocol

> **Eligibility check**: This protocol applies ONLY when the reading agent
> confirms it has the capability to spawn subagents AND the user has not
> explicitly forbidden subagent usage. If either condition fails, skip this
> protocol entirely and use standard single-agent CTAGV.
>
> Core principle: *The main agent is a supervisor — it ensures work gets done,
> it does not do all the work itself.*

---

## Table of Contents

- [1. Should I Spawn? — Decision Matrix](#1-should-i-spawn--decision-matrix)
- [2. Role Taxonomy — Horizontal Decomposition Only](#2-role-taxonomy--horizontal-decomposition-only)
- [3. Handoff Contract — State Passing](#3-handoff-contract--state-passing)
- [4. Main Agent as Supervisor — CTAGV Re-mapping](#4-main-agent-as-supervisor--ctagv-re-mapping)
- [5. Parallel Execution Patterns](#5-parallel-execution-patterns)
- [6. Anti-Patterns](#6-anti-patterns)
- [7. Emergency Procedures](#7-emergency-procedures)

---

## 1. Should I Spawn? — Decision Matrix

Spawn a subagent when **ANY** of the following conditions are met:

| Condition | Rationale | Examples |
|-----------|-----------|----------|
| **Result-oriented task** | Main session only needs a fraction of the final answer; the process of getting there is disposable | "Find all usages of function X across the codebase" — main agent only needs the aggregated result |
| **Context/token-consuming task** | Large input expected that would bloat main agent context | "Analyze this 50-file PR for correctness, concurrency, performance, and safety issues" |
| **Parallel and time-consuming** | Multiple independent workstreams exist that can execute simultaneously | "Check for TypeScript errors AND run the test suite AND lint the changed files" |

**Do NOT spawn** when:

| Condition | Rationale | Examples |
|-----------|-----------|----------|
| **Locally context-dependent task** | Requires understanding of the ongoing conversation flow | "Explain what you just did", "Why did you choose that approach?" |
| **Trivially completable** | Inline execution is faster than orchestration overhead | A single file edit, a one-line grep, answering a straightforward factual question |
| **Continuous user interaction** | Subagents lack direct user access; mid-flight clarification is impossible | Any task likely to require user feedback before completion |

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

### Extensibility Rules

- **User-defined roles take precedence**: If the user specifies custom roles or role names, use those verbatim
- **Domain expansion**: This skill may add baseline roles for non-coding domains (e.g., data analysis, creative writing) in future iterations
- **Horizontal only**: Each role covers a different *concern* at the same *level*. Never assign a role whose job is to "manage other subagents"
- **Max depth = 1**: Subagents are **strictly prohibited** from spawning further subagents. If a subagent encounters a sub-subtask, it must either:
  - Complete the sub-subtask inline using its own context and tools
  - Report back to the main agent with a clear recommendation for re-delegation

### Composition Guidance

For effective parallel execution, 5–7 concurrent subagents is a practical cutoff. Exceeding this range adds coordination overhead that typically outweighs parallelism gains. This is guidance, not a hard limit — the framework may enforce its own concurrency ceiling.

---

## 3. Handoff Contract — State Passing

Every spawned subagent receives a **mandate** containing all and only the information it needs. No implicit context.

### Mandate Format

```markdown
# Subagent Mandate

## Task
[Single-sentence subject line — clear, specific, traceable]

## Context
[Relevant background the subagent needs to begin work]

## Input
[Files, code snippets, or data to operate on]

## Constraints
[Hard/soft/negative constraints applicable to this subtask]

## Expected Output
[Exact format and content expected on completion]

## Verifier Hook
[How the main agent will check the output: specific, checkable condition]
```

### Rules

- **No implicit context**: The subagent receives *only* what's in the mandate
- **No side effects**: The subagent returns *only* the expected output — no file writes, no state changes, unless explicitly scoped in the mandate
- **Clean workspace**: Intermediate work products stay in `/tmp/`; only deliverables return to main agent
- **No competing subagents**: If multiple subagents are given related tasks, their mandates must have non-overlapping scopes. Never pit subagents against each other to "see who does better"

---

## 4. Main Agent as Supervisor — CTAGV Re-mapping

The main agent still implements CTAGV, but its responsibilities shift from execution to orchestration:

| Phase | Single-Agent Mode | Subagent-Supervisor Mode |
|-------|-------------------|--------------------------|
| **C**onstraints | Write constraints file | Write constraints file; derive per-subagent constraint slices |
| **T**ask | Plan own work | Decompose into subtasks; assign to subagent roles via mandates |
| **A**cquire | Search/read/gather | Spawn acquisition subagents in parallel; synthesize their returns |
| **G**enerate | Do the work | Spawn executor subagents; review and integrate their outputs |
| **V**erify | Run verification hooks | Spawn verifier subagents; cross-check outputs against hooks; adjudicate conflicts |

**Key shift**: The main agent's "work" becomes *reviewing, integrating, and adjudicating* subagent outputs — not producing them directly.

---

## 5. Parallel Execution Patterns

### Pattern A: Fan-Out (Independent Concerns)

```
Main Agent --> Subagent A (concern X)
          |--> Subagent B (concern Y)
          |--> Subagent C (concern Z)
          |
          <---- (synthesize A + B + C results)
```

Use when: Multiple concerns can be evaluated independently. Each subagent handles a distinct dimension of the same input.

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

Use when: Later steps fundamentally depend on earlier outputs. **Prefer to avoid** — sequential chains are slower than inline single-agent work. Only use when each stage is itself context-heavy enough to justify the handoff cost.

### Pattern C: Swarm (Same Task, Multiple Angles)

```
Main Agent --> Subagent A (approach: static analysis)
          |--> Subagent B (approach: runtime testing)
          |--> Subagent C (approach: manual code review)
          |
          <---- (compare findings; adjudicate conflicts)
```

Use when: High-stakes verification requiring cross-method consensus. If subagents disagree, the main agent must adjudicate or **initiate interactive clarification with the user** — never autonomously pick a winner without user awareness.

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

---

## 6. Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|-------------|-----------------|
| **Over-spawning** | Token cost balloons; trivial tasks cost more via orchestration overhead than inline execution | Check Decision Matrix — trivial tasks stay inline |
| **Vertical nesting (depth > 1)** | Subagent spawns subagent → exponential error cascade, context loss, unaccountable failures | Max depth = 1, strict; subagent reports back, main agent re-delegates if needed |
| **Vague mandates** | Subagent lacks clarity → returns garbage → main agent context wasted anyway | Handoff Contract: exact input, exact output, exact constraints |
| **Sequential pipeline overuse** | Each subagent adds latency; 3 sequential subagents = 3x wall clock time | Prefer Fan-Out; Pipeline only when each stage is independently context-heavy |
| **Competing subagents** | Pitting subagents against each other wastes tokens, creates conflicting outputs, and removes user agency | Assign non-overlapping scopes per mandate; if approaches conflict, escalate to user for clarification |
| **No synthesis plan** | Main agent drowns in disconnected subagent outputs | Define Expected Output in every mandate; have integration strategy before spawning |
| **Autonomous conflict resolution** | Main agent picks winners between conflicting subagent outputs without user input | Interactive clarification: present conflict, sources, and trade-offs; let user decide |

---

## 7. Emergency Procedures

### Subagent Failure

If a subagent fails or returns unusable output:

1. **Do NOT** spawn another subagent to fix it (depth violation)
2. Main agent takes over the failed subtask inline, with full context
3. If the subtask is too large for inline work: re-scope into smaller, handoff-ready pieces and delegate fresh

### Conflicting Subagent Results

If subagents return conflicting or divergent results:

1. Present the conflict to the user with full attribution (RAG Pattern)
2. Include: what each subagent concluded, what evidence/method they used, and the trade-offs
3. **Prefer interactive clarification** — let the user adjudicate
4. Only autonomously resolve when: (a) one result is objectively verifiable as correct, AND (b) the other is demonstrably wrong by the same verification standard

### Context Bloat Despite Subagents

If the main agent context is still overloaded despite using subagents:

1. Review mandate quality — are you passing too much context to subagents?
2. Review synthesis strategy — are you failing to discard intermediate outputs after integration?
3. Consider breaking the overall task into sequential macro-phases, clearing context between phases
