# Context Drift Governance

> Priority: P0 (supersedes all other constraints)

## Overview

A structured working loop to ensure reliable in-session memory, constraint compliance, and information generation quality. Based on the principle:
*A file of several hundred bytes is worth a context window of a trillion tokens.*

### Compaction Anchors

If the host environment performs history compaction, task goals and hard constraints MUST be written to the external state files (constraints.md, todo.md) BEFORE compaction occurs. Anchor summaries may compress narrative detail but never compress goals or hard constraints.

## The CTAGV Working Loop

Every task must follow this five-phase cycle visibly in-session:

```
Constraints → Task → Acquire → Generate → Verify
```

| Phase | Action | Must Show |
|-------|--------|-----------|
| **C**onstraints | Read constraint file | Explicit ReadFile action on constraints file |
| **T**ask | Read task from TODO | Explicit ReadFile on TODO file for current task |
| **A**cquire | Gather context (session, disk, web) | ReadFile, web search, or session scan |
| **G**enerate | Execute work | File write, code execution, modification |
| **V**erify | Check against verification hooks | Explicit thinking or action on verification |

All five phases must use actual tool actions visible in-session. No simulated or implied steps.

## Pre-Work Setup (Required Before ANY Task)

Before beginning the first task, create three files:

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
**Status**: pending | in_progress | completed
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

Designated by user or derived from constraints (stricter wins). Apply **Verification Hooks** pattern: embed specific, checkable conditions:

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
- [ ] FINAL: Temporary files cleaned up — ALL intermediates incl. code-work byproducts and Cleanup Registry paths; externally-depended files (db/log) exempt; when unsure a file is safe to delete, leave it. Default behavior; waived or relocated only by explicit user instruction (record waiver in constraints file)
```

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

### Phase A — Acquire

Inject only the minimal high-signal token set needed for the current step; just-in-time retrieval is preferred over preloading (context-rot evidence).

Gather context from all relevant sources:
- **Session contents**: Scan conversation history
- **On-disk files**: ReadFile on relevant project files
- **Online sources**: Web search for external knowledge (apply Reference Verification protocol and RAG Pattern as appropriate)

**Timing**: Acquire always happens immediately before Generate. Never acquire then do unrelated work before generating.

### Phase G — Generate

- Execute the actual work
- Prefer editing existing files over creating new ones
- Keep intermediate files in the OS-temp session subdirectory (see File Hygiene); redirect code-work byproducts there where the toolchain allows, else record them in the Cleanup Registry
- Do not pollute the workspace with temporary files
- Show generation actions explicitly

### Phase V — Verify

- Consult verification hooks file for current task
- Explicitly show thinking and/or action process
- Check each hook conditionally
- Apply **Chain-of-Reasoning Trigger** for complex verification decisions
- If verification fails: mark task incomplete, return to Acquire or Generate
- Do not mark task complete unless all hooks pass

## Mode B Extension — Swarm State & Bounded Verification

When subagent orchestration (Mode B) is active, extend the CTAGV state files and verification loop as follows:

- **Task Ledger + Progress Ledger**: when orchestrating subagents, the constraint/TODO files additionally track per-subagent status and last-update tick.
- **Stall detection**: no progress update from a subagent after N actions/checkpoints → forced replan, re-delegation, or inline takeover.
- **Bounded verification**: max 2 refine-retry rounds per verification loop; on non-convergence, escalate to the user (interactive clarification) rather than looping or autonomously adjudicating.
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
```

Each chunk executor MUST, before writing any shared file, re-read it or compare its hash/mtime against this log; a mismatch means STALE — abort the chunk and report back. Blind overwrites are a protocol violation.

## Mode A — Iteration Caps & Termination Conditions

For Mode A (single-agent CTAGV), each task must set an explicit satisfiable termination condition and a maximum iteration/step cap before execution begins:

- **Termination condition**: a concrete, satisfiable criterion defining when the task is done (tied to the task's verification hooks).
- **Iteration/step cap**: a hard maximum on loop iterations or steps. The cap is an alarm, not a cure — hitting it triggers replan or escalation to interactive clarification, mirroring the Mode B bounded-verification rule, rather than continued looping.
- **Chunked execution for large edits**: a large single-session edit/write task is split into ordered chunks rather than carried in one stretch. Between chunks, checkpoint decisions and per-file state (hash/mtime) to the state file, and re-read the target file before each chunk write — the Mode B Artifact State Log's staleness guard, applied inline. Context drift makes an un-checkpointed long edit session prone to the same stale-overwrite failure as unlogged sequential subagents.

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

**Overall**: PASS / FAIL — Proceeding / Returning to Generate
```

## File Hygiene

- **Location**: Session state files and intermediate files go to the OS-specific temporary directory by default — `/tmp` on Linux, `$TMPDIR` on macOS (falling back to `/tmp`), `%TEMP%` on Windows — under a session subdirectory (e.g. `qrh-session/`). Landing them anywhere else requires explicit user specification.
- **Code-work intermediates**: when code work or program execution generates byproducts (compiler/interpreter/build artifacts, caches, downloaded fixtures), redirect them to the temp directory where the toolchain allows (environment variables, output flags, working-directory choice); where redirection is not possible, record each path in the state file's Cleanup Registry (below) for cleanup reference.
- **Exemption — externally-depended files**: files that external processes or later user-instructed runs depend on — notably database files and log files produced during user-instructed program execution — are NOT intermediate files; they stay in place and are excluded from cleanup.
- **Cleanup Registry**: the state file carries a running block:

```markdown
## Cleanup Registry
- [path] — [origin: which task/step produced it] — [ ] cleaned
```

- **Cleanup**: temporary files are cleaned up as the FINAL verification hook (see Verification Hooks) — final so that verification never depends on files already deleted. The duty covers ALL generated files: code-work byproducts and intermediates alike. When unsure whether an auto-generated file is safe to delete (unidentifiable files beyond common byproducts), default to NOT cleaning it up. Waivers: explicit user instruction may waive cleanup entirely or relocate it (e.g. "keep the build dir for inspection"); record any waiver in the constraints file.
- **Workspace**: Only final deliverables in the workspace
- **No pollution**: Never write intermediate state to the project directory

## Integration with Other Protocols

| Protocol | Integration Point |
|----------|-------------------|
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

Pause immediately. Re-read constraints file. Enter Clarification Protocol if needed. Do not proceed with unverified assumptions.
