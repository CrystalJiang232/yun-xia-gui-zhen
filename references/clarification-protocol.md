# Clarification Protocol

## Table of Contents

- Overview
- When to Activate
- Defaults and Overrides
- Clarification Loop
- Required Decision Substance
- Representation Selection
- Consultant If-Then Variant
- Clarification Channel Governance
- Decision Ownership (DO-1…DO-3)
- Mid-Work Barrier Detection
- State Management
- Subagent Inspector

## Overview

Defer all work until requirements are explicit and exact. This protocol governs the interactive clarification loop between agent and user.

**Clarification package (anchoring instruction, default-on).** Clarification is the default for ANY non-trivial task (multi-step, ambiguous, high-risk, or state-mutating), even when the task looks approachable at a glance. To prevent redundant interrupts, bundle all open decision points into ONE **clarification package** (a single block, minimal items) instead of asking one question at a time. Treat the state-persistence confirmation and any stale-state reconcile decision as items of that same package.

**Delivery routing (normative; choose the path BEFORE invoking the channel).** The package is logically one; it is delivered on exactly one of two paths:

1. **Channel path** — allowed only when the package fits the host's per-call capacity: at most **3 items**, and no item carrying more options than the host accepts (2–3 on Codex-class hosts; up to 4 elsewhere).
2. **Session-output path** — the DEFAULT whenever the package would exceed that capacity, i.e. **more than 3 items** or any item over the host's option limit. Present the whole package as plain text in the session output, record every item `awaiting`, and await the user's next message. Do not invoke the channel for a package that cannot fit, and do not split it to make it fit.

Both paths are one clarification round. Nothing closes merely because it travelled the session-output path, and no item may be silently dropped or deferred to make a package fit.

**Decision ownership (pointer).** Nothing in this protocol authorizes the agent to close a clarification item on its own recommendation. The commitment test, the deferral set, the reserved phrase table, the default-identity guard, bounded escalation, the item-state enum, and the non-trivial test are normative in **Decision Ownership (DO-1…DO-3)** below — read it before raising or resolving any item.

## When to Activate

Activate when ANY of these conditions are met:
- Task description contains words like "maybe", "probably", "whatever", "simple", "just", "similar to"
- Multiple valid implementation approaches exist
- Task requests implementation, refactoring, or an API/SPI change and any scope, approach, contract, behavior, or implementation decision remains ambiguous
- Task is non-code-type but non-trivial and its scope, approach, output, or downstream effect remains ambiguous
- Business logic involves filtering, thresholds, or conditional rules
- Output format, target environment, or constraints are unspecified
- Request is a bare imperative naming a deliverable but not its acceptance criteria (DO-3)
- User says "do what you think is best" without prior established patterns (as a *reply*, this is a Class W discretion grant only when a recommended default was presented for that item; as a *request*, it grants nothing — see §D)

**Carve-out — Missing-Field Protocol**: when the instruction's conveyance is damaged (stripped/truncated message, invalid structured payload, missing parameter, or a parameter far outside any valid range), the missing field is NOT a clarification point under this protocol. Do not offer options, representations, plan briefs, or a recommended default for it; apply the Missing-Field Protocol (missing-field-protocol.md): plain field request, wait loop, waiver branch.

## Defaults and Overrides

- **Default-on**: clarify by default on any non-trivial task; the listed triggers are illustrative, not exhaustive.
- **Low-effort override (task-based)**: a clearly trivial and fully reversible task with one obvious approach may skip or shrink the package; the agent states its brief assumption instead of interrupting.
- **Waiver override (prompt-based)**: an explicit user "don't clarify" or pre-authorized no-interrupt instruction permits proceeding; record the waiver's exact wording and scope. Never infer a waiver from silence, a timeout, or a default/system response (see Clarification Channel Governance §A). A recognized waiving phrasing, the rule that procedural permission resolves nothing (DO-2b), and the exact Class W/R scopes and their English-only limit are normative in §D. Missing-Field, pre-edit, and channel rules still bind when a waiver applies.

## Clarification Loop

### Phase 1: Suspend and Analyze

1. STOP all generation/modification work immediately
2. Scan the request for ambiguity points:
   - Unspecified approaches (library choice, algorithm, architecture)
   - Missing business rules (filtering criteria, threshold logic, edge cases)
   - Undefined outputs (format, structure, scope)
   - Implicit assumptions (environment, permissions, conventions)
   - Unclear scope (what's in/out of bounds)

### Phase 2: Raise Questions

For each ambiguity point, make the decision substance explicit, then select the preview representation from the decision's granularity and communicative fit. Whether the surrounding task contains code does not select the representation.

This phase does not apply to a field governed by the Missing-Field Protocol (missing-field-protocol.md); that protocol's plain field request replaces options, representations, and defaults.

**Package grouping**: bundle every open decision point into a single **logical** clarification package (minimal but complete) and include the standing items below; "at once" means one round, not necessarily one call — the delivery path is fixed by the routing rule in the Overview.

### Standing Package Items

- **State-persistence item (exact line)**: "Write durable state to `<working-dir>/.agent/state/` (enabled by default); confirm / correct." Include it whenever `.agent/state/` does not yet exist or is being (re)initialized.
- **State-reconcile item**: only when existing state is stale / inexplicable / inconsistent with the current project status — offer overwrite-from-scratch, amend-on-top, or leave (move / absent); see context-drift-governance.md, File Hygiene.

### Required Decision Substance

Every non-trivial clarification point MUST include:

- **Question and option identity:** the exact decision and clearly distinguishable options
- **Plan brief and insights:** what each option does and the decisive reasoning
- **Cascading changes:** affected API/SPI behavior, business semantics, architecture, consumers, artifacts, and concrete symbols when known
- **Critical change preview:** the smallest fitting representation that makes the decisive change concrete and reviewable
- **Trade-off analysis or caveats:** benefits, costs, risks, losses, assumptions, and operational consequences
- **Recommended default:** one option, its explicit assumptions, and a design-based reason
- **Preview status:** whether the preview is `exact`, `illustrative`, `assumed`, or `pending verification`, and whether it is applied or non-applied
- **Permission status:** whether the output is clarification/recommendation only, generation is permitted, or target-specific edit approval exists

These are representation-invariant semantic requirements. Section labels may be compacted when the meaning remains recognizable; no particular rendering form satisfies the requirements by itself.

```markdown
### Clarification N: [Short title]

**Question:** [One-sentence exact aspect awaiting decision]

**Option A: [name]**

**Plan brief and insights:** [approach and decisive reasoning]

**Cascading changes:** [concrete affected behavior, symbols, consumers, and artifacts]

**Critical change preview:**
- Representation: [prose / if-then / table / flow / contract / schema / example / diff / other]
- Status: [exact / illustrative / assumed / pending verification], [applied / non-applied]
- Anchor: [decisive slice in the selected representation]

**Trade-off analysis or caveats:** [upsides, downsides, risks, and assumptions]

**Recommended default: Option X.** [reason and explicit assumptions]

**Permission status:** [clarification/recommendation only / generation permitted /
target-specific edit approval and scope]
```

### Representation Selection

Choose the representation by applying these gates in order:

| Gate | Decision test | Selection |
|------|---------------|-----------|
| **1. Explicit direction** | Did the user explicitly require a representation? | Prefer it within instruction precedence while preserving all required decision substance; a requested diff still must pass all five diff gates. |
| **2. Diff eligibility** | Do ALL five diff gates below pass? | A minimal non-applied diff may be the primary preview. |
| **3. Conditional outcome** | Do material conditions change the recommendation or result? | Use grouped `if ... then ...` branches or a decision table. |
| **4. Structural relationship** | Is the decision primarily a comparison, sequence/state transition, contract, data shape, or architecture/ownership split? | Use respectively a table, flow/diagram, contract or pseudo-signature, schema/example, or component/responsibility view. |
| **5. Minimal fallback** | Would no specialized form improve reviewability? | Use concise natural language, a BEFORE/AFTER outline, or sampled critical intentions. |

Select the smallest anchor that exposes the decision. Do not use a diff merely because implementation would eventually change code.

#### Diff Eligibility — All Five Gates Required

A diff may be the primary preview only when ALL five gates pass:

1. **Exact locus:** One existing artifact and the exact symbol, clause, or contiguous region are known.
2. **Line granularity:** The literal lines or wording are themselves the decision surface.
3. **Bounded surface:** One locus and no more than 8 decisive changed lines fully represent the decision.
4. **Semantic completeness:** The diff exposes the decision without hiding architecture, state transitions, compatibility effects, downstream behavior, or other material semantics.
5. **Fidelity:** The exact before-state was inspected; the preview contains no invented context or placeholders.

Failure of any gate prohibits a diff as the primary preview. After a complete non-diff primary anchor, a mini-diff may supplement a local detail only when labeled **Supplementary mini-diff**, marked `exact` or `illustrative`, and kept separate from the decision's primary representation. It never substitutes for missing cascade analysis or hidden semantics.

#### Non-Diff Reviewability — All Gates Required

A non-diff preview is reviewable only when ALL of these gates pass:

1. It identifies its representation.
2. It states a baseline-to-target or condition-to-result relationship.
3. It names concrete actors, symbols, consumers, or artifacts, or explicitly marks their discovery as pending.
4. It states at least one observable consequence.
5. It marks content as `exact`, `illustrative`, `assumed`, or `pending verification`.
6. It shows only the decisive slice and records wider effects under cascading changes.

Vague prose such as "improve the architecture" or "handle errors better" fails these gates even when it is concise.

#### Selection Matrix

| Decision surface | Preferred primary representation |
|------------------|----------------------------------|
| Fine-grained code or documentation wording | Diff only if all five diff gates pass; otherwise exact excerpt plus BEFORE/AFTER intent |
| API/SPI behavior contract | Contract statement, pseudo-signature, or BEFORE/AFTER behavior table |
| Architecture or ownership | Component/flow diagram, responsibility table, or concise ownership contract |
| Conditional business or runtime behavior | `if ... then ...` branches or decision table |
| Workflow, lifecycle, routing, or state | Sequence, flow, or state-transition representation |
| Schema, configuration shape, or structured data | Schema, field table, or representative input/output example |
| Consultant recommendation | Grouping selected by conditions; preview selected independently by these gates |
| Broad non-code decision | Concise prose, comparison table, BEFORE/AFTER outline, or concrete example |

#### Balanced Examples

Fine-grained diff example (eligible only when the exact locus and inspected before-state are true in the active task):

````markdown
**Critical change preview:**
- Representation: diff
- Status: exact, non-applied
- Locus: `settings.toml`, key `timeout_seconds`

```diff
-timeout_seconds = 30
+timeout_seconds = 45
```

Observable consequence: requests may run for 15 seconds longer before timeout.
````

Broad architecture example:

```markdown
**Critical change preview:**
- Representation: responsibility table
- Status: illustrative, non-applied
- Baseline → target: peer identity is derived in multiple layers → the acceptor
  validates the endpoint once and the server owns identity formatting.

| Actor | Target responsibility | Observable consequence |
|-------|-----------------------|------------------------|
| Acceptor | Validate the peer endpoint and pass structured data | Lookup failure rejects only that peer |
| Server | Format and own the connection identity | Registration policy remains centralized |

Cascading changes: the connection factory and server creation contract carry
the structured endpoint; presentation and registration behavior stay in the server.
```

### Consultant If-Then Variant

Use this clarification presentation variant only when the user explicitly asks the agent to act as a consultant or advisor, or explicitly requests a recommendation-only or proposal-only deliverable, and material conditions genuinely change the recommendation. A no-write, deferred-work, or read-only status alone does NOT activate consultant mode. If role or deliverable intent is unclear, raise it as a clarification point rather than inferring the variant.

Group related guidance by its deciding conditions:

```markdown
### Recommendation Group N: [Decision area]

**Question:** [Decision or uncertainty being resolved]

- **If [material condition], then [recommendation].**

  **Plan brief and insights:** [approach and decisive reasoning]

  **Critical change preview:** [use the universal representation-selection
  policy and state the representation and exact/illustrative status]

  **Cascade-changing points:** [API/SPI behavior, business semantics,
  architecture, downstream consumers, and concrete symbols when discoverable]

  **Caveats:** [costs, risks, losses, assumptions, and operational consequences]

- **If [different material condition], then [alternative recommendation].**
  [Repeat the same compact fields.]

**Recommended default:** [branch], assuming [explicit conditions]. [Reason]

**Permission status:** Recommendation only. This preview does not authorize
implementation or workspace modification.
```

When an explicit consultant or recommendation-only request has alternatives that compete under the same conditions, retain the standard Option A/B grouping. Use `if ... then ...` only when conditions genuinely change the recommendation. Consultant mode selects grouping, not preview representation: each option uses the universal representation-selection policy and retains critical preview substance, cascade analysis, caveats, a recommended default, verification obligations, and all permission gates.

If the user later requests implementation, exit the consultant variant. Convert explicitly accepted recommendations and their conditions into constraints, confirm that the selected conditions still hold, and re-enter standard clarification for every unresolved implementation choice. Re-evaluate representation per decision using the universal gates. A prior recommendation, selected default, or proposal preview is not implementation permission.

### Phase 3: Await Resolution

- Present all clarification points to user in a single message
- Explicitly state: "Work deferred until clarification complete"
- If user partially responds, REPEAT the loop with the remaining points only; items the user did not address stay `awaiting`/`deferred` with `pending_reason` recorded
- If the user says "just proceed" without addressing points, no item resolves (DO-2b): proceed only under Phase 4, with assumptions declared and marked `assumed`, and list which assumptions are being used
- An item resolves only on a reply that is type-conforming to its `question_form` and unambiguous about the option or default it selects (DO-1); any other reply defers (DO-2)
- Never default-resolve the source/canonical input selection, the files or other targets authorized for editing, or edit approval itself; these require an explicit user decision

### Phase 4: Permission Gate

Generation of implementation content is PROHIBITED until ONE of these conditions is met:
- User explicitly uses permission terms: "permitted", "cleared", "generate", "proceed", "go ahead"
- User has explicitly decided on every clarification point
- User has waived clarification with explicit default acknowledgment

**If in doubt about permission: default to analyst mode (no writing).**

**Permission is not resolution.** A permission term ("permitted", "cleared", "generate", "proceed", "go ahead") satisfies this gate for *execution* only and resolves no clarification item (DO-2b). An item closes only under DO-1.

Generation permission and edit approval are distinct. Permission to draft or generate content does not authorize modifying an unresolved target. Before writing, the user must have explicitly approved the target files or an unambiguous scope that includes them; a general permission term may carry edit approval only when the requested write scope was already explicit. Apply `pre-edit-safety.md` to determine authoritative on-disk code or file state immediately before any write.

The gate also covers the channel itself: asking clarification questions about forbidden or unpermitted edits via an ask_user-class tool is prohibited (Clarification Channel Governance §B).

## Clarification Channel Governance

**Applicability**: This section governs any interactive clarification/approval channel exposed by the host — a tool named `ask_user`, an approval-request tool, or any similarly purposed tool/hook that returns user answers in-session. Determine presence/absence/name at skill load time and record it in the constraints file (`CHANNEL: available|absent|unknown`). If no such channel exists, §B/§C read with "the channel" as "structured clarification questions by any means", and §A is inert.

### §A — Non-Resolution Response Handling

An empty response, a system-default auto-response, or a timeout-fallback from the channel is NOT a resolution and NOT consent to "proceed with default". The same applies to any reply that is **not type-conforming and unambiguous** under DO-1 — for example a bare "ok" or "yes" returned to a `selection` item — and to an item the user did not address inside a partially answered package. Upon receiving any of these, the agent MUST, in order:

1. Mark every point raised in that channel call as `deferred` in the pending-clarifications file.
2. Halt the entire round — no further generation/modification/tool calls on task material, even for points answered earlier in the round. Phase 3's "just proceed → apply defaults" branch does NOT apply.
3. Persist before halting: (a) decisions made so far (resolved points + rationale) to the constraints file; (b) a `next_round_proposal` block (see context-drift-governance.md) carrying any work proposal derivable from those decisions, marked `UNEXECUTED`; (c) the deferred points with the exact questions to re-ask.
4. **Re-route, never re-ask.** The halt output MUST carry the full clarification package as plain text in the session output — the session-output delivery path defined in the Overview — so the user can answer in their next message without another tool call. The agent MUST NOT re-issue the channel call for those items. If a second channel call for the same items has already returned a system-default, DO-2c's escalation guard applies instead of any third call.
5. End output with the notice template below and await the user's next message. Resumption requires explicit user answers.

```markdown
Round halted: clarification returned an empty/system-default response.
Deferred: [points]. State persisted to [state-file path]; next-round proposal is UNEXECUTED.
The full package is re-presented in plain text below; no further channel call will be made for these items.
Awaiting your answer on the deferred points.
```

### §B — No Clarify-Into-Forbidden-Work

If the user has said "defer work"/"no code/workspace edits", or has not explicitly permitted modifying specific files, the agent MUST NOT use the channel to ask *how* to perform those modifications — asking a user who forbade edits "which edit do you prefer" is itself a protocol violation. Questions needed to deliver an explicitly requested consultation or proposal remain allowed when they seek recommendation inputs rather than edit authority or forbidden implementation details. Otherwise, the agent may state in plain text what it would clarify once permitted, and waits.

### §C — User Channel Preference Override

Subject to the user-override principle in `SKILL.md`, explicitly shown user preference about the channel overrides this skill's channel defaults in both directions: "prefer ask_user"/"ask me dynamically during work" → invoke the channel actively when available; "do not use ask_user"/"halt after each round" → never invoke it, use plain-text questions and stop. Record the preference in the constraints file (`CHANNEL_PREFERENCE: default|prefer-ask|no-ask`).

## Decision Ownership (DO-1…DO-3)

Normative home for how a clarification item opens, defers, and closes. `SKILL.md` carries the rule names and a soft pointer to this section, and must not restate the literals.

### §D — Commitment Test, Deferral Set, and Reserved Phrase Table

**DO-1 — Commitment test (type-conformity + unambiguity).** Record each item's `question_form` (`polar` | `selection` | `open`) **before** raising it. A reply **commits** an item when it is (i) **type-conforming** to that question form and (ii) **unambiguous** as to which option or default it selects; a reply that is not both defers that item (DO-2). **Commitment is structural, not literal:** an ordinary affirmative ("yes", "ok", "sounds good", "agreed", "approved") that is type-conforming to a `polar` item commits it, and no reserved-word membership is required to commit. A committed *selection* closes the item as `resolved-explicit`; an unambiguous *grant of discretion* resolves it to the offered default as `resolved-waiver`; an explicit *ratification* of the agent's named default closes it as `resolved-ratified`. The agent's own recommendation never closes an item, and `resolved-default` is not a state and must not be recorded.

**DO-2 — Deferral set.** An item defers — staying `awaiting`/`deferred`, never deleted, merged into a sibling item, or silently dropped, and re-raised with `pending_reason` recorded — when the reply is: an empty return; a system-default auto-response; a timeout submission; an item the user did not address inside a partially answered package; a non-committal answer ("no preference", "whatever", "anything", "doesn't matter", "not sure", "no opinion", "any is fine"); **or any reply that is not both type-conforming and unambiguous under DO-1**. The last clause is what "otherwise it defers, following the existing Channel Governance §A pattern" means: these cases are added *into* §A, and §A is not relaxed.

**DO-2b — Procedural permission resolves nothing.** "just proceed", "proceed", "go ahead", "continue", "just do it" authorize *execution* (Phase 4) and resolve *no* item. They are neither waivers of clarification nor decisions.

**Reserved phrase table (optional fast-path; NOT the commitment test).** The closed list below is a fast-path classifier for recognizing discretion/waiver grants quickly. A reply matching a Class W/R literal resolves under DO-1 without further structural analysis; a reply matching **no** literal is still evaluated structurally by DO-1, so an unlisted or non-English reply can still commit. The list is **English-only** — deliberately not localized, to keep one auditable literal set — and that limit restricts only this fast-path, never the commit path.

- **Class W — grants discretion**, resolving the item to the offered default as `resolved-waiver`: "your discretion", "at your discretion", "your call", "you decide", "you choose", "use your judgment", "as you see fit", "per your recommendation", "go with your recommendation", "I trust your judgment", "do what you think is best", "up to you", "your choice", "either way".
- **Class R — ratifies a named default**, closing the item as `resolved-ratified`: "use the default", "go with the default", "the recommended option is fine", "yes, use your recommendation", "approved as proposed".
- **Class P — procedural permission**, resolving nothing (DO-2b).

A Class W phrase is a grant **only** if a recommended default was actually presented for that item: discretion cannot be granted over a question that was never asked.

**Non-English replies.** Because the table is English-only, a discretion grant phrased in another language does not match the fast-path — but under DO-1 it still **commits** when it is type-conforming and unambiguous. The English-only limit therefore cannot create a deadlock; it only means the agent cannot rely on a literal match to accelerate recognition, and it should still name the reserved English phrasing in its asking output so the user can unblock in one word.

### §E — Default-Identity Guard, Bounded Escalation, and Item States

**DO-2a — Default-identity guard (an evidence guard, not the commitment criterion).** Record `default_offered` for every item *before* raising it. A return byte-identical to the offered default is treated as a **system-default auto-response** and therefore defers (DO-2 / §A) **unless** it also carries explicit ratification: value-equality is not evidence of a decision, because a known, unfixed host defect silently selects the first option, which is commonly the recommended one. Identical value + ratification ⇒ `resolved-ratified`; identical value with ratification absent ⇒ `awaiting`. This guard operationalizes §A's "system-default auto-response" clause for a *non-empty* return; it does not narrow DO-1.

**DO-2c — Bounded escalation, with a terminal disposition.** If the same item defers on two consecutive channel calls, do not issue a third identical call: escalate once in plain text, naming the exact default and the exact waiving phrase, and halt. `escalated` is **terminal**: it closes the item without claiming the user decided it, because the reply was never type-conforming and unambiguous under DO-1. The round-closing output MUST disclose it as unresolved-after-escalation, naming the default and the waiving phrase. The state file therefore reaches zero pending while the decision remains visibly unresolved; no escalated item is ever silently dropped, and escalation never records a resolution state.

**Item states (normative enum).** `awaiting | deferred | resolved-explicit | resolved-ratified | resolved-waiver | escalated`. `resolved-default` is removed: it contradicted "never infer an override from an empty/default response".

### §F — Specification Completeness and the Non-Trivial Test (DO-3)

**DO-3 — Specification-completeness presumption.** A fluent imperative names a deliverable but does not specify its acceptance criteria, so it is underspecified by default. Before treating a request as executable, state which RTCF fields (Role, Task, Context, Format) and which acceptance criteria the user actually supplied, and which the agent inferred. Every inferred field is either raised as a clarification item or declared as a visible stated assumption. Brevity, confidence, and the words "simple" or "just" are not evidence of completeness.

**DO-3a — Non-trivial test (aligned to the low-effort override).** A task is trivial when it is clearly reversible, has one obvious approach, and its outcome is understood before it is run; otherwise it is non-trivial. Size is a guideline, not a threshold — neither file count nor line count decides. A task is non-trivial when ANY of these holds: (a) its outcome could change behaviour, obligations, or durable state beyond the session; (b) it requires three or more distinct decisions or external effects; (c) its scope, output format, or approach is not fully determined by the request. Excluded by rule, not by judgement: skill-mandated governance writes to `.agent/state/` — bookkeeping is never itself a task. This test is the definition of "non-trivial" wherever the skill uses the term for clarification purposes.
  - *Definition confidence: lower.* The phrasing above is grounded in one external source (Google Engineering Practices, "Small CLs": "There are no hard and fast rules about how large is 'too large.'") plus this skill's own low-effort override. It is to be refined if further sources become available.

**DO-3b — Waiver requires explicit wording.** Clarification is waived only by an explicit user instruction to skip it ("skip clarification", "proceed directly to work", "no questions", "don't ask"). Under DO-2b such a waiver permits proceeding but resolves no item: the agent proceeds with its assumptions **declared and marked `assumed`**, and must not record any item as resolved.

## Mid-Work Barrier Detection

During execution, monitor for these signals:
- Starting a sentence with "but wait..."
- Discovering unforseen constraints or requirements
- Realizing the approach needs fundamental change
- Encountering conflicting information that invalidates prior decisions

**Action**: IMMEDIATELY PAUSE work. Enter clarification phase again.

## State Management

Maintain a `pending_clarifications` file in-session and reference it in every output until every item is terminal (§E holds the state enum):

```markdown
# Pending Clarifications

- [ ] P1: [title]
  status: awaiting | deferred | resolved-explicit | resolved-ratified | resolved-waiver | escalated
  raised_in: round [n] via [channel tool name] | plain-text
  question_form: polar | selection | open          # REQUIRED before raising the item
  options: [A: literal] | [B: literal]
  default_offered: [option id + literal text]      # REQUIRED before raising the item
  returned_verbatim: "[exact channel return]" | (empty) | (unaddressed) | (non-committal)
  identity_check: identical | different | not-applicable
  ratification: present("<literal phrase>") | absent | not-applicable
  pending_reason: [why it is not closed]           # REQUIRED whenever status is not terminal
```

`question_form` and `default_offered` must be recorded *before* the item is raised, because DO-1 and DO-2a are incomputable without them.

## Subagent Inspector

When available and appropriate:

1. **Pre-clarification explorer**: Spawn a subagent to search/verify the doubt points before presenting questions to user
2. **Post-clarification supervisor**: Spawn a subagent to verify that the clarification responses are consistent and complete

Use subagents especially for:
- Technical feasibility questions
- Domain-specific best practices
- Compatibility and version concerns
