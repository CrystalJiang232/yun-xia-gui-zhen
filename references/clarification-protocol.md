# Clarification Protocol

## Overview

Defer all work until requirements are explicit and exact. This protocol governs the interactive clarification loop between agent and user.

## When to Activate

Activate when ANY of these conditions are met:
- Task description contains words like "maybe", "probably", "whatever", "simple", "just", "similar to"
- Multiple valid implementation approaches exist
- Task is code-type (implementation, refactor, API/SPI change) AND clarification is entered → the Tier-2 option format below is MANDATORY, not optional
- Task is non-code-type but non-trivial AND clarification is entered → the Tier-1 option format below applies (weak trigger: same semantics, relaxed format)
- Business logic involves filtering, thresholds, or conditional rules
- Output format, target environment, or constraints are unspecified
- User says "do what you think is best" without prior established patterns

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

For each ambiguity point, produce a structured entry:

```markdown
### Clarification Point N: [Brief Title]

**Question**: [One-sentence exact aspect awaiting decision]

**Options**:
- **Option A**: [description] — [trade-off]
  ```python
  # inline code sample if relevant
  ```
- **Option B**: [description] — [trade-off]

**Default**: [Option X] — [one-sentence reason]
```

### Option Depth Tiers

**Tier 2 — Code-type tasks (MANDATORY when the code-type trigger above fires).**

Every option MUST carry all four sections below, with verbatim section labels. Keep each section to 1–3 sentences; the diff preview shows only the minimal critical segment (~5–8 lines), not a full patch. Cascading changes must name concrete symbols (functions, interfaces, modules), not abstractions.

**Exception — architectural-level decisions:** When the clarification point concerns non-code-level decisions within a code task — overall workflow, API behavior contracts, business logic amendments, or any architectural design choice — the diff-style preview MAY be omitted, or expressed in any abstract form that fits: BEFORE/AFTER behavior tables, sequence or flow descriptions, contract statements, pseudo-signatures, or any equivalent representation. Do NOT confine the preview to a fixed set of expressions; the requirement is that the change be made concrete and reviewable, not that it look like a diff. All other sections (plan brief, cascading changes, trade-off analysis, recommended default) remain mandatory regardless.

```markdown
### Clarification N: [Short Title]

**Question:** [One-sentence exact aspect awaiting decision]

**Option A: [name]**

**Plan brief and insights:** [what this approach does, key insight]

**Cascading changes:** [API/SPI behavior, business logic/semantics,
architecture-level program behavior affected — name concrete symbols]

**Critical code diff preview:**
```diff
-old_critical_segment()
+new_critical_segment()
```

**Trade-off analysis:** [honest upsides AND downsides — state what this option loses]
```

After the last option, once per clarification point:

```markdown
**Recommended default: Option X.** [reason arguing from design principle,
explicitly dismissing weaker justifications where relevant]
```

Anchoring example (canonical form, from a C++ accept-loop fix):

```markdown
**Option A: Pass a validated `tcp::endpoint` by value**

**Plan brief and insights:** Perform one non-throwing lookup in
`do_accept()`. Reject that peer and continue on failure. Pass the endpoint
by value to `server`, which formats and owns the connection ID.

**Cascading changes:** `connectionFactory`, its lambda, and
`server::create_connection()` gain a `tcp::endpoint` parameter. The socket
formatter is removed. Registration and session semantics remain under `server`.

**Critical code diff preview:**
```diff
-auto peer = socket.remote_endpoint();
+boost::system::error_code ec;
+auto peer = socket.remote_endpoint(ec);
+if (ec) { LOG_WARN(...); continue; }
+factory(std::move(socket), peer, core_id, io);
```

**Trade-off analysis:** Best match for the apparent architecture and future
structured peer data. It changes an internal interface, which is acceptable
here. Address presentation still needs a checked conversion inside `server`.

**Recommended default: Option A.** It removes duplicate inspection while
preserving `server` ownership of identity policy — for architectural
reasons, not compatibility.
```

**Tier 1 — Generalized (weak trigger: any non-code-type but non-trivial task entering clarification).**

The same semantics apply — plan brief and insights, cascading changes, change preview, trade-off analysis, recommended default with reason — but the format is relaxed: the strict `diff`-style preview is NOT required. Instead, show the changes in whatever form fits the domain: sampled/critical intentions, before→after outline, excerpt preview, schema or sample-output preview, or step-sequence preview. "Cascading changes" generalizes to impact on downstream consumers, existing artifacts, and prior decisions. Section labels should still be recognizable, but brevity and domain-fit take precedence over rigid structure.

> **TODO (placeholder for future completion):** An anchoring output sample for non-code-type tasks is currently ABSENT. Until one is added, refer to the Tier-2 code-type anchoring example above and adapt its semantics to the domain. This placeholder marks a known gap for future implementation/addition/completion of this skill.

### Phase 3: Await Resolution

- Present all clarification points to user in a single message
- Explicitly state: "Work deferred until clarification complete"
- If user partially responds, REPEAT the loop with remaining points
- If user says "just proceed" without addressing points, apply defaults but explicitly list which defaults are being used

### Phase 4: Permission Gate

Code generation is PROHIBITED until ONE of these conditions is met:
- User explicitly uses permission terms: "permitted", "cleared", "generate", "proceed", "go ahead"
- User has explicitly decided on every clarification point
- User has waived clarification with explicit default acknowledgment

**If in doubt about permission: default to analyst mode (no writing).**

The gate also covers the channel itself: asking clarification questions about forbidden or unpermitted edits via an ask_user-class tool is prohibited (Clarification Channel Governance §B).

## Clarification Channel Governance

**Applicability**: This section governs any interactive clarification/approval channel exposed by the host — a tool named `ask_user`, an approval-request tool, or any similarly purposed tool/hook that returns user answers in-session. Determine presence/absence/name at skill load time and record it in the constraints file (`CHANNEL: available|absent|unknown`). If no such channel exists, §B/§C read with "the channel" as "structured clarification questions by any means", and §A is inert.

### §A — Empty/Default Response Handling

An empty response, system-default auto-response, or timeout-fallback from the channel is NOT a resolution and NOT consent to "proceed with default". Upon receiving one, the agent MUST, in order:

1. Mark every point raised in that channel call as `deferred` in the pending-clarifications file.
2. Halt the entire round — no further generation/modification/tool calls on task material, even for points answered earlier in the round. Phase 3's "just proceed → apply defaults" branch does NOT apply.
3. Persist before halting: (a) decisions made so far (resolved points + rationale) to the constraints file; (b) a `next_round_proposal` block (see context-drift-governance.md) carrying any work proposal derivable from those decisions, marked `UNEXECUTED`; (c) the deferred points with the exact questions to re-ask.
4. End output with the notice template below and await the user's next message. Resumption requires explicit user answers.

```markdown
Round halted: clarification returned an empty/system-default response.
Deferred: [points]. State persisted to [state-file path]; next-round proposal is UNEXECUTED.
Awaiting your answer on the deferred points.
```

### §B — No Clarify-Into-Forbidden-Work

If the user has said "defer work"/"no code/workspace edits", or has not explicitly permitted modifying specific files, the agent MUST NOT use the channel to ask *how* to perform those modifications — asking a user who forbade edits "which edit do you prefer" is itself a protocol violation. The agent may state in plain text what it would clarify once permitted, and waits.

### §C — User Channel Preference Override

Explicitly shown user preference about the channel overrides this skill's defaults, in both directions: "prefer ask_user"/"ask me dynamically during work" → invoke the channel actively; "do not use ask_user"/"halt after each round" → never invoke it, use plain-text questions and stop. Record the preference in the constraints file (`CHANNEL_PREFERENCE: default|prefer-ask|no-ask`).

## Mid-Work Barrier Detection

During execution, monitor for these signals:
- Starting a sentence with "but wait..."
- Discovering unforseen constraints or requirements
- Realizing the approach needs fundamental change
- Encountering conflicting information that invalidates prior decisions

**Action**: IMMEDIATELY PAUSE work. Enter clarification phase again.

## State Management

Maintain a `pending_clarifications` file in-session:

```markdown
# Pending Clarifications

- [ ] Point 1: [title] — Status: awaiting / resolved-default / resolved-explicit
- [ ] Point 2: [title] — Status: awaiting / resolved-default / resolved-explicit
```

Reference this file in every output until ALL items are resolved.

## Subagent Inspector

When available and appropriate:

1. **Pre-clarification explorer**: Spawn a subagent to search/verify the doubt points before presenting questions to user
2. **Post-clarification supervisor**: Spawn a subagent to verify that the clarification responses are consistent and complete

Use subagents especially for:
- Technical feasibility questions
- Domain-specific best practices
- Compatibility and version concerns
