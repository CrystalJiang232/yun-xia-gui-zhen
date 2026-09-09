# Interrupt Recovery Protocol

## When to Activate

Activate on any interrupt, resumed session, repeated message, or steering message such as `halt`, `stop`, or `wait`.

## Status Re-Establishment

Do not assume the reason for the interrupt. Before reasoning about active status, re-read session history/context and inspect workspace status. Treat every workspace and session state as unknown until verified.

1. Re-read session history/context.
2. Inspect `git status`.
3. Verify files with simple commands such as `ls`, `find`, or `rg`.
4. Use hash checks only as an optional aid, never as the sole basis for acting.

## Identical or Subset Message

If the later message is identical to, or overlaps enough with, the prior message, treat the later message as the source of truth. Do not reinject the former message as a competing instruction. Do not treat the event as an anomaly or failure.

When the overlap is uncertain, prefer Clarification Protocol over assuming intent.

No redundant work is needed beyond the briefest workspace verification.

## Steering Reset Protocol

On `halt`, `stop`, `wait`, or equivalent steering language:

1. Stop continuing work immediately.
2. Kill only recorded PIDs. If no PID is recorded or no match is found, report what was actually done: the spawned execution command and any known state. Leave the kill decision to the user. Do not use `pgrep` to locate processes.
3. Close opened tools and subagents.
4. Remove only intermediates definitely known to be agent-generated and safe to delete, such as session status files and program-run files including swap files. `.agent/state/`, the protection registry, and registered backups are never intermediates and never deleted in a steering reset. When unsure, do not delete.
5. Create a fresh status/session file and re-analyze the user prompt. Later instructions override earlier ones.
6. Use informative reset language, for example: "I'll close previous spawned subagent and re-analyze your requirements."
7. Do not offer apologies or regrets.
8. Report what was done and which phase was abandoned. Offer practical options: rollback when applicable, steer to the correct direction, or manual cleanup information.

## Rejection Feedback

When the user provides a rejection reason, treat that reason as the highest-priority instruction. System-generated rejections are exempt.

If following the reason requires too large a deviation, halt and report current status. Request explicit permission to steer.

Too large a deviation includes:

- Using a different library or command when the user designated one and has not permitted alternatives.
- Escalating tool use, such as writing outside the workspace instead of using the normal write tool.
- Invoking `curl` or `web_search` when the prior context implies local-only reads.

Offer alternatives through the Clarification Protocol.
