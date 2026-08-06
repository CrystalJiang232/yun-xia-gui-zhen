# Prompt Engineering Patterns

## Table of Contents

- [RTCF Template](#rtcf-template)
- [Explicit Constraint](#explicit-constraint)
- [Chain-of-Reasoning Trigger](#chain-of-reasoning-trigger)

---

## RTCF Template

### Overview

RTCF (Role-Task-Context-Format) is a universal prompt structuring framework. Use it to decompose any request into four dimensions, ensuring completeness and surfacing implicit assumptions before execution.

### The Four Dimensions

| Dimension | Question to Answer | Example |
|-----------|-------------------|---------|
| **R**ole | What persona, expertise level, or function should the agent adopt? | "Senior Python developer reviewing code for a junior teammate" |
| **T**ask | What specific action or output is required? | "Refactor this function to use async/await pattern" |
| **C**ontext | What background, constraints, or relevant state exists? | "Running on Python 3.11, existing codebase uses asyncio elsewhere, must maintain backward compatibility with Python 3.9" |
| **F**ormat | What structure, style, or delivery format is expected? | "Decision table with concise examples for each option" |

**Format dimension note**: When a prompt mixes content types (instructions, data, examples), separate them with structured delimiters — XML tags OR Markdown headers. Pick one format and apply it consistently; do not mix both in the same prompt.

### Usage Patterns

**Pattern A: Internal decomposition (silent)**
- Apply RTCF mentally before engaging with any user request
- Use it to identify missing pieces that trigger Clarification Protocol
- Do not output the RTCF structure unless helpful

**Pattern B: Explicit output (for complex requests)**
- Restate the user's request in RTCF form to confirm understanding
- Use it as a clarification tool when requirements span multiple dimensions
- Example output:
  ```markdown
  Let me confirm my understanding through the RTCF lens:

  - **Role**: You need me to act as [role]
  - **Task**: The specific action is [task]
  - **Context**: Relevant background includes [context]
  - **Format**: You expect the output as [format]

  Please correct any misinterpretation before I proceed.
  ```

**Pattern C: Self-correction (mid-work)**
- When hitting a barrier or uncertainty, re-evaluate the RTCF decomposition
- A mismatch often reveals the source of confusion
- Example: "I realize my assumed Role may be wrong — let me reconfirm"

### RTCF as Clarification Enabler

RTCF naturally exposes gaps. Missing dimensions become clarification points:
- Missing **Role** → Ask: "From what perspective should I approach this?"
- Missing **Task** → Ask: "What is the specific deliverable or action needed?"
- Missing **Context** → Ask: "What background or constraints should I know?"
- Missing **Format** → Ask: "What form should the output take?"

**Truncation carve-out**: a missing dimension caused by a stripped or truncated instruction (incomplete sentence, invalid structured payload, missing parameter, or out-of-range value) is NOT a normal clarification point. Do not use Pattern B restatement or the missing-dimension questions to solicit options or guesses; apply the Missing-Field Protocol (missing-field-protocol.md) — state the missing field plainly and request completion.

An explicit consultant/advisor role or recommendation-only/proposal-only deliverable routes clarification to the Consultant If-Then Variant in [clarification-protocol.md](clarification-protocol.md) when condition-dependent grouping fits. A no-write, deferred-work, or read-only status alone does not establish that role. If the role or deliverable is ambiguous, clarify it. If the user later requests implementation, return unresolved choices to standard clarification and reselect each decision's representation under that reference's granularity-and-fit rule. Presentation preferences remain subject to the user-override principle in `SKILL.md`.

### Anti-Patterns

- **Over-structuring**: Do not apply RTCF to trivial one-sentence requests
- **Rigidity**: RTCF is a lens, not a cage. Skip dimensions that genuinely do not apply, but document the skip consciously
- **Assumption filling**: Never guess a missing dimension; raise it for clarification

---

## Explicit Constraint

### Overview

Surface and declare all constraints explicitly before generating any output. Implicit constraints are the primary source of implementation drift and requirement mismatch. This pattern forces constraint visibility.

### Constraint Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **Hard Constraints** | Non-negotiable limits that must be satisfied | "Must support Python 3.9+", "Must complete within O(n) time" |
| **Soft Constraints** | Preferred but not mandatory guidelines | "Prefer functional style over OOP", "Ideally under 100 lines" |
| **Negative Constraints** | Explicitly excluded approaches or outputs | "Do NOT use regex for HTML parsing", "No external dependencies allowed" |
| **Implicit Constraints** | Unstated assumptions that need surfacing | User's tech stack, organization conventions, performance expectations |

**Phrasing guidance**: Prefer positive specification of desired behavior. Negative constraints are for exclusions that cannot be positively expressed; each negative constraint should carry an alternative where possible.

### Workflow

**Step 1: Constraint Extraction**

From the user's request, extract all explicitly stated constraints. Then probe for implicit ones:

```markdown
# Constraint Extraction for [task-name]

## Explicit Constraints
1. [constraint] — Source: user stated
2. [constraint] — Source: user stated

## Implicit Constraints (need confirmation)
1. [constraint] — Reasoning: [why you think this might apply]
2. [constraint] — Reasoning: [why you think this might apply]

## Constraint Conflicts
- [ ] Conflict A vs B — Resolution needed: [options]
```

**Step 2: Constraint Declaration**

Restate all confirmed constraints in a single canonical location. This becomes the canonical constraint record for the task. For code and file authority immediately before a write, follow `pre-edit-safety.md` rather than treating the constraint record as a substitute for current on-disk state.

**Step 3: Constraint Checking**

Before marking any task complete, verify all hard constraints are satisfied. Use Verification Hooks for this check.

### Integration with Context Drift Governance

The Explicit Constraint pattern feeds directly into the CTAGV loop:
- **Phase C (Constraints)**: Use constraint extraction to build the constraints file
- **Phase T (Task)**: Reference declared constraints when planning task steps
- **Phase V (Verify)**: Validate output against all hard constraints

### Placement of Key Constraints

Key instructions and hard constraints should be placed at the prompt's start and restated at the end. Models exhibit a U-shaped position bias — content at the beginning and end receives more attention than content in the middle ("Lost in the Middle", TACL 2024). Avoid burying critical constraints mid-prompt.

### Anti-Patterns

- **Constraint omission**: Skipping implicit constraint surfacing because "the user would have mentioned it"
- **Constraint invention**: Assuming constraints that do not exist
- **Soft constraint enforcement**: Treating soft constraints as hard without confirmation
- **Emphasis marker overuse**: Emphasis markers (bold, caps) must be sparse and consistent; indiscriminate use dilutes their signal. (A research-derived principle from format-sensitivity studies; no authoritative quantitative threshold exists.)
- **One-shot constraint stuffing**: Start with a minimal prompt and add constraints incrementally; avoid stuffing templates and examples into a single up-front prompt. (Directionally confirmed guidance.)

---

## Chain-of-Reasoning Trigger

### Overview

A technique to force step-by-step reasoning before reaching conclusions. Applied when tasks involve complex decisions, trade-off analysis, debugging, or any scenario where jumping to conclusions risks error.

### Trigger Conditions

**Model-conditional exemption**: When the host model has built-in reasoning capability (reasoning models / extended thinking), explicit step-by-step triggers are redundant and may degrade quality — keep prompts minimal and use the REASON structure only as a post-hoc self-check (Pattern C). For non-reasoning models, the conditions below apply unchanged.

Activate Chain-of-Reasoning when ANY of these are true:
- Multiple valid approaches with different trade-offs
- Debugging or root-cause analysis
- Performance or architectural decisions
- Complex conditional logic design
- Trade-off evaluation (speed vs memory, simplicity vs robustness, etc.)
- Prioritization or sequencing decisions

### The REASON Structure

A structured reasoning chain follows these phases:

| Phase | Action | Output |
|-------|--------|--------|
| **R**eview | State what you understand the problem to be | Problem restatement |
| **E**xplore | List all viable approaches or factors | Options inventory |
| **A**nalyze | Evaluate each option against declared constraints | Trade-off matrix |
| **S**elect | Choose the optimal option with justification | Decision with rationale |
| **O**utline | Plan the implementation or response structure | Step-by-step plan |
| **N**ext | Execute and verify | Action with checkpoint |

### Usage Patterns

**Pattern A: Silent reasoning (internal monologue)**
- Apply REASON structure mentally
- Show only the conclusion and key decision points to user
- Use when reasoning is straightforward and user trusts the process

**Pattern B: Explicit reasoning (visible to user)**
- Output the full REASON structure
- Use when decisions are contentious, trade-offs are significant, or user needs to audit the reasoning
- Format:
  ```markdown
  Let me work through this step by step:

  **R — Review**: The problem is [restatement]
  **E — Explore**: Options include [list]
  **A — Analyze**: [trade-off evaluation]
  **S — Select**: I choose [option] because [rationale]
  **O — Outline**: Plan is [steps]
  **N — Next**: Proceeding with [action]
  ```

**Pattern C: Self-check reasoning (verification)**
- After reaching a conclusion, apply REASON retroactively
- Check if the conclusion holds up when forced through the structure
- Use at Verification Hooks to catch reasoning errors

### Anti-Patterns

- **Reasoning theater**: Using Chain-of-Reasoning as decoration without genuine analysis
- **Premature selection**: Deciding on an approach before completing the Explore phase
- **Missing trade-offs**: Analyzing options without honest evaluation of downsides
- **Infinite reasoning**: Getting stuck in analysis paralysis; set explicit time/depth limits
