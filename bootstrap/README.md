# Bootstrap — Active Configuration Self-Scan (opt-in)

> Status: inspection draft (2026-08-18). Companion active-check manifest: `checks.md` — approved content is staged in the vault (`06-checks.md`) and is placed here upon inspection approval. This is an inspection-only application of the bootstrap entry contract; the SKILL.md gate section and `checks.md` are not yet applied.

## What this is

An **active self-scan** mode, complementary to the passive skill protocols. The main skill is a passive constraint set triggered on work; this directory performs an on-demand, read-only scan of the agent's host/framework configuration and reports what is not properly set up, with recommended values and the approach to fix them.

## Activation (opt-in, inactive by default)

- Inactive by default. Files here are not loaded at skill load; the passive trigger surface is unchanged.
- The user activates the scan by saying **"check the current configuration status"** or an equivalent description (e.g., "bootstrap scan", "system self-check", "setup check", "run the configuration scan").
- On activation, the agent reads this README and `checks.md`, then executes the scan.

## How the scan works

1. Read `checks.md` — the normative checklist (16 items across workspace/authority, filesystem/permissions, runtime/tools, framework config, and channel/subagent capability).
2. Inspect each item read-only; record **PASS / WARN / FAIL / SKIP** with evidence.
3. Fill a copy of `checks.md` in the host-specific temporary directory (never system config); report significant caveats in-session.
4. Output remediation per item: what is missing, the recommended value, and how to change it. Never modify system configuration automatically.

## Invariants

- Read-only: no writes outside the approved temporary result path.
- Secrets: presence-only, never values.
- The skill does not check itself: no skill, repo-state, AGENTS.md, or intermediate/local-file checks (configuration/auth files are the exemption).
- Network checks: skipped by design.

## Gating (planned)

SKILL.md will carry a gated "Bootstrap Mode (opt-in)" section (frontmatter untouched); this directory is the reference payload for that gate. No post-edit maneuvers (packaging/reinstall) are performed without explicit user direction.
