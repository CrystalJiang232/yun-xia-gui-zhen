# Approval Briefing and Governance

Single-file owner of approval-request briefing and approval-fatigue governance. It operationalizes the **Approval Briefing and Governance** bullet in [../SKILL.md](../SKILL.md) and composes with [pre-edit-safety.md](pre-edit-safety.md), [clarification-protocol.md](clarification-protocol.md), [context-drift-governance.md](context-drift-governance.md), and [retry-governance.md](retry-governance.md).

## Table of Contents

- Purpose
- M1 — Approval Briefing Rules
- M1.1 — Prerequisite/Mutation Separation (two-sided)
- Few-Shot Anchoring
- M2 — Approval Volume & Attention Governance
- Emission Discipline
- Caveats

## Purpose

Human approval reliability degrades under confirmation fatigue: users approve roughly 97% of permission requests, and in a controlled study only 13.6% of testers refused a clearly dangerous command swapped into a permission prompt; interception falls further as prompt volume grows. Two mechanism groups counter this degradation: **M1** explicit, readable approval briefings, and **M2** approval-volume governance — fewer, risk-tiered, host-native approval requests with deliberate high-risk confirmation, milestone review, and optional user-activated tracking.

This file deliberately does NOT inject test or no-op approval requests. Hosts decide which actions surface approval: read-only/no-op commands are suppressed or auto-approved by the framework, so a fabricated no-op request either never appears or violates the approval pipeline. Injecting tests also erodes the channel's honest signal. Both mechanisms below operate on real approval requests only.

## M1 — Approval Briefing Rules

Every user-facing approval request MUST contain all of the following:

1. **Label** — `[APPROVAL REQUEST — EXECUTABLE]` for real normal requests, `[APPROVAL REQUEST — HIGH-RISK — TYPE TO CONFIRM]` for the high-risk tier, `[ILLUSTRATIVE — DO NOT ACT]` for examples.
2. **Intended action** — one sentence stating what the agent is about to do.
3. **Named targets** — every target path, URL, or argument with a variable name and its role; no magic strings.
4. **Risk tier** — none / low / medium / high / destructive, plus a one-line consequence statement.
5. **Exact command** — multi-line with one logical step per line; never an opaque one-liner; line breaks at `&&` and `|`; every argument visible. Line breaks are formatting only: a read-only prerequisite is never conjoined with the mutating command in the first place (M1.1).
6. **Options** — Approve / Deny for normal requests; for high-risk requests, the required confirmation phrase (see M2.2); never pre-select Approve; risky actions require a deliberate non-default answer.

Variable naming convention: declare `TARGET_DIR`, `TARGET_FILE`, or `CONFIG_*` variables at the top of the command; reference variables instead of literals; use lowercase for unexported variables; mask secrets (tokens, keys, passwords) in previews.

Template — normal branch:

```
[APPROVAL REQUEST — EXECUTABLE]
Intended action: <one sentence>
Targets: <variable> | <path> | <role>
Risk tier: <tier> — <consequence>

TARGET_DIR="<path>"
TARGET_FILE="${TARGET_DIR}/<name>"
<command> "${TARGET_FILE}"

Approve — Deny
```

Template — high-risk branch (type-to-confirm):

```
[APPROVAL REQUEST — HIGH-RISK — TYPE TO CONFIRM]
Intended action: <one sentence>
Targets: <variable> | <path> | <role>
Risk tier: high / destructive — <consequence>

TARGET_DIR="<path>"
TARGET_FILE="${TARGET_DIR}/<name>"
<command> "${TARGET_FILE}"

Reply exactly (no arguments, no other words): approved to <base_command>
Any other reply, empty, or timeout = Deny. The command will NOT be executed otherwise.
```

### M1.1 — Prerequisite/Mutation Separation (two-sided, equal precedence)

Two clauses of **equal precedence** — apply both; neither is a caveat to the other. They decide where an approval boundary is, and where it is not.

**M1.1a — Split when needed.** A read-only or reversible prerequisite — a backup copy, `sha256sum`/hashing, `ls`/`cat`/`echo` inspection, `git status`, or any other non-mutating step — MUST NOT be joined to a mutating command by a shell control operator (`&&`, `||`, `;`, `|`) or a subshell/command-substitution boundary.

- Run the prerequisite as its own step, as its own command, before the mutation.
- If the host gates that step, brief it on its own with risk tier none/low; if the host suppresses it (the usual case), it produces no dialog and the mutation stands alone as the single approval.
- Line-breaking at `&&` (rule 5) formats an operator chain; it does not create an approval boundary and does not satisfy this clause.
- The escalation trigger must be attributable to one visible command: the reviewer approves the safe step alone and the mutation alone, never a bundle.

**M1.1b — Never over-split.** Separation applies only to read-only prerequisites; it never inflates the approval count.

- Never raise an approval request for a read-only or no-op step (Emission Discipline): the host suppresses those, and a fabricated request erodes the approval signal.
- Two or more mutating steps that must land together are an atomic mutation group (M2.3): they stay in ONE approval request and are never split.
- Prefer the fewest real approval requests that keep each mutation individually attributable; every extra prompt spends review attention on a routine action (M2).

## Few-Shot Anchoring — Good vs Bad Commands

Use these contrast pairs to anchor briefing generation: the good side declares named variables at the top, uses one logical step per line, and references variables instead of literals; the bad side packs inline literal paths into opaque one-liners. These pairs are illustrative reference material, not executable requests.

Pair 1 — cleaning a build directory:

BAD (magic strings, one-liner, hard to review):

```bash
rm -rf /home/hibiscus/git_repos/SkillLib/tmp/build && rm -rf /tmp/qrh-session-cache
```

GOOD (named targets, one step per line):

```bash
PROJECT_ROOT="/home/hibiscus/git_repos/SkillLib"
BUILD_DIR="${PROJECT_ROOT}/tmp/build"
CACHE_DIR="/tmp/qrh-session-cache"
rm -rf "${BUILD_DIR}"
rm -rf "${CACHE_DIR}"
```

Pair 2 — copying a log file into workspace temp:

BAD (repeated literal paths, chained one-liner):

```bash
cp /tmp/qrh-session-approval-fatigue/log.txt /home/hibiscus/git_repos/SkillLib/tmp/ && echo "copied"
```

GOOD (named targets, one step per line):

```bash
STATE_DIR="/tmp/qrh-session-approval-fatigue"
LOG_FILE="${STATE_DIR}/log.txt"
WORKSPACE_TMP="/home/hibiscus/git_repos/SkillLib/tmp"
cp "${LOG_FILE}" "${WORKSPACE_TMP}/"
echo "copied"
```

Pair 3 — running a test suite in a target project:

BAD (literal path repeated, chained one-liner):

```bash
cd /var/lib/jenkins/workspace/project-a && pytest /var/lib/jenkins/workspace/project-a/tests -k integration
```

GOOD (named targets, one step per line):

```bash
PROJECT_DIR="/var/lib/jenkins/workspace/project-a"
cd "${PROJECT_DIR}"
pytest "${PROJECT_DIR}/tests" -k integration
```

Pair 4 — backup, then mutate (split the read-only prerequisite from the mutation, per M1.1):

BAD (safe prerequisite welded to the mutation by `&&`):

```bash
cp "${SKILL_FILE}" "${BK_DIR}/" && unzip -oq "${SKILL_FILE}" -d "${SKILL_DIR}"
```

GOOD (the prerequisite is its own command; the mutation is the single approval):

```bash
# step 1 — prerequisite (read-only, its own command; usually host-suppressed)
cp "${SKILL_FILE}" "${BK_DIR}/"

# step 2 — the single approval-gated mutation
unzip -oq "${SKILL_FILE}" -d "${SKILL_DIR}"
```

Contrast notes: literal paths repeated across a line and across commands make typos and copy-paste drift invisible; opaque one-liners hide arguments and intermediate commands between operators; the good side's variables make each target's role visible and reviewable, matching the named-targets rule. Pair 4 adds the M1.1 split: a read-only prerequisite never rides along inside the mutation's approval command.

## M2 — Approval Volume & Attention Governance

### M2.1 Host-Native Standing Approvals

- The host owns approval gating; the agent adapts, never simulates. Prefer the host's standing-approval primitives — prefix rules, allowlists, execpolicy rules, session approvals, sandbox presets — to reduce prompt volume structurally.
- When requesting escalation for a repeatable command class, propose a categorical, reasonably scoped standing rule so future identical requests skip approval. Follow host guidance on scope: categorical but narrow, never dangerously broad (e.g., never a bare interpreter or shell).
- The agent proposes; only the user or host policy grants. Never self-grant standing approval, and never silently extend an approved rule to a broader scope.
- Already-authorized operations get an informational note, not an approval dialog (see Emission Discipline).
- Record granted standing approvals in session state (constraints / protection-status) so later requests recognize them and do not re-ask.

### M2.2 Risk-Tiered Friction with Type-to-Confirm

**Tier assignment**:
- Low / reversible: informational note or auto-approval; no dialog.
- Medium: standard M1 briefing with Approve / Deny.
- High / destructive / irreversible: standard M1 briefing plus type-to-confirm.

**Type-to-confirm semantics (high-risk tier only)**:
- The user must reply with exactly `approved to <base_command>`, where `<base_command>` is the first token of the proposed command (e.g., `rm` for `rm -rf "${BUILD_DIR}"`).
- Strict matcher: trim whitespace; require the exact phrase; no arguments, no quoted variants, no synonyms (`yes`, `ok`, `go`, `approved` alone are Deny). Command token matching is case-sensitive.
- Any mismatch, empty, or timeout response → Deny: do not execute, do not self-spin or re-present; record the verdict in the audit ledger; the user may re-issue deliberately.
- The phrase authorizes only the single proposed command instance shown in the briefing. It never becomes a standing approval (standing approvals come from M2.1 / host rules).

**Channel adaptation**:
- If the host exposes a free-text approval channel (ask_user-alike), require the phrase in that response.
- If the host approval channel is binary (Approve / Deny only), run a two-phase protocol: (1) full briefing stating the required phrase; (2) wait for the user's chat reply; execute only on exact match.
- Record channel capability (`CHANNEL` + free-text availability) in the constraints file at skill load.

### M2.3 Milestone / Plan Review Checkpoints

- At natural boundaries — before a destructive group, at milestone ends, before handoff — present a batch summary: actions taken, pending approvals, next actions, and the rationale for each.
- The user confirms or amends the plan; silence is never approval (Clarification Channel Governance §A of [clarification-protocol.md](clarification-protocol.md) applies).
- Never break atomic destructive groups; checkpoints wait for the group boundary.

### M2.4 User-Activated Approval-State Tracking (default dormant)

- **Default: OFF.** The agent does not collect approval-state statistics or metrics unless the user requests it.
- **Activation:** the user asks semantically in-prompt, e.g., "keep track of approval status", "track approvals", "approval metrics", "monitor approval patterns", "approval audit". Record the trigger wording, timestamp, and scope in the constraints file (`APPROVAL_TRACKING: off|on` + trigger evidence). Session-scoped by default; "always" extends to future sessions only with explicit user direction.
- **While ON:**
  - Maintain an approval ledger in the session temp directory: timestamp, tier, verdict, command base, approval latency, phrase match (high-risk), standing-rule reuse.
  - Run deferred exception-based analysis at milestones or session end: rubber-stamp signals (median approval latency, approve-all streaks, first-try denial rate, type-to-confirm mismatch rate). Report only when thresholds trip or the user asks; never in-band.
  - Optional canary/honeytoken layer only on explicit user request and with host approval: decoy files/credentials alarm on access; they are never presented as approval prompts and never referenced in briefings.
- **Disclosure:** passive but disclosed. On activation, give the user one line ("approvals are being tracked; you will only see exceptions"); otherwise fully silent. Hidden tracking requires an explicit user override, recorded per [conflicting-prompt-handling.md](conflicting-prompt-handling.md).

## Emission Discipline

Approval boxes appear only for genuinely approval-gated actions. No fabricated, no-op, or test approval requests are ever emitted. Routine, already-authorized operations get an informational note, not an approval dialog. Real requests are marked `[APPROVAL REQUEST — EXECUTABLE]` or `[APPROVAL REQUEST — HIGH-RISK — TYPE TO CONFIRM]`; illustrative instances are marked `[ILLUSTRATIVE — DO NOT ACT]`. Over-asking accelerates habituation and erodes the approval signal.

## Caveats

- Warning fatigue is real: users ignore a large share of security alerts, so keep approvals rare and honest; over-asking accelerates habituation and erodes the approval signal.
- Volume reduction is the primary anti-fatigue mechanism; risk-tiered friction concentrates attention where it matters. In Anthropic's controlled study, humans caught only 13.6% of dangerous commands in per-command prompts while rejecting 39% of full plans; per-prompt review degrades as prompt volume grows.
- Type-to-confirm is reserved for truly irreversible actions; overusing it on routine actions trains users to bypass it. No confirmation method fixes a flawed rationale; it only raises deliberate-action cost.
- Deceptive or hidden testing erodes trust. Approval-state tracking is disclosed on activation by default; canary layers are opt-in and never in-band.
- Hosts suppress approval for read-only/no-op commands; never fabricate no-op approval requests — they are semantically incoherent and either suppressed or violate the host pipeline.
- Checks never break atomic destructive groups; interval and boundary rules apply to real approval requests and checkpoints only.
