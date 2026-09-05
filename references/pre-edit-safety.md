# Pre-Edit Safety

This reference is the sole detailed owner of source selection, workspace classification, pre-edit protection, backup, protection-state, and rollback semantics. Apply it to every task that may read implementation contents or write a workspace artifact in either Mode A or Mode B.

## Table of Contents

1. [Authority and Ordering](#authority-and-ordering)
2. [Scoped Explicit Overrides](#scoped-explicit-overrides)
3. [Source Resolution](#source-resolution)
4. [Repository Classification](#repository-classification)
5. [Protection Decision](#protection-decision)
6. [Backup Rules](#backup-rules)
7. [Protection Status Registry](#protection-status-registry)
8. [Mode A and Mode B Enforcement](#mode-a-and-mode-b-enforcement)
9. [Failure and Rollback](#failure-and-rollback)
10. [Cleanup and Session Termination](#cleanup-and-session-termination)
11. [Reporting Requirements](#reporting-requirements)

## Authority and Ordering

Apply constraints in host priority order. System, developer, safety, permission, workspace, project, and explicit user constraints that outrank this skill remain binding. This skill never grants authority to write, delete, restore, or inspect a path that the host or user has not placed in scope.

Create the minimal governance state before task work. For every task that may read implementation contents or write a workspace artifact, enforce this order:

```text
minimal state -> authority -> scoped explicit overrides -> source proposal
              -> explicit source approval
              -> read-only intent: ready_read -> implementation Acquire
              -> write intent: repository classification -> protection decision
                             -> implementation Acquire -> Generate
```

Before source approval and an accepted read state, limit acquisition to conversation state and path/repository metadata needed for the gate. Do not read implementation contents until the registry contains `ready_compare`, `ready_read`, or a writable ready state for the exact approved scope. Do not enter Generate without a writable ready state. Tasks that will neither read implementation contents nor write artifacts record `not_required`; `ready_read` and `ready_compare` never require a protection backup because they cannot authorize writes.

## Scoped Explicit Overrides

An explicit user direction may override a skill default only within the direction's stated task, workspace, paths, operation, and time scope. Record the exact user wording and resolved scope before relying on it. Never infer an override from silence, generic permission to proceed, an empty response, a timeout, or a system-selected default.

Keep these overrides independent:

- `source_approval_waived`: specifically waives the separate explicit source-approval prompt for one exact absolute existing source, when higher-priority constraints permit the waiver.
- `dirty_state_accepted`: permits work on the identified current dirty Git state.
- `backup_waived`: permits work without a protection backup for the identified scope.

These overrides are independent. Source-approval waiver does not accept dirty state or waive backup. `dirty_state_accepted` does not approve a source or waive backup. `backup_waived`, including wording such as `work with no backup`, does not approve a source or accept a dirty Git state. Require every applicable decision. A broader explicit direction may set more than one only when its wording unambiguously covers each decision.

An override cannot bypass a higher-priority safety, host, permission, workspace, project, or explicit user constraint. If scope or authority is unclear, halt before writing and clarify.

## Source Resolution

Resolve the source of truth before repository protection. This section governs source paths used as the basis of an edit, including duplicate skill trees, generated copies, mirrors, vendored copies, and multiple plausible code roots.

### Source States

Use one of these registry states:

- `not_applicable`: the task will not read implementation contents or write task artifacts.
- `no_path`: no source path was supplied and discovery found no candidate.
- `nonabsolute`: the user supplied a relative path; codework is halted even if a likely base exists.
- `nonexistent`: the resolved absolute path does not exist.
- `proposed`: one exact absolute existing candidate is proposed but not approved.
- `multiple_candidates`: more than one plausible candidate remains.
- `comparison_approved`: explicit authorization covers read-only comparison of a recorded set of exact absolute existing candidates; no candidate is authoritative or writable.
- `approved`: one exact absolute existing source has explicit approval evidence or a specifically permitted source-approval waiver.
- `halted`: source selection cannot safely proceed.

### Candidate Discovery and Labels

Before selection, label every plausible source only as `CANDIDATE`. Do not call a candidate authoritative, original, canonical, installed, mirror, stale, or non-authoritative before the selection decision is recorded.

After explicit approval, label exactly one path `AUTHORITATIVE`. Only then label every rejected candidate `NON_AUTHORITATIVE`, with the exact user instruction or permitted approval-waiver evidence supporting the decision. Never write a `NON_AUTHORITATIVE` path unless a later explicit, in-scope direction approves it for a separate task.

An agent may propose a sole candidate but may never approve it from task context, shell location, naming, repository layout, or its own comparison. An absolute existing directory and an explicit edit direction naming that directory in the same user prompt satisfy source selection and approval; record that prompt verbatim as approval evidence.

### Required Branches

- **No path supplied, no candidate found**: record `no_path`, halt, and request an absolute source path or an authorized discovery scope.
- **No path supplied, one candidate found**: validate that it is absolute and exists, label it `CANDIDATE`, record `proposed`, halt codework, and await explicit user approval of that absolute path.
- **No path supplied, multiple candidates found**: record `multiple_candidates`; enumerate the absolute candidates and do not read implementation contents or edit any candidate before authorized comparison and explicit selection.
- **Nonabsolute path supplied**: always record `nonabsolute` and halt codework. Without reading implementation contents, enumerate zero, one, or multiple resolved absolute candidates that could correspond to the supplied path, then await explicit user selection of an absolute path. Even an obvious workspace base or shell current directory does not authorize resolution or source approval. Zero candidates also halts.
- **Resolved path does not exist**: record `nonexistent` and halt. Do not create the missing source merely to satisfy selection.
- **Multiple explicit paths supplied**: label each `CANDIDATE`, validate each independently, and enter the multiple-candidate branch.
- **A candidate disappears or changes identity during selection**: invalidate the selection evidence, record `halted`, and reacquire.
- **Absolute existing directory plus edit instruction**: when the same explicit user prompt names the absolute existing directory and directs edits there, record `approved`, store the exact instruction, and proceed to repository classification.

### Multiple-Candidate Comparison

When candidates require code-level or artifact-level comparison:

- In Mode B, first obtain explicit authorization to read the exact absolute candidates for comparison, record `comparison_approved`, and establish `ready_compare`; then delegate the comparison as a read-only explorer task. Require evidence such as repository roots, manifests, references, version metadata, hashes, and call sites. The delegate compares candidates but does not edit, approve a source, or prematurely label authority.
- In Mode A, halt by default and ask the user to select or authorize a bounded comparison. Do not autonomously perform a broad code-level comparison.
- An explicit user direction may permit Mode A comparison or approve a candidate only when its scope is clear and higher-priority constraints allow the required reads and decision.

Record comparison authorization separately from source approval. `ready_compare` permits only the authorized read-only comparison and must return to source proposal afterward; it cannot enter Generate or authorize a write. Comparison results may support a proposal, but only explicit user approval or a specifically permitted `source_approval_waived` record may transition the source to `approved`. Record the evidence, exact instruction, and approval actor before applying `AUTHORITATIVE` and `NON_AUTHORITATIVE` labels.

## Repository Classification

Classify each approved authoritative workspace that contains a write target. A source-approved read-only task uses `ready_read` without repository backup classification. Edits spanning multiple repositories or non-Git roots require separate protection records.

### Git Worktree

Resolve the repository root and inspect `git status --porcelain=v1 --untracked-files=all` before the first write. Parse porcelain XY states; do not treat all non-empty output alike.

- `clean`: no reported records.
- `staged_only`: the index column is changed and the worktree column is blank for every record, with no untracked or unmerged records.
- `unstaged`: any tracked record has a changed worktree column, including a staged file modified again after staging.
- `untracked`: any `??` record.
- `unmerged`: any unmerged combination, including `UU`, `AA`, `DD`, `AU`, `UA`, `DU`, or `UD`.

Ignored `!!` paths are outside the default classification unless they are in the approved edit scope. A submodule, nested repository, or linked worktree gets its own classification when it contains a write target.

### Non-Git Workspace

If the authoritative workspace is not inside a Git worktree, record `non_git`. Do not treat a Git repository found only in a parent or sibling path as protection for the selected workspace.

### Classification Failure

If the repository root cannot be resolved, status cannot be read, or classification is ambiguous, record `classification_failed` and halt before writing. An explicit in-scope user direction may authorize non-Git-style backup protection or waive backup, but it cannot bypass unavailable read permission or another higher-priority constraint.

## Protection Decision

Use only these gate states:

- `not_required`: neither implementation-oriented reads nor workspace writes will occur.
- `pending`: source, classification, override, or backup work remains.
- `deferred_dirty`: dirty Git state requires user action or acceptance.
- `ready_compare`: exact absolute candidates, comparison-read approval, and read-only scope are recorded; no writes are permitted.
- `ready_read`: one exact absolute existing source is `approved`, the implementation-read scope is recorded, and no workspace write is authorized.
- `ready_git`: source state is `approved`, Git state is clean or staged-only, and the approved scope is recorded.
- `ready_backed_up`: source state is `approved`, and the non-Git or accepted dirty Git scope has a verified registered backup.
- `ready_no_backup`: source state is `approved`, an explicit backup waiver covers the exact scope, and any required dirty-state acceptance is also present.
- `halted`: no valid write path remains.

Apply this decision table:

| Intent or workspace state | Default | Valid continuation |
|---|---|---|
| Approved source, read-only review | No repository classification or backup | `ready_read` |
| Git clean or staged-only | No backup required | `ready_git` |
| Git unstaged, untracked, or unmerged | Notify user to stage/stash; defer | Accept dirty state, then back up or separately waive backup |
| Non-Git | Back up approved edit scope | Verified backup or explicit backup waiver |
| Classification failed | Halt | Explicit authorized fallback, when higher-priority constraints permit |

No protection outcome may become `ready_git`, `ready_backed_up`, or `ready_no_backup` while source state is `no_path`, `nonabsolute`, `nonexistent`, `proposed`, `multiple_candidates`, or `halted`. Source state may become `approved` only from explicit approval evidence, or from a `source_approval_waived` override that names one exact absolute existing source and is permitted by higher-priority constraints.

The complete source transition is:

```text
no_path | nonabsolute | nonexistent | multiple_candidates | proposed
    -> no writable transition
multiple_candidates + explicit bounded comparison-read approval
    -> comparison_approved + ready_compare -> read-only evidence -> proposed
proposed + explicit approval evidence
    -> approved
proposed + specifically permitted source_approval_waived for the same exact absolute path
    -> approved
approved + read-only intent
    -> ready_read -> read-only completion
approved + repository/protection decision
    -> ready_git | ready_backed_up | ready_no_backup
ready_read + later write intent
    -> pending -> repository/protection decision
    -> ready_git | ready_backed_up | ready_no_backup
```

Thus neither an unresolved source, an agent proposal, comparison evidence, nor `ready_read` has a direct edge to a writable operation.

Before any implementation read, confirm `ready_compare`, `ready_read`, or a writable ready state covers that target. Before any write, confirm a writable ready state covers it. A newly discovered target invalidates readiness for that target until its source approval and, for write intent, protection are expanded. Do not reclassify agent-created Git changes as pre-existing dirtiness; preserve the initial porcelain baseline and track later agent writes separately.

## Backup Rules

Create protection backups under the active session's OS-temporary directory unless a higher-priority instruction specifies another safe location. Use an absolute, unique path and preserve the approved edit scope's relative structure and relevant metadata.

For every backup:

1. Record the authoritative workspace and exact covered paths.
2. Copy every existing target before its first write.
3. Record planned targets that do not yet exist in a manifest so later-created paths are identifiable.
4. Verify that the backup and manifest are readable and cover the declared scope.
5. Register the absolute backup and manifest paths before setting `ready_backed_up`.
6. Report the backup path immediately after verification.

A partial, unreadable, ambiguous, or failed backup does not satisfy the gate. Record `backup_failed` and halt by default. Continue only if an explicit `backup_waived` override covers the affected scope; report the failed backup attempt before proceeding.

Registered protection backups are recovery aids, not permission to restore automatically.

## Protection Status Registry

Store the registry in the repository working directory under `.agent/state/protection-status.md` (durable). Preserve it through normal cleanup. Use this minimum schema:

```markdown
# Protection Status

Session: [stable session id]
Task: [task id]
Authority constraints: [resolved hierarchy and limiting constraints]

## Source
State: [source state]
Candidates: [absolute path + CANDIDATE label]
Proposed: [absolute existing path + proposal evidence]
Approved: [absolute existing path + AUTHORITATIVE label]
Approval status: [pending | explicit | waived]
Approval evidence: [exact user instruction/message reference, or exact permitted waiver + authority]
Comparison-read authorization: [none | exact instruction + scope]
Rejected: [absolute path + NON_AUTHORITATIVE label + evidence]

## Workspace
Root: [absolute path]
Repository: [git | non_git | classification_failed]
Baseline: [clean | staged_only | unstaged | untracked | unmerged]
Baseline evidence: [command/result reference]

## Overrides
Source approval waived: [yes/no + exact wording + exact absolute source + scope + permitting authority]
Dirty state accepted: [yes/no + exact wording + scope]
Backup waived: [yes/no + exact wording + scope]

## Gate
State: [gate state]
Intent: [metadata_only | compare_read | read_only | write]
Read scope: [absolute paths]
Edit scope: [absolute paths]
Last validated: [time/checkpoint]

## Backups
- Path: [absolute path]
  Manifest: [absolute path]
  Scope: [paths]
  Status: [created | verified | failed | retained | deleted | delete_failed | missing]
  Reported: [immediate yes/no; final yes/no]

## Writes
- Path: [absolute path]
  Writer: [Mode A agent or Mode B worker]
  Before-state: [hash/mtime/nonexistent]
  After-state: [hash/mtime]
```

Maintain a session CAS register (edit-cas-gate.md) as the active pre-write baseline; these Before/After fields are its audit trail.

Never erase prior status entries to make the current state appear clean. Append or update status and preserve the evidence trail across retries, handoffs, cleanup, and terminal failure.

## Mode A and Mode B Enforcement

In Mode A, the active agent reads and validates the registry immediately before each implementation read and write. Large or newly expanded read scopes re-enter source approval; any new write intent re-enters repository classification and the protection decision.

In Mode B, the supervisor completes or explicitly assigns only metadata preflight before approval, then passes the registry path and permitted implementation-read/edit scope to every worker. Each worker must read the registry and confirm an approved source plus a valid protection state before reading implementation contents or writing. A worker, replacement worker, chunk executor, or inline takeover must not inherit permission from prompt prose alone.

`ready_compare` permits only the explicitly bounded read-only comparison of its recorded candidates. `ready_read` permits implementation-oriented reads of one approved source but never a write. The writable states are only `ready_git`, `ready_backed_up`, and `ready_no_backup`, and each requires source state `approved` plus the full repository protection decision. `not_required`, `pending`, `deferred_dirty`, and `halted` prohibit implementation reads and writes.

If write intent appears during `ready_read`, stop before the first write, set the gate back to `pending`, classify the repository, and complete the normal protection decision. Source approval may be reused only while its exact path and scope remain valid; `ready_read` itself contributes no backup waiver, dirty-state acceptance, or writable readiness.

Before a sequential chunk write, validate both the Protection Status Registry and the Artifact State Log. A mismatch, external change, stale hash, source change, or scope expansion invalidates the affected readiness and returns to Acquire/protection. Apply the general write-time CAS gate (edit-cas-gate.md) to non-chunked writes as well.

## Failure and Rollback

Classify verification and debugging failures before retrying:

- `recoverable`: a safe, in-scope diagnostic or correction remains and the declared retry budget is not exhausted.
- `unrecoverable`: the retry cap is exhausted, required authority or dependencies are unavailable, continuation would breach scope or constraints, state cannot be classified safely, or no safe diagnostic next step remains.

For a recoverable failure, record the attempt and return to Acquire or Generate only while the protection state remains valid. For an unrecoverable failure, stop all further modification, mark the task incomplete or halted, preserve the current workspace and registry, and report the failure and every registered backup path.

Never automatically restore, revert, reset, delete agent changes, or otherwise roll back after failure. Rollback is a new write operation requiring an explicit user instruction, authority checks, a fresh protection decision, and exact rollback scope.

## Cleanup and Session Termination

Normal cleanup operates only on exact paths registered by the active session as cleanup-eligible. Never infer cleanup targets from directory scans, globs, naming patterns, another session's registry, or general statements about temporary files.

Protection backups and `protection-status.md` are excluded from normal cleanup. Preserve them and report their retained paths even when verification passes.

An intentional, operative user directive `terminates session` triggers protection-backup cleanup only when it instructs the agent to end the active session and clean its backups. Incidental quotation, documentation, examples, discussion of the phrase, or text copied from another source does not trigger cleanup.

When the directive applies:

1. Read the active session's preserved registry.
2. Select only exact backup and manifest paths registered to that active session.
3. Reject nonabsolute, unregistered, mismatched-session, broad, or ambiguous targets.
4. Clean each selected path without expanding its scope.
5. After every attempt, update its registry status to `deleted`, `delete_failed`, or `missing`.
6. Preserve the updated `protection-status.md` after cleanup and report every result.

An explicit user direction may retain, relocate, or clean a registered backup within scope, subject to higher-priority constraints. Normal task completion alone is not a termination cleanup directive.

## Reporting Requirements

Report protection results visibly:

- Report dirty-state deferral and the stage/stash action required.
- Report every proposed source and whether approval is pending, explicit, or specifically waived.
- Report each verified backup path immediately after creation.
- Report a backup failure before asking for or applying a later waiver.
- Report the exact scope and effect of every applied override.
- Report every backup path again in the final, halted, interrupted, or failed outcome, regardless of self-check results.
- If no backup exists because it was unnecessary or explicitly waived, report that status rather than inventing a path.
- Report the preserved registry path and cleanup statuses at session termination.

Before handing off or completing, verify that every implementation read names `ready_compare`, `ready_read`, or a writable ready state; every write names a writable ready state; and every backup record has both immediate and final reporting status.
