# State Archive Lifecycle

This file is the single owner of the distinction between current governance state, durable distilled memory, and archived session evidence.

## Table of Contents

- Purpose
- Storage Layout
- Lifecycle States
- Archive Eligibility
- Task Completion Review
- New-Session Detection
- Archive Procedure
- External References
- Existing-State Migration
- Retention Review
- Utility
- Integration Boundaries

## Purpose

Keep the default state-reading path small without discarding recoverable audit evidence.

`.agent/state/` contains current truth only.

`.agent/memory/` contains compact, reviewed, reusable project knowledge.

`.agent/archive/` contains reviewed session evidence retained for audit and later retrieval.

An archive is not a deletion queue.

Historical evidence remains retained unless the user explicitly approves an exact deletion through [pre-edit-safety.md](pre-edit-safety.md).

## Storage Layout

```text
.agent/
  state/
    constraints.md
    todo.md
    verification.md
    protection-status.md
    pending-clarifications.md
    session-status.md
  memory/
    project.md
    decisions.md
    workflows.md
  archive/
    retention.md
    YYYY-MM/
      <session-id>/
        manifest.md
        snapshot/
          <reviewed source files>
```

The canonical hot files remain in `.agent/state/` so existing workflows and path references stay stable.

Historical round narratives, completed verification blocks, finished protection registries, resolved clarification rounds, implemented proposals, superseded plans, and obsolete external references move to the session archive.

Treat `.agent/archive/` as outside the default working set.

Do not load, search, grep, glob, index, enumerate, or cite archived state files by default.

If historical evidence appears useful, ask the user for explicit permission to search a named archive scope for the current task.

A general permission to continue, the agent's judgment that a lookup is necessary, prior familiarity with an archive, or discovery of its path is not permission to inspect it.

After permission, read only the approved scope and record why the lookup was needed.

Treat every match as historical evidence, not current truth.

Before using an archived record to support a present-state claim, verify that claim against current `.agent/state/` and the relevant live files or repository evidence.

If current and archived evidence conflict, current live evidence wins and the archived record is disclosed as stale; if no current evidence exists, mark the claim unverified rather than presenting archive content as current state.

## Lifecycle States

Work completion and archival are independent fields.

```text
work_status:
  pending | in_progress | blocked | incomplete | completed

archive_status:
  active | pending_review | held | reviewed | archived
```

- `work_status=completed` means the task's verification hooks have executed with PASS.
- `archive_status=pending_review` means completed work still occupies hot state and is waiting for close-out review.
- `archive_status=held` means the user postponed review.
- `archive_status=reviewed` means the user approved the archive manifest but the move has not finished.
- `archive_status=archived` may appear only in the archive manifest.

A completed task is not automatically archived.

An active task is not archived.

## Archive Eligibility

A record remains in hot state only when at least one condition holds:

1. It is required by the current task.
2. It affects future agent behavior or obligations.
3. It affects safety, permissions, authorization, recovery, or data-loss prevention.
4. It is a standing durable rule or reviewed memory entry.
5. It is required to control the current migration or archival operation.

Otherwise, the record is archive-eligible after the source snapshot exists.

The following are specifically archive-eligible:

- completed tasks and their detailed narratives;
- resolved clarifications and later-superseded awaiting/deferred text;
- obsolete protection registries and write audits;
- implemented proposals and completed plans;
- unexplained or accidental session-local operations that are not workflow-critical;
- optional editorial follow-ups that do not block current or future workflow;
- duplicate-copy maintenance for mirrors, installed copies, or backup trees;
- stale Git-status statements that have been superseded by later history.

An item concerning interrupt recovery, terminal escalation, safety, permissions, rollback, or another workflow-critical control remains active even when old.

Never infer disposition from age or keyword matching alone.

Read any later resolution that disposes of the earlier status.

## Task Completion Review

After a task reaches `work_status=completed`, recommend one close-out review:

> The task is verified complete. Before archiving its state, please review the completion evidence and classify any remaining exceptions as workflow-critical or archive-eligible. If correct, reply `archive <task-id>`; reply `hold <task-id>` to keep it active.

The review checks:

1. Every completion hook has executed PASS evidence.
2. Every remaining hot record satisfies the Archive Eligibility test.
3. Workflow-critical items have been copied into current state or durable memory.
4. The archive manifest names every source file in the snapshot.
5. No current task or current-operation control file is being archived.

Archival requires explicit user confirmation.

A recommendation, timeout, empty response, or generic permission to continue is not archival approval.

## New-Session Detection

On state load, inspect only active `todo.md` records for entries with `work_status=completed` and `archive_status=pending_review`; never scan the archive to perform this check.

Emit at most one batched hint per session:

> Active state contains `<N>` verified-complete tasks awaiting archival review: `<ids>`. They do not block the current task. Reply `review completed` to review them, or leave them unchanged to continue without interruption.

Do not repeat the hint for every item, task, or turn.

Do not call these records stale.

They are complete records whose close-out disposition is pending.

If the user continues without responding, proceed with the current task and leave the records unchanged.

## Archive Procedure

1. Run `scripts/state_archive.py prepare-session` without `--apply`.
2. Inspect the reported source and destination file list.
3. Confirm that every non-archived record satisfies the Archive Eligibility test.
4. Apply the same command with `--apply --confirm-session <session-id>`.
5. Verify the archive manifest and snapshot hashes.
6. Remove or replace the reviewed hot-state files.
7. Run `status` and `check-todo` from `scripts/state_archive.py`.

A reviewed batch may archive multiple completed sessions at once.

Every archive manifest records:

- session ID and source commit;
- review evidence and archive status;
- exact source and archived paths;
- SHA-256 hashes;
- external references recorded as historical context;
- promoted durable-memory entries;
- workflow-critical items copied forward;
- retention state.

External references do not block archival when their paths are missing.

## External References

External artifact paths are evidence references, not active state.

This includes:

- temporary protection backups from historical non-Git operations;
- fetched research captures;
- preview files;
- mirror and package paths;
- installed-copy snapshots;
- referenced URLs or system files.

The archive records what was referenced, whether it was known to exist, and any relevant hash.

A missing referenced path does not by itself keep an item in hot state.

A missing path must not be described as deleted or verified unless the archive contains executed evidence of that status.

This rule governs archival eligibility.

It does not waive the pre-edit protection gate for an active operation: before an active write, the required backup or explicit waiver still must be present under [pre-edit-safety.md](pre-edit-safety.md).

## Existing-State Migration

Migration is review-assisted.

1. Inventory current `.agent` content with `scripts/state_archive.py inventory`.
2. Apply the Archive Eligibility test to every record.
3. Classify records as `active-workflow-critical` or `archive-eligible`.
4. Treat unresolved session-local questions, obsolete external paths, duplicate-copy maintenance, and superseded Git states as archive-eligible.
5. Keep active interrupt-recovery, safety, permission, and recovery obligations in hot state.
6. Write `.agent/migration/<session-id>/migration-review.md`.
7. Stage replacement hot files without historical round narratives.
8. Obtain explicit user approval for the migration manifest.
9. Archive the source snapshot, install the staged hot files, and verify the surviving records.

When a Git-status record is already resolved or superseded by later history, classify it as archive-eligible and retain the source snapshot.

Do not archive a Git-status record whose referenced working-tree state is still current and uncommitted.

## Retention Review

The default retention decision is **retain**.

Soft threshold: **2,000 archived lines or 256 KiB, whichever is reached first**.

The threshold applies to `.agent/archive/`, not to hot state and not to external references.

Before the threshold, emit no spontaneous retention hint.

When an archival operation finds the threshold reached, emit one review-only hint:

> Archive retention review is due: `<lines>` lines and `<size>` (soft threshold: 2,000 lines or 256 KiB). No archived session will be deleted automatically. Reply `review retention` to inspect candidates, `retain archives` to acknowledge and postpone, or `hold` to make no change.

After `retain archives`, record the reviewed byte and line watermarks in `.agent/archive/retention.md`.

Suppress another automatic retention hint until the archive grows by at least 25% or the user explicitly requests retention review.

Deletion is a separate destructive action.

Apply [pre-edit-safety.md](pre-edit-safety.md), name each exact archive path, show its manifest and contents, and obtain explicit user approval for that exact deletion set.

## Utility

Run from the skill repository:

```bash
python3 scripts/state_archive.py status
python3 scripts/state_archive.py status --json
python3 scripts/state_archive.py inventory
python3 scripts/state_archive.py check-todo
python3 scripts/state_archive.py prepare-session \
  --session-id yxgz-example \
  --source .agent/state \
  --archive-root .agent/archive
```

`status`, `inventory`, `check-todo`, and `prepare-session` without `--apply` are read-only.

Any invocation that enumerates, scans, indexes, or reads `.agent/archive/` performs an archive lookup and requires the explicit user permission defined above.

Applying an archive copy requires both `--apply` and `--confirm-session <session-id>`.

The utility never deletes source files or archives.

There is no shipped test harness.

Verification uses the three read-only commands above, followed by a reviewed dry run of `prepare-session`.

## Integration Boundaries

- [context-drift-governance.md](context-drift-governance.md) owns CTAGV state fields and the hot-state format.
- [pre-edit-safety.md](pre-edit-safety.md) owns active-operation protection, collection, cleanup, deletion, and rollback authority.
- [clarification-protocol.md](clarification-protocol.md) owns user decision and confirmation semantics.
- [approval-briefing.md](approval-briefing.md) owns destructive archive-deletion requests.

The threshold design follows PostgreSQL's soft size limit, systemd journald's distinction between active and archived files, and logrotate's size-based rotation policy ([PostgreSQL](https://www.postgresql.org/docs/current/runtime-config-wal.html), [journald](https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html), [logrotate](https://man7.org/linux/man-pages/man8/logrotate.8.html), retrieved 2026-10-20).
