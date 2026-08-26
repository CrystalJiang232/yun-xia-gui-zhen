# Bootstrap Checks — combined checklist

Status: ACTIVE (2026-08-18). Approved checklist; companion to `README.md` in this directory.

## Purpose and usage

- Pure-Markdown guidance/anchor for the agent's active self-scan, invoked by the user saying "check the current configuration status" (or equivalent descriptions). No scripts.
- Read-only: the agent inspects and records; it never modifies system config.
- Result recording: the agent fills a copy of this file (in the host-specific temp directory) with PASS/WARN/FAIL/SKIP + evidence per item; significant caveats are reported in-session.
- Secrets: presence-only, never values.
- The skill does not check itself: no skill/repo-state/AGENTS.md checks, no intermediate/local file checks (config/auth files are the exemption).

## Legend

| Status | Meaning |
|---|---|
| PASS | Meets expected value |
| WARN | Deviation with workaround, or capability unavailable |
| FAIL | Missing/blocking |
| SKIP | Conditional/optional item not applicable (record reason) |

## Portability rules

- No absolute host paths in checks; use placeholders (`<workspace-root>`, `<config-path>`, `<temp-dir>`).
- Commands are examples only; the agent uses whatever the host provides (git / Get-FileHash / etc.).
- Network checks: skipped by design (none below probe the network).

---

## Area 01 — Workspace / authority

### CHK-01-02 — VCS identity (CONDITIONAL)

- Applicability: only when the target workspace is a Git repository (identity is required for commits); otherwise SKIP.
- Inspect: VCS identity config, e.g. `git config --get user.name`, `git config --get user.email`.
- Expected: configured. Recommended: configured with the correct owner.
- Severity: P1.
- Record: PASS / WARN / SKIP + evidence.
- Remediation: `git config --global user.name "<name>"`; `git config --global user.email "<email>"`.

### CHK-01-03 — Repo trust / edit authority

- Applicability: always when the workspace is an edit target.
- Inspect: host/project trust config (e.g., `projects.<path>.trust_level`) and the approved-source record.
- Expected: trusted or explicitly approved. Recommended: trusted + explicit approval recorded.
- Severity: P0 (hard safety).
- Record: PASS / WARN / FAIL + evidence.
- Remediation: add trust entry / obtain explicit user approval; record in protection-status.

---

## Area 03 — Filesystem / permissions

### CHK-03-01 — Writable roots sane

- Inspect: sandbox/permission profile; writable-roots list.
- Expected: no broad `$HOME` or `/` write scope. Recommended: workspace + temp only.
- Severity: P0 (hard safety).
- Record: PASS / WARN / FAIL + evidence.
- Remediation: narrow writable roots in the host configuration.

### CHK-03-02 — Session temp writable

- Inspect: host-specific temp path (`/tmp`, `%TEMP%`, `$TMPDIR`) writable.
- Expected: writable. Recommended: verified with a probe create/remove.
- Severity: P0 (hard safety).
- Record: PASS / WARN / FAIL + evidence.
- Remediation: fix temp permissions or choose an alternate approved temp location.

### CHK-03-04 — Config/auth files readable

- Inspect: configuration and credential file locations (host-specific), presence/readability only.
- Expected: readable or approved escalation. Recommended: readable; unreadable -> WARN with reason.
- Severity: P1.
- Record: PASS / WARN / FAIL + evidence.
- Remediation: adjust permissions or request approval/escalation.

---

## Area 04 — Runtime / tools

### CHK-04-01 — Core tools present

- Inspect: presence of shell, VCS, hash tool, text search (examples: `bash`/`sh`, `git`, `sha256sum`/`Get-FileHash`, `rg`) — presence only, no version pinning.
- Expected: present or a documented alternative. Recommended: present.
- Severity: P0 (tool check required).
- Record: PASS / WARN / FAIL + evidence.
- Remediation: use an available alternative and record it; install if user approves.

---

## Area 05 — Framework config (configuration/auth exemption)

### CHK-05-01 — Config discoverable and readable

- Inspect: agent config file location (host-specific, e.g., `<config-path>`), presence and readability.
- Expected: discoverable. Recommended: readable.
- Severity: P0.
- Record: PASS / WARN / FAIL + evidence.
- Remediation: locate the config per host docs; adjust permissions.

### CHK-05-02 — Approval policy present

- Inspect: approval/permission policy setting (e.g., `approval_policy`).
- Expected: present. Recommended: `on-request` or stricter.
- Severity: P0.
- Remediation: set approval policy per host docs.

### CHK-05-03 — Sandbox mode not permissive

- Inspect: sandbox mode setting and effective behavior.
- Expected: `workspace-write` or stricter. Recommended: workspace-write + project trust recorded.
- Severity: P0 (sandbox check required).
- Remediation: tighten sandbox mode per host docs.

### CHK-05-04 — Network config consistency (config-only)

- Inspect: compare configured network access to actual sandbox behavior; no network probing.
- Expected: consistent. Recommended: consistent + documented.
- Severity: P1.
- Record: PASS / WARN / FAIL + evidence.

### CHK-05-05 — Concurrency/limit keys present

- Inspect: depth/threads/iteration-cap settings in config.
- Expected: present. Recommended: values cross-verified from official docs (pending verification at implementation).
- Severity: P1.

### CHK-05-06 — Multi-agent capability recorded

- Inspect: multi-agent feature flag and inter-agent messaging capability (FULL/PARTIAL/NONE).
- Expected: recorded. Recommended: explicit capability statement.
- Severity: P1.

### CHK-05-07 — Secrets hygiene

- Inspect: credential presence only; ensure no value is ever echoed.
- Expected: credentials never echoed. Recommended: redaction rule enforced in all output.
- Severity: P0 (auth exemption).
- Record: PASS / WARN / FAIL + evidence (presence boolean only).

### CHK-05-08 — Standing approval rules scoped

- Applicability: always when the host exposes standing-approval primitives (prefix rules / allowlists / execpolicy); otherwise SKIP with reason.
- Inspect: standing-approval configuration (host-specific, e.g., `<config-path>` rules) and the scope of each rule.
- Expected: routine command classes covered by narrow, categorical rules; no dangerously broad rules (e.g., no bare interpreter or shell wildcard).
- Recommended: narrow allowlist paired with sandbox boundaries; rules proposed by the agent, granted only by the user/host.
- Severity: P1.
- Record: PASS / WARN / SKIP + evidence.
- Remediation: propose scoped rule additions per host docs; never self-grant.

### CHK-05-09 — No-op suppression understood

- Applicability: always.
- Inspect: host approval behavior for read-only/no-op commands (auto-approved or suppressed?).
- Expected: recorded; the skill never fabricates no-op approval requests.
- Recommended: record host behavior in constraints; route approvals only through genuinely gated actions.
- Severity: P1.
- Record: PASS / WARN + evidence.
- Remediation: update in-skill instructions to remove any test/no-op request conventions.

---

## Area 07 — Channel / subagent capability

### CHK-07-01 — Channel presence recorded

- Inspect: availability of an interactive clarification/approval channel (ask_user or equivalent).
- Expected: recorded as available / absent / unknown.
- Severity: P1.

### CHK-07-02 — Inter-agent messaging capability recorded

- Inspect: messaging capability of the host.
- Expected: recorded as FULL / PARTIAL / NONE.
- Severity: P1.

### CHK-07-03 — Subagent mode detection (GENERIC)

- Applicability: always.
- Inspect: subagent spawning availability for mode routing (Mode A vs Mode B).
- Output: a generic capability statement (subagents available / partial / unavailable). Informational item.
- Label: PASS when subagents are available; WARN only when subagent spawning is unavailable; never FAIL.
- Severity: P1.
- Record: PASS / WARN + evidence.
- Remediation on WARN: continue in Mode A (single-agent) and note the routing consequence.

### CHK-07-04 — Free-text approval channel capability

- Applicability: always.
- Inspect: whether the host's approval/clarification channel accepts free text (ask_user-alike), is binary-only, or is absent.
- Expected: recorded as free-text / binary-only / absent.
- Recommended: recorded; free-text enables direct type-to-confirm, binary-only requires the two-phase chat protocol.
- Severity: P1.
- Record: PASS / WARN + evidence.

---

## Excluded by design (traceability)

Dropped categories per the approved rule-of-thumb: skill self-checks (area 02), repo-state check (CHK-01-01), AGENTS.md check (CHK-01-04), intermediate/local file checks (area 06: backup registry, protection-status file, cleanup eligibility; CHK-03-03), network checks (CHK-04-02/04-03), and skill-internal bookkeeping (mode-selection consistency). Philosophy: the skill shall not check itself (loopback).
