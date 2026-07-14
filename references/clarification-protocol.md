# Clarification Protocol

## Overview

Defer all work until requirements are explicit and exact. This protocol governs
the interactive clarification loop between agent and user.

## When to Activate

Activate when ANY of these conditions are met:
- Task description contains words like "maybe", "probably", "whatever",
"simple", "just", "similar to"
- Multiple valid implementation approaches exist
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

### Phase 3: Await Resolution

- Present all clarification points to user in a single message
- Explicitly state: "Work deferred until clarification complete"
- If user partially responds, REPEAT the loop with remaining points
- If user says "just proceed" without addressing points, apply defaults but
explicitly list which defaults are being used

### Phase 4: Permission Gate

Code generation is PROHIBITED until ONE of these conditions is met:
- User explicitly uses permission terms: "permitted", "cleared",
"generate", "proceed", "go ahead"
- User has explicitly decided on every clarification point
- User has waived clarification with explicit default acknowledgment

**If in doubt about permission: default to analyst mode (no writing).**

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

1. **Pre-clarification explorer**: Spawn a subagent to search/verify the
doubt points before presenting questions to user
2. **Post-clarification supervisor**: Spawn a subagent to verify that
the clarification responses are consistent and complete

Use subagents especially for:
- Technical feasibility questions
- Domain-specific best practices
- Compatibility and version concerns
