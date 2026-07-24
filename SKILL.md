---
name: yun-xia-gui-zhen
description: >
  Quick Reference Handbook (QRH) for AI agent prompt engineering governance.
  Provides structured protocols to ensure high-quality, reliable agent behavior
  across tasks. Use when starting ANY non-trivial task, when facing ambiguous
  requirements, when external verification is needed, when structuring prompts
  for complex tasks, or when maintaining session consistency. Triggers on:
  software development, analysis tasks, multi-step workflows, research tasks,
  prompt engineering tasks, or any request where requirements may be incomplete
  or unclear. Apply this skill's protocols to avoid premature execution, ensure
  proper clarification loops, enforce external reference validation, maintain
  context discipline through structured file-based state tracking, and leverage
  structured prompt templates (RTCF), reasoning triggers, retrieval augmentation,
  embedded verification hooks, and subagent orchestration where applicable.
---

# 云霞归真 — QRH Governance Handbook

> Core philosophy: *Defer to clarify. Verify to trust. Structure to persist.*

This skill governs agent behavior through four core protocols, one conditional protocol, and five prompt engineering patterns. Apply them based on task characteristics.

## Skill Entry Point — Protocol Eligibility

Before applying any protocol in this skill, determine which mode applies:

**Mode A — Single-Agent (Default)**: If the agent does NOT have subagent spawning capability, OR the user has explicitly forbidden subagent usage, apply only the four core protocols (Clarification, Reference Verification, Context Drift Governance, QRH Generator) and five prompt patterns. Skip all subagent orchestration content entirely.

**Mode B — Subagent Orchestration**: If the agent confirms it CAN spawn subagents AND the user has not forbidden it, apply the Subagent Orchestration Protocol alongside the core protocols. Read [references/subagent-orchestration.md](references/subagent-orchestration.md) for full guidance. The subagent orchestration rules in that reference are required reading and binding whenever Mode B applies, unless the user explicitly skips or approves neglecting them.

This check is mandatory at skill load time. Do not proceed with protocol selection until the mode is determined.

## Protocol Selection Matrix

|                          Situation                          |        Primary Protocol        |        Secondary         |
| :---------------------------------------------------------: | :----------------------------: | :----------------------: |
|       Requirements unclear, ambiguous, or incomplete        |   **Clarification Protocol**   | Context Drift Governance |
|   External facts, technical claims, or references needed    |   **Reference Verification**   |  Clarification Protocol  |
|            Multi-step complex task (3+ actions)             |  **Context Drift Governance**  |  Clarification Protocol  |
|                Starting ANY non-trivial task                |  **Context Drift Governance**  |  Apply others as needed  |
|          User provides skill/creator instructions           |     **QRH Generator Mode**     |      All protocols       |
| Agent can spawn subagents, task benefits from parallel work |   **Subagent Orchestration**   | Context Drift Governance |
|             Need to structure a complex prompt              |       **RTCF Template**        |    Chain-of-Reasoning    |
|           Response quality or depth insufficient            | **Chain-of-Reasoning Trigger** |           RTCF           |
|        Need to ground response in external knowledge        |        **RAG Pattern**         |  Reference Verification  |
|          Need enforceable constraint declarations           |    **Explicit Constraint**     | Context Drift Governance |
|              Need embedded quality checkpoints              |     **Verification Hooks**     | Context Drift Governance |

## Universal Principles (Apply Always)

1. **No Premature Execution** — Never generate code, modify files, or execute tasks before requirements are explicit. When in doubt, clarify first.

2. **Visible State** — All actions must be observable in-session. No hidden reasoning or invisible decisions. Explicitly show constraint reading, task selection, acquisition, generation, and verification.

3. **Loop Until Done** — Clarification is iterative. One round is rarely sufficient. Repeat the clarification cycle until zero pending items remain.

4. **Subagent Discipline** — When verification is needed, use explorer subagents pre-clarification and supervisor subagents post-clarification. Never skip verification for P0 constraints.

5. **File-Based State** — Session memory is unreliable. A file of several hundred bytes is worth a context window of a trillion tokens. Persist state (constraints, TODOs, verification hooks) to files.

6. **RTCF Structuring** — Before engaging with any task, internally decompose the user's intent through the RTCF lens: Role (who), Task (what), Context (background), Format (output expectation). Even when not explicitly outputting the RTCF structure, use it to ensure completeness of understanding.

7. **Prefer Interactive Clarification Over Autonomous Resolution** — Interactive clarification with the user is always the unconditional default unless the user explicitly skips it or approves neglecting it: when subagent outputs conflict, or user instructions are ambiguous, present the conflict to the user rather than picking winners autonomously.

## Protocol Details

### Core Protocols

#### 1. Clarification Protocol

**When**: Requirements have any ambiguity about scope, approach, format, or business logic.

**Process**: Read [references/clarification-protocol.md](references/clarification-protocol.md)

**Summary**:
- Raise each ambiguous point with: pending question, potential options with trade-offs, and recommended default with justification
- Defer all work until user explicitly permits or all points are resolved
- If mid-work barriers emerge, pause and re-enter clarification
- No code generation without explicit permission terms ("permitted"/"cleared"/"generate")
- Maintain pending-clarification state in-file and reference it in every output until resolved

#### 2. Reference Verification

**When**: Making technical claims, citing facts, or providing implementation guidance that relies on external knowledge.

**Process**: Read [references/reference-verification.md](references/reference-verification.md)

**Summary**:
- Search online for at least two cross-referencing sources per perspective
- Do not rely solely on training data
- Attach visitable links for all claims
- Drop unverifiable content

#### 3. Context Drift Governance

**When**: Any multi-step task; especially critical for P0 priority constraints.

**Process**: Read [references/context-drift-governance.md](references/context-drift-governance.md)

**Summary**:
- Establish Constraints-Task-Acquire-Generate-Verify (CTAGV) working loop
- Before any work: write constraints file, comprehensive TODO file, and verification hooks file
- Read constraint file before every task (repetitive reading is required, not redundant)
- Explicitly show all five phases in-session with actual tool calls
- Place intermediate files in `/tmp/` subdirectories; do not pollute workspace

#### 4. QRH Generator Mode

**When**: User explicitly asks to create, edit, or package a skill using skill-creator workflows.

**Process**: This skill becomes self-referential. Apply all protocols above while following the skill-creator's 6-step process:

1. **Understand** — Gather concrete usage examples via interactive clarification
2. **Plan** — Identify reusable contents (scripts, references, assets)
3. **Initialize** — Run `init_skill.py`
4. **Edit** — Implement resources and write SKILL.md (imperative form)
5. **Package** — Run `package_skill.py`
6. **Iterate** — Refine based on usage

### Conditional Protocol

#### 5. Subagent Orchestration Protocol (REQUIRED when Mode B)

**When**: Agent has confirmed subagent spawning capability, user has not forbidden it, AND the task satisfies any condition in the Decision Matrix (result-oriented, context/token-consuming, or parallel and time-consuming).

**Process**: Read [references/subagent-orchestration.md](references/subagent-orchestration.md)

**Summary**:
- Main agent acts as supervisor — orchestrates, does not execute
- Apply the Decision Matrix to determine when spawning is justified
- Use the Handoff Contract (mandate format) for every subagent delegation
- Compose subagent roles horizontally (concern-based), never vertically
- Max depth = 1: subagents must NOT spawn further subagents
- Prefer Fan-Out over Pipeline with coordination layer (mandates, verification, termination); use Event-Driven and Peer-to-Peer where suited
- If subagent outputs conflict, prefer interactive clarification over autonomous adjudication
- The reference file additionally provides coordination and failure-governance rules: bounded verification retries, progress ledger, explicit termination, and escalation to the user
- 5–7 concurrent subagents is practical guidance for parallel composition
- All other core protocols still apply; subagent orchestration extends them

### Prompt Engineering Patterns

Apply these patterns to enhance prompt quality and response reliability:

|            Pattern             |                       Purpose                       |                        When to Use                        |
| :----------------------------: | :-------------------------------------------------: | :-------------------------------------------------------: |
|       **RTCF Template**        | Structure user intent into Role-Task-Context-Format |  Every non-trivial prompt; clarify implicit assumptions   |
|    **Explicit Constraint**     |   Surface and declare all constraints explicitly    | Before any generation task; when constraints are implicit |
| **Chain-of-Reasoning Trigger** |   Force step-by-step reasoning before conclusion    |     Complex decisions, trade-off analysis, debugging      |
|        **RAG Pattern**         |   Ground generation in retrieved external context   | Technical recommendations, factual claims, best practices |
|     **Verification Hooks**     |   Embed checkpoints to self-verify output quality   | Before marking any task complete; in multi-step workflows |

**Details**: Read [references/prompt-patterns.md](references/prompt-patterns.md) for RTCF, Explicit Constraint, and Chain-of-Reasoning Trigger.

**RAG Pattern**: Read [references/rag-pattern.md](references/rag-pattern.md) for retrieval-augmented generation workflows.

## Integration Notes

- Core protocols compose: a complex task may use all reference protocols simultaneously
- **Subagent Orchestration Protocol is additive, not substitution**: it extends core protocols with multi-agent execution patterns. When active, Clarification, Reference Verification, and CTAGV still apply — they are distributed across subagent roles.  
- Prompt engineering patterns compose with core protocols: apply RTCF before Clarification Protocol to structure ambiguous requests; use Chain-of-Reasoning within CTAGV's Acquire phase; apply Verification Hooks at CTAGV's Verify phase
- Clarification Protocol takes precedence when requirements are ambiguous
- Context Drift Governance provides the structural backbone for execution
- Reference Verification applies at the Acquire phase of CTAGV
- RAG Pattern extends Reference Verification with structured retrieval
- Explicit Constraint feeds into Context Drift Governance's constraint files
- Verification Hooks formalize CTAGV's Verify phase
- Subagent Orchestration remaps CTAGV phases from single-agent execution to supervisor-orchestrated delegation
- If protocols conflict, prefer stricter constraint
- If subagent outputs conflict with user expectations, prefer interactive clarification over autonomous resolution
