# Context Drift Governance

> Priority: P0 (supersedes all other constraints)

## Overview

A structured working loop to ensure reliable in-session memory, constraint compliance, and information generation quality. Based on the principle:
*A file of several hundred bytes is worth a context window of a trillion tokens.*

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

Gather context from all relevant sources:
- **Session contents**: Scan conversation history
- **On-disk files**: ReadFile on relevant project files
- **Online sources**: Web search for external knowledge (apply Reference Verification protocol and RAG Pattern as appropriate)

**Timing**: Acquire always happens immediately before Generate. Never acquire then do unrelated work before generating.

### Phase G — Generate

- Execute the actual work
- Prefer editing existing files over creating new ones
- Keep intermediate files in `/tmp/` subdirectories
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

- **Location**: All session state files under `/tmp/qrh-session/` or similar
- **Cleanup**: Remove `/tmp/qrh-session/` after session completes
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
