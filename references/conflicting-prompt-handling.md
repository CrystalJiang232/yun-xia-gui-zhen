# Conflicting Prompt Handling

Single-file owner of conflict-resolution semantics for conflicting instructions across user, system, project, and session inputs. It operationalizes the **Conflicting Prompt Handling** bullet in [../SKILL.md](../SKILL.md) and composes with [clarification-protocol.md](clarification-protocol.md), [pre-edit-safety.md](pre-edit-safety.md), and [context-drift-governance.md](context-drift-governance.md).

## Resolution Order

When instructions conflict, resolve in this fixed order; never skip a level:

1. **Authority** — strict constraints outrank lower-scope instructions; among non-strict system-injected scopes, session-level outranks project(workspace)-level, which outranks system/global-level.
2. **Polarity** — within the same scope, bans and DON'Ts override DOs.
3. **Scope** — a ban binds only its declared scope; actions outside that scope are not prohibited.
4. **Recency** — for user instructions at the same authority level, the later round wins; recency never applies within one single input.
5. **Clarification** — a single-input conflict that authority, polarity, and scope cannot decide always enters Clarification Protocol; never resolve silently or by strictness alone.

## Authority Ladder

Rank sources of instruction from highest to lowest binding power:

| Rank | Source class | Examples |
|------|--------------|----------|
| 1 | Strict constraints | Host-enforced sandbox and permissions, org-policy-pinned settings, platform/system-prompt directives, safety-critical rules |
| 2 | Session-level injected guidance | Session memory, `CLAUDE.local.md`, cwd-scoped `AGENTS.override.md`, per-session settings |
| 3 | Project(workspace)-level | Repository `AGENTS.md` / `CLAUDE.md` and workspace rules |
| 4 | System/global-level injected guidance | User-global files such as `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md` |
| 5 | Skill defaults and general guidance | This skill's own defaults when no higher-priority instruction applies |

Host discovery chains reinforce this ladder: Codex reads `AGENTS.override.md` before `AGENTS.md` and merges files from the repository root down to the current directory, so closer-to-cwd guidance overrides earlier guidance because it appears later in the combined prompt. Claude Code loads managed memory lowest, then user memory, then project memory, then local memory, with files closer to the working directory taking priority.

## Strict vs Non-Strict System Directives

**Strict** means host-enforced or safety-critical: sandbox and permission confinements, org-policy-pinned settings, platform/system-prompt directives, and safety-critical rules. Strict constraints bind regardless of user or file instructions and cannot be waived by prompt-level override.

**Non-strict** means prompt/instruction-level only: style, conventions, workflow guidance, and other directives that the host does not enforce. An explicit user instruction overrides a non-strict system directive in the same message or round.

This rule is agent-governance semantics, not a claim about model instruction hierarchy. The strictness classification is the security boundary: never treat a safety-critical directive as non-strict on inference alone; when in doubt, classify strict and clarify.

## Polarity (Bans over DOs)

Within the same scope, negative-side instructions override positive-side ones: "no write" beats "proceed with work". A ban binds only its declared scope: "keep task read-only" (workspace) does not block clarification work whose files live under the temporary directory. Only absolute prohibitions ("never", "must not") qualify as bans; soft negatives ("prefer not to") do not qualify.

This rule is normative governance, not a compliance-optimality claim. It is a defined polarity precedence, not the generic "stricter wins" shortcut that [../SKILL.md](../SKILL.md) forbids.

## Recency (Inter-Round Only)

Recency applies only across rounds: for user instructions at the same authority level, the later round wins. Example: a later "edit approved" overrides an earlier "keep this session read-only".

Never apply recency within one single input, such as one long prompt, one instruction file, or one system prompt. Intra-input conflicts resolve by authority, polarity, and scope, then by clarification.

## Single-Input Conflicts

Conflicting instructions can occur within a single instruction file, a single user message, or a single system prompt, for example:

- Different approval or write-access instructions
- Conflicting reference constraints
- Contradictory implementation details (for example, "use struct" versus "use enumerating parameters")

Resolve by authority, then polarity, then scope. If the conflict remains undecided, always enter Clarification Protocol; never pick a winner silently or by strictness alone. Channel responses that are empty, system-default, or timeout defer the round per Clarification Channel Governance §A of [clarification-protocol.md](clarification-protocol.md).

## Worked Examples

1. **"No write" vs "proceed with work"**: polarity decides — the ban wins within the workspace scope; the agent may still produce analysis and persist governance state under the session temporary directory.
2. **"Keep task read-only" vs "proceed with clarification protocol"**: scope decides — the ban covers the workspace only; clarification work that writes only under the temporary directory is compatible and proceeds.
3. **Earlier "keep read-only", later "edit approved"**: recency decides across rounds — the later same-authority user instruction wins for the workspace.
4. **Two same-priority user directives in one message** ("edit X" and "do not edit X"): authority, polarity, and scope cannot decide; enter Clarification Protocol.
5. **User message vs non-strict system directive in one round**: authority with strictness classification decides — the user instruction overrides the non-strict directive; a strict directive remains binding.

## Caveats (reference-verified)

- Instruction-polarity practice reports that positive directives outperform negative ones in compliance, so reserve bans for absolute prohibitions and prefer positive phrasing elsewhere.
- Models resolve conflicting instructions inconsistently (benchmarks report strong declines on conflict sets), so a documented precedence is behavioral guidance, not a guarantee; keep conflicts visible and use clarification as the fallback.
- Allowing user instructions to override non-strict system directives must not become a prompt-injection vector: strictness classification is the boundary, and safety-critical directives default to strict.
- Instruction volume and layer depth degrade compliance; keep precedence rules concise and avoid duplicating the same rule across layers.
