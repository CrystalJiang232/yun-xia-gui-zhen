# Writing for Agents (AI-Facing Docs Style)

## Purpose and Scope

Guidance for authoring the compact, always-on files agents read first: `AGENTS.md`, `CLAUDE.md`, `SKILL.md` entry points, and similarly scoped AI-reachable docs. The goal is high signal-to-noise: rules that survive attention competition and load only what a task needs.

## Core Principles

- **Concise by default**: keep the always-on file short; every line competes for attention on every task. Vendor guidance points the same direction (Claude Code's CLAUDE.md guidance recommends staying under roughly 200 lines; Agent Skills best-practice guidance recommends keeping a SKILL.md body near or under roughly 500 lines). Treat vendor numbers as attributed recommendations, not universal thresholds, and prefer the leanest file that stays accurate for the project.
- **Specific and verifiable**: write instructions an agent can check, not aspirations. Prefer behavior the agent can demonstrate (commands, binary conditions, exact scopes) over adjectives ("carefully", "thoroughly", "properly").
- **Description-first discovery**: a skill or doc is found and invoked through its description and triggers. State plainly what it is for and when to load it; keep the body for the behavior.
- **Calibrate triggers with an eval set**: maintain roughly 20 should-trigger / should-not-trigger queries and re-run them after every description edit; the set size is an attributed recommendation from the anthropics/skills skill-creator, not a universal threshold.
- **Progressive disclosure**: the entry file points; procedures live on demand. Put full protocols, runbooks, and details in separate files (references, skills bodies) that load only when their trigger matches. Import or link rather than duplicating content across files; keep one authoritative copy and soft pointers elsewhere.
- **Don't restate what a higher-priority layer already enforces**: system, safety, and permission constraints do not need mirroring in every agent-facing file; duplicating them creates drift when the higher layer changes.

## Match the Form to the Failure (Authoring Guidance)

When editing an agent-facing rule, classify the baseline failure first; the wording form that bulletproofs one failure type measurably backfires on another (taxonomy adapted from obra/superpowers `writing-skills`, attributed guidance for editing this skill — not a runtime rule).

| Baseline failure | Right form | Wrong form |
|---|---|---|
| Skips a known rule under pressure | Prohibition + rationalization table + red-flags self-check | Soft guidance ("prefer", "consider") |
| Complies, but the output has the wrong shape | Positive recipe or contract naming the required parts in order | Prohibition list ("don't restate", "never narrate") |
| Omits a required element | A REQUIRED field or slot in the template being filled | Prose reminders near the template |
| Behavior depends on a condition | A conditional keyed to an observable predicate | An unconditional rule plus exemption clauses |

Rules for any form: no nuance clauses ("don't X unless it matters" reopens the negotiation); express a real exception as its own conditional on an observable predicate; an exemption clause does not scope a prohibition — restructure so the rule cannot reach the exempt part.

## Worked Examples

**Before** (vague, unverifiable):

> Be careful when editing files and think before you act. Make sure requirements are understood.

**After** (specific, verifiable):

> Run the pre-edit gate before any project-file write: confirm the authorized source path, classify the repository state, and record the gate state in protection-status.md. If requirements are ambiguous, halt and present options with a recommended default; do not proceed on silence or a timeout.

This "after" wording follows the approved E1-E4 behavior wording (always-on operating behaviors, complexity auto-routing with approval guards, detect-before-ask, and written Definition-of-Done). The pattern generalizes: each rule names the trigger, the action, and the checkable outcome.

**Before** (burying the trigger):

> This skill contains protocols for many situations. Refer to the references when relevant.

**After** (description-first):

> Use when starting any non-trivial task, when requirements are ambiguous, or when external verification is needed. Load exactly one reference file required by the active protocol.

## Relationship to This Skill

This skill's own layout is the working example: `SKILL.md` stays the compact entry point (protocol matrix, mode rules, soft pointers), while detailed protocols live in `references/*.md` loaded on demand, and governance detail lives in the installed skill and `AGENTS.md` rather than being mirrored in every file. Edits to this file should follow the principles above: specific instructions, no duplicated content, no unmarked vendor numbers.

## Anti-Patterns

- **Kitchen-sink entry file**: growing the always-on file until it covers every possible procedure instead of pointing to on-demand references
- **Aspirational wording**: instructions an agent cannot verify or demonstrate
- **Duplicated rule sets**: the same rule restated in AGENTS.md, CLAUDE.md, and SKILL.md with slightly different wording, inviting drift (note: CLAUDE.md does not read AGENTS.md by default; bridge via an `@AGENTS.md` import or symlink rather than copying content)
- **Unattributed thresholds**: presenting vendor line-count guidance as a universal law
- **Self-violation**: authoring agent-facing docs that fail the style they prescribe
