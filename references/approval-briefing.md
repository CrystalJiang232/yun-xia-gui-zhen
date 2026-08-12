# Approval Briefing and Fatigue Detection

Single-file owner of approval-request briefing and human-attention fatigue detection. It operationalizes the **Approval Briefing and Fatigue Checks** bullet in [../SKILL.md](../SKILL.md) and composes with [pre-edit-safety.md](pre-edit-safety.md), [clarification-protocol.md](clarification-protocol.md), and [context-drift-governance.md](context-drift-governance.md).

## Table of Contents

- Purpose
- M1 — Approval Briefing Rules
- Few-Shot Anchoring
- M2 — Fatigue Detection
- Emission Discipline
- Caveats

## Purpose

Human approval reliability degrades under confirmation fatigue: users approve roughly 97% of permission requests, and in one study only 13.6% of testers refused a clearly dangerous command swapped into a permission prompt. Two mechanisms counter this degradation: M1 explicit and readable approval briefings, and M2 periodic labeled attention checks.

## M1 — Approval Briefing Rules

Every user-facing approval request MUST contain all of the following:

1. **Label** — `[APPROVAL REQUEST — EXECUTABLE]` for real normal requests, `[ILLUSTRATIVE — DO NOT ACT]` for examples, `[ATTENTION CHECK — TEST MESSAGE]` for fatigue checks.
2. **Intended action** — one sentence stating what the agent is about to do.
3. **Named targets** — every target path, URL, or argument with a variable name and its role; no magic strings.
4. **Risk tier** — none / low / medium / high / destructive, plus a one-line consequence statement.
5. **Exact command** — multi-line with one logical step per line; never an opaque one-liner; line breaks at `&&` and `|`; every argument visible.
6. **Options** — Approve / Deny; never pre-select Approve; risky actions require a deliberate non-default answer.

Variable naming convention: declare `TARGET_DIR`, `TARGET_FILE`, or `CONFIG_*` variables at the top of the command; reference variables instead of literals; use lowercase for unexported variables; mask secrets (tokens, keys, passwords) in previews.

Template — normal branch:

```
[APPROVAL REQUEST]
Intended action: <one sentence>
Targets: <variable> | <path> | <role>
Risk tier: <tier> — <consequence>

TARGET_DIR="<path>"
TARGET_FILE="${TARGET_DIR}/<name>"
<command> "${TARGET_FILE}"

Approve — Deny
```

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

Contrast notes: literal paths repeated across a line and across commands make typos and copy-paste drift invisible; opaque one-liners hide arguments and intermediate commands between operators; the good side's variables make each target's role visible and reviewable, matching the named-targets rule.

## M2 — Fatigue Detection (Attention Checks)

**Trigger**: after every 12-20 user-facing approval requests, emit one labeled attention check; the interval is random uniform within that range. Only user-facing approval requests count toward the interval.

**Atomicity (higher-priority rule)**: destructive operations are atomic; never insert an attention check inside an atomic operation group; checks wait for the group boundary.

**Check content**: explicit test-message label; a statement that this is a test; a command that is all no-op but long, composed of `cd`, `echo`, `printf`, `ls`, and `grep` against arbitrary paths that may fail; the agent never executes the command; the expected answer is Deny.

**Response semantics**:

- Deny → monitoring confirmed; proceed with the interrupted work.
- First failure (any other answer) → self-spin once: re-present the check with explicit in-prompt guidance that it is a test message and the user should click Deny.
- Second failure → halt as if a timeout occurred; record resume state (task, pending approvals, artifacts and hashes, decision log, UNEXECUTED next-round proposal) and report.
- Timeout / empty / system-default → immediately record status and halt, per Clarification Channel Governance §A of [clarification-protocol.md](clarification-protocol.md).

Every check and its outcome is written to the session audit log with a timestamp.

Template — fatigue branch:

```
[ATTENTION CHECK — TEST MESSAGE]
This is a test to verify the user is monitoring the session, not a real command request.
If present, answer Deny; the command below will NOT be executed.
Intended action: none
Risk tier: none

TEST_PATH_A="<arbitrary path>"
cd "${TEST_PATH_A}"
echo "checkpoint alpha"
printf '%s\n' "heartbeat"
ls "<arbitrary path>"
grep -R "marker" "${TEST_PATH_A}"
echo "checkpoint omega"

Allow — Deny (expected: Deny)
```

## Emission Discipline

Approval boxes appear only for genuinely approval-gated actions. Routine, already-authorized operations (for example, session state writes under the temporary directory) get an informational note, not an approval dialog. Real requests are marked `[APPROVAL REQUEST — EXECUTABLE]`; illustrative instances are marked `[ILLUSTRATIVE — DO NOT ACT]`. Over-asking accelerates habituation and erodes the approval signal.

## Caveats (reference-verified)

- Warning fatigue is real: users ignore up to roughly 70% of security alerts, so checks must be rare and honest; over-asking accelerates habituation and erodes the approval signal.
- Automation-complacency research supports artificial friction, but deceptive checks erode trust; always label the check as a test.
- Better briefing does not fix absent attention; layer host-level controls (classifier, allowlist, sandbox) underneath human review.
- Checks never break atomic destructive groups; interval counting resumes at the group boundary.
