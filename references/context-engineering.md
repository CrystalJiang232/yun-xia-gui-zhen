# Context Engineering (Context-Window Governance)

Context engineering is the discipline of curating what enters an LLM's context window at each inference turn — system prompt, instructions, tool definitions, retrieved documents, memory, message history, and prior tool outputs — and how that content is selected, ordered, and compacted. It treats the context window as a finite budget, not a buffer, and drives toward the smallest possible set of high-signal tokens that maximizes the likelihood of the desired outcome. Memory is storage; context is a compiled view.

The 2026 umbrella discipline: treat the context window as a budget — compaction, just-in-time retrieval, memory files, and sub-agents used primarily as context isolation, not as an org chart of little employees.

## When

Any long-horizon, multi-step, tool-using, or retrieval-heavy task; any task where the working set risks exceeding the window, where context contamination is likely, or where durable state must survive compaction. Apply at task start and re-apply at each phase boundary of CTAGV.

## Four operations (after LangChain / Lance Martin)

- **Write** — Author durable, high-signal context outside the window (system instructions, memory files, external state) so it is stable across turns. Failure: Stale Context.
- **Select** — Pull only the relevant context for the current step (top-k retrieval, just-in-time tool load, reference-over-content). Failure: Bloated Context.
- **Compress** — Drop token waste without losing meaning; keep signal per token, not minimum length (summarize history, compact earlier turns, prune superseded tool output). Failure: Bloated Context / Distraction.
- **Isolate** — Keep unrelated context in separate scopes so it cannot interfere; sub-agents as context isolation, per-role workspaces. Failure: Leaking Context.

Broader failure modes: Context Poisoning (contaminated input compounds across iterations), Context Distraction (excess history repeats old patterns), Context Confusion (irrelevant tools/docs obscure the right choice), Context Clash (contradictory information paralyzes decision-making).

## Core techniques

- **Compaction**: on approaching the budget, summarize and restart the loop; keep goals and hard constraints in constraints.md / todo.md — never compress goals.
- **Just-in-time loading**: hold lightweight identifiers (file paths, queries, links) and fetch via tools on demand instead of pre-loading everything.
- **Memory**: short-term thread state (scratchpad, TTL-limited) vs long-term durable state (episodic / semantic / procedural); promote only durable facts.
- **Routing injection vs retrieval**: if the corpus fits the window and is cheap, direct injection can beat retrieval (arXiv 2407.16833); otherwise retrieve. State the route; do not default to RAG.
- **Tool surface**: expose few ergonomic tools; let the model search on demand. If static list-pruning would invalidate KV-cache, prefer logit-level masking during decoding.

## Interaction with this skill

- **Pre-Edit Safety**: keep authorization / backup registry in durable files (Write), not in the window.
- **Context Drift Governance**: compaction anchors and memory hygiene live here; run the four operations per phase boundary.
- **RAG Pattern**: context engineering subsumes RAG as one Select/Compress route (lexical tool search over live files is the default route); keep citation + permission-isolation obligations.
- **Sub-agent Orchestration**: sub-agents as context isolation for read-heavy parallelizable work; one-agent-one-context for write-heavy work; condensed returns only — return-side quarantine lives in [subagent-orchestration.md](subagent-orchestration.md) §4.
- **Guardrail hooks**: enforce a context-budget hook (max tokens / turns / cost) as a stop condition before generation.

## Verification hook

Record (scope, route, retrieved/compacted delta, final budget headroom); PASS if the budget was never exceeded and no poisoning / distraction / clash observed.

## Provenance

Definition: Tobi Lütke, June 19 2025 (Manning, bonigarcia context-engineering). Framework: LangChain "Context Engineering for Agents" (2025). Practitioner basis: Anthropic "Effective context engineering for AI agents" (2025). Failure taxonomy: nv-context definitions research. Umbrella framing: ThibautMelen agentic-ai-systems.
