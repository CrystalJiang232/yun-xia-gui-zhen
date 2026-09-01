# Context Drift Governance

> Priority: P0 within this skill. Higher-priority system, developer, safety, permission, user, workspace, and project constraints remain authoritative.

## Table of Contents

- Overview
- The CTAGV Working Loop
- Pre-Work Setup
- Phase-by-Phase Execution Rules
- Mode B Extension
- Verification Hooks Pattern
- Verification Execution Log
- File Hygiene
- Effort & Cost Budgeting
- Integration with Other Protocols
- Emergency Pause

## Overview

A structured working loop to ensure reliable in-session memory, constraint compliance, and information generation quality. Based on the principle:
*A file of several hundred bytes is worth a context window of a trillion tokens.*

### Compaction Anchors

If the host environment performs history compaction, task goals and hard constraints MUST be written to the external state files (constraints.md, todo.md) BEFORE compaction occurs. Anchor summaries may compress narrative detail but never compress goals or hard constraints.

**Context engineering relation**: This file is the session-scope slice of [context engineering](context-engineering.md). Its compaction anchors and memory hygiene implement the Compress and Write operations.

## The CTAGV Working Loop

Every task must follow this five-phase cycle visibly in-session. Minimal state initialization and a mandatory preflight gate occur before Phase A whenever implementation reads or workspace writes are possible:

```
[Initialize State] → Constraints → Task → [Metadata Preflight + Protection Gate]
                   → Acquire → Generate → Verify
```

| Phase | Action | Must Show |
|-------|--------|-----------|
| **C**onstraints | Read constraint file | Explicit ReadFile action on constraints file |
| **T**ask | Read task from TODO | Explicit ReadFile on TODO file for current task |
| **Preflight** | Resolve authority and protection without implementation reads | Valid state in `protection-status.md` |
| **A**cquire | Gather approved implementation context | ReadFile, web search, or session scan within approved scope |
| **G**enerate | Execute work | File write, code execution, modification |
| **V**erify | Check against verification hooks | Explicit thinking or action on verification |

All five phases and every applicable protection transition must use actual tool actions visible in-session. No simulated or implied steps. [pre-edit-safety.md](pre-edit-safety.md) is the sole detailed owner of source approval, protection, backup, cleanup, and terminal-failure semantics.

## Pre-Work Setup (Required Before ANY Task)

Before task work or implementation reads, create the four minimal state files below. Populate source approval and protection fields through metadata-only preflight before reading implementation contents or writing task artifacts.

### 1. Constraints File (`/tmp/qrh-session/constraints.md`)

Classify constraints as global or task-specific. Apply **Explicit Constraint** pattern: surface all hard, soft, and negative constraints:

```markdown
# Session Constraints

## Global (apply to all tasks)
- [HARD] Constraint 1
- [SOFT] Constraint 2
- [NEGATIVE] Constraint 3

## Task-Specific

### Task: [task-name]
- [HARD] Constraint A
- [SOFT] Constraint B
```

### 2. TODO File (`/tmp/qrh-session/todo.md`)

Comprehensive task list with full detail:

```markdown
# Session TODO

## Task 1: [Title]
**Status**: pending | in_progress | blocked | incomplete | halted | completed
**Dependencies**: none | Task X

### Details
[Full context needed to accomplish this task]

### Context
[Session contents, file paths, relevant background]

### Verification
[How to verify this task is correctly completed]
```

### Channel & Deferred-State Fields

The constraints file additionally carries `CHANNEL: available|absent|unknown` (set at skill load, per SKILL.md entry point) and `CHANNEL_PREFERENCE: default|prefer-ask|no-ask` (updated whenever the user expresses one). When a round is halted per Clarification Channel Governance §A (clarification-protocol.md), append a `next_round_proposal` block to the constraints file:

```markdown
## Next-Round Proposal (UNEXECUTED)
Basis: decisions [D1..Dn] (resolved points above)
Deferred points: [list]
Proposed work upon resolution: [concrete proposal]
Status: DO NOT EXECUTE until deferred points are resolved
```

On any new round opening with an `UNEXECUTED` next-round proposal, read it before planning; executing it before the linked deferred points resolve is a protocol violation.

### 3. Verification Hooks File (`/tmp/qrh-session/verification.md`)

Designated by the user or derived from constraints. Resolve hook precedence by instruction priority first, then applicable scope, then recency at equal priority and scope. Use strictness only to choose among equally authorized, compatible hooks; strictness never overrides a higher-priority, narrower, or newer conflicting instruction. Apply **Verification Hooks** pattern: embed specific, checkable conditions:

```markdown
# Verification Hooks

## Per-Task Hooks

### Task 1: [Title]
- [ ] Check: [specific verifiable condition]
  - Verification method: [how to check]
  - Expected result: [what passes looks like]
- [ ] Check: [specific verifiable condition]
  - Verification method: [how to check]
  - Expected result: [what passes looks like]

## Global Hooks
- [ ] All files written to correct paths
- [ ] No syntax errors in generated code
- [ ] Session state files updated
- [ ] All hard constraints from constraints.md satisfied
- [ ] Every implementation read and workspace write consumed an accepted state from `protection-status.md`
- [ ] FINAL: File hygiene and cleanup conform to [pre-edit-safety.md](pre-edit-safety.md)
```

### 3.1 Missing-Field Log (Missing-Field Protocol activations)

When the Missing-Field Protocol (SKILL.md) activates, record each activation in session state — append to the constraints file or a dedicated `missing-field-log.md` in the session directory:

```markdown
## Missing-Field Log — Activation <id>
Field: <name or description>
Signals: incomplete sentence | invalid JSON/structured payload | missing parameter | out-of-range value
Status: awaiting | deferred | restored | waived
Attempts: <N> — one line per round (response summary + still-missing evidence)
Waiver: none | <exact wording + scope + mode>
Disclosure: interpreted semantic / suggested missing field / completed semantic (assumed)
```

Reference this log in every output until the activation is restored or waived. The wait loop's deferral on empty/system-default/timeout responses follows Clarification Channel Governance §A (clarification-protocol.md): mark deferred, halt the round, persist the UNEXECUTED next-round proposal, and await the user.

### 4. Protection Status Registry (`/tmp/qrh-session/protection-status.md`)

Create and preserve the registry defined in [pre-edit-safety.md](pre-edit-safety.md). Initialize it minimally before task work, then record explicit source approval and protection readiness before any implementation read or task-artifact write.

### 5. State Schema Discipline

Give the session state files a **contract shape** to prevent state explosion and context overflow:

- Define an explicit, typed **state schema** (explicit fields and types) that lists **only the necessary variables** the task actually reads or writes; omit derived or redundant data.
- Define **update rules** per field (append vs last-value-wins) so concurrent or repeated updates merge predictably instead of clobbering or exploding state.
- Treat the schema as a **validation boundary**: a missing or unexpected field fails fast rather than drifting silently.
- Keep stored state minimal by design; add a field only when a phase genuinely consumes it.

## Phase-by-Phase Execution Rules

### Phase C — Constraints

- Read the constraints file at the start of every single task
- Repetitive reading is not redundant; it is required for reliability
- Explicitly show the reading process in-session
- If constraints conflict with current task needs, raise clarification

### Phase T — Task

- Read the TODO file to identify the current task
- Mark task as `in_progress` before beginning
- Only ONE task may be `in_progress` at a time
- If blocked, mark as blocked with reason and spawn new task for blocker

### Metadata Preflight and Protection Gate

- Apply [pre-edit-safety.md](pre-edit-safety.md) before implementation Acquire or any task-artifact write
- Limit preflight reads to conversation and path/repository metadata authorized for source proposal and protection
- Do not continue while source approval is unresolved or merely proposed, except for an explicitly authorized `ready_compare` read-only comparison
- `ready_compare` permits bounded candidate comparison; `ready_read` permits review of one approved source; neither permits writes
- The writable states are only `ready_git`, `ready_backed_up`, and `ready_no_backup`, each backed by the source-approval and repository-protection evidence required by the detailed owner

### Phase A — Acquire

After the gate passes, inject only the minimal high-signal context needed for the current step. Gather implementation context only within the accepted scope. Acquire under `ready_compare` or `ready_read` is read-only and cannot enter Generate. Acquire under a writable ready state happens immediately before Generate; stale, expanded, or newly writable scope re-enters preflight.

### Phase G — Generate

- Execute the actual work
- Consume `ready_git`, `ready_backed_up`, or `ready_no_backup` for every Generate scope; `ready_compare` and `ready_read` never enter Generate
- Prefer editing existing files over creating new ones
- Before any write to a file already written this session, re-hash and compare against the session CAS register ([edit-cas-gate.md](edit-cas-gate.md)); mismatch ⇒ re-read before editing (whole file < 100 KB, targeted section otherwise; escalate for core files). Prefer scoped edits; global substitution only after a full re-read
- Keep intermediate files in the OS-temp session subdirectory (see File Hygiene); redirect code-work byproducts there where the toolchain allows, else record them in the Cleanup Registry
- Do not pollute the workspace with temporary files
- Show generation actions explicitly

### Phase V — Verify

- Consult verification hooks file for current task
- Explicitly show thinking and/or action process
- Check each hook conditionally
- Apply **Chain-of-Reasoning Trigger** for complex verification decisions
- Apply the retry and terminal-failure transitions owned by [pre-edit-safety.md](pre-edit-safety.md)
- Do not mark task complete unless all hooks pass

## Mode B Extension — Swarm State & Bounded Verification

When subagent orchestration (Mode B) is active, extend the CTAGV state files and verification loop as follows:

- **Task Ledger + Progress Ledger**: when orchestrating subagents, the constraint/TODO files additionally track per-subagent status and last-update tick.
- **Stall detection**: no progress update from a subagent after N actions/checkpoints triggers replan, re-delegation, or inline takeover; every replacement or takeover inherits the preflight contract in [pre-edit-safety.md](pre-edit-safety.md).
- **Bounded verification**: max 2 refine-retry rounds per verification loop; non-convergence follows the terminal transition owned by [pre-edit-safety.md](pre-edit-safety.md).
- **Conflict adjudication**: autonomous adjudication only where objectively verifiable criteria exist AND the user has pre-approved it; otherwise escalate to interactive clarification.
- **Artifact State Log (required for chunked edits)**: when a large edit/write task is split into sequential chunks (subagent-orchestration.md §5 Pattern F), the state files carry an artifact-state log shared across chunk executors:

```markdown
## Artifact State Log — [task name]

| File | Last chunk | Hash/mtime after write |
|------|-----------|------------------------|
| [path] | chunk N | [hash or mtime] |

Completed chunks: [one-line outcome each]
Decisions: [D1: ...]
Symbols introduced: [names + locations, so later chunks never reference unknown code]
Protection registry: [path + valid gate state + approved edit scope]
```

Each chunk executor MUST consume an accepted Protection Status Registry state and follow the staleness contract in [pre-edit-safety.md](pre-edit-safety.md) before implementation reads or writes.

## Mode A — Iteration Caps & Termination Conditions

For Mode A (single-agent CTAGV), each task must set an explicit satisfiable termination condition and a maximum iteration/step cap before execution begins:

- **Definition of Done (termination condition)**: a concrete, satisfiable criterion defining when the task is done, written in prose (what counts as done, what counts as blocked) and tied to the task's verification hooks. The loop stops on DoD satisfaction, on a no-progress signal, or on the step ceiling — never by continuing indefinitely.
- **Iteration/step cap**: a hard maximum on loop iterations or steps, set through the host framework's native limit when available (e.g., a recursion/step limit, `max_turns`). Derive the ceiling from the task's declared step estimate (`ceiling = base + margin × estimated_steps`, with a global hard max) rather than a hardcoded vendor integer; coefficients are skill-level tunable defaults. Hitting the cap follows the terminal transition owned by [pre-edit-safety.md](pre-edit-safety.md).
- **Working-set token budget**: keep the run's working set within a percentage of the model's context window (e.g., ≤ ~90%), compacting (summarizing) or trimming history when the threshold is crossed and reserving headroom for output; keep per-response `max_tokens` (a vendor parameter) conceptually separate. Percentages are tunable defaults, not authoritative.
- **Chunked execution for large edits**: a large single-session edit/write task is split into ordered chunks rather than carried in one stretch. Between chunks, checkpoint decisions and per-file state (hash/mtime) to the state file, and re-read the target file before each chunk write — the Mode B Artifact State Log's staleness guard, applied inline. Context drift makes an un-checkpointed long edit session prone to the same stale-overwrite failure as unlogged sequential subagents — the general single-agent analogue is [edit-cas-gate.md](edit-cas-gate.md).

## Verification Hooks Pattern (Extended)

### What Makes a Good Verification Hook

A verification hook must be:
- **Specific**: Not "check the code works" but "run `pytest tests/test_feature.py` and confirm all assertions pass"
- **Checkable**: Must have a binary pass/fail criterion
- **Automatable where possible**: Prefer tool-executable checks over manual review
- **Tied to constraints**: Each hard constraint should have at least one verification hook

### Hook Types

| Type | Description | Example |
|------|-------------|---------|
| **Output Check** | Verify file exists at correct path | `ls /expected/path/file.md` returns the file |
| **Syntax Check** | Verify code is syntactically valid | `python -m py_compile script.py` exits 0 |
| **Behavioral Check** | Verify code behaves correctly | `pytest test_module.py::test_case` passes |
| **Constraint Check** | Verify hard constraints are met | File size < 100KB, uses only stdlib, etc. |
| **Semantic Check** | Verify output meaning is correct | Review output against user's explicit requirements |

### Hook Execution

```markdown
## Verification Execution Log

### Task: [name]
- [x] Hook 1: [description]
  - Method: [command or action taken]
  - Result: PASS / FAIL
  - Notes: [any observations]
- [x] Hook 2: [description]
  - Method: [command or action taken]
  - Result: PASS / FAIL
  - Notes: [any observations]

**Overall**: PASS / FAIL — Completing / Retrying within cap / Halting
```

## File Hygiene

- Put governance state and intermediates in the permitted active-session temporary location by default, and register their provenance and status.
- Apply cleanup, backup retention, termination directives, and status preservation only as specified by [pre-edit-safety.md](pre-edit-safety.md); do not introduce a second cleanup algorithm here.
- **Workspace**: Only final deliverables in the workspace
- **No pollution**: Never write intermediate state to the project directory

**Memory hygiene (lifecycle rules for stored state):**

- **Short-term vs long-term**: keep short-term (thread-scoped) memory trimmed; promote only durable, structured facts to long-term storage.
- **Summarize, don't retain verbatim**: when history approaches the working-set budget, replace older turns with a running summary (compaction); keep the summary plus recent raw turns.
- **Clip/trim**: drop or edit old turns including tool results; trim to the token budget before each call.
- **TTL/expiry**: apply a time- or size-based expiry to stored fragments and tool results so stored state cannot grow without bound.
- These rules are tunable per model/context; mark thresholds as defaults, not authoritative.

## Effort & Cost Budgeting

Make cost/latency a first-class governance item for long or expensive tasks:

- Set an **explicit token/cost budget** for the task (track tokens and cost per call/run) with a ceiling and alert.
- **Model tiering**: route simple subtasks to small/cheap models and escalate to a larger model only when the task requires it.
- **Monitor** tokens, call counts, and latency; act on budget alerts rather than discovering spend after the fact.
- **Guard** runaway spend with a circuit breaker on repeated failures and by caching reused context; these are tunable defaults, not authoritative values.

## Integration with Other Protocols

| Protocol | Integration Point |
|----------|-------------------|
| Pre-Edit Safety | Mandatory transition before Phase A for implementation reads and workspace writes |
| Clarification Protocol | Phase C (conflicts trigger clarification) and Phase T (ambiguous tasks) |
| Reference Verification | Phase A (external source acquisition) |
| RAG Pattern | Phase A (enhanced retrieval) and Phase G (grounded generation) |
| Explicit Constraint | Pre-work Setup (constraints file) and Phase V (constraint verification) |
| Chain-of-Reasoning | Phase V (complex verification decisions) and Phase T (task decomposition) |
| RTCF Template | Phase T (task understanding before execution) |

## Emergency Pause

If at any point you find yourself:
- Repeating "but wait"
- Making assumptions to proceed
- Uncertain about constraint applicability
- About to skip a verification hook

Pause immediately. Re-read the constraints and Protection Status Registry, then apply the halt/report contract in [pre-edit-safety.md](pre-edit-safety.md). Do not proceed with unverified assumptions.
