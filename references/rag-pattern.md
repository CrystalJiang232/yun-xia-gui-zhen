# RAG (Retrieval-Augmented Generation) Pattern

## Table of Contents

- Overview
- When to Activate
- The RAG Workflow
- Retrieved Context
- Synthesis
- RAG vs. Reference Verification
- Failure Modes and Handling
- Anti-Patterns

## Overview

RAG grounds AI-generated content in externally retrieved information rather than relying solely on internal knowledge. Use this pattern when technical accuracy, factual correctness, or up-to-date information is critical.

> **Scope — read first**: In this skill, "RAG" means grounding generation in retrieved context. It does not imply a vector database, embeddings, chunking, or a standing index. Retrieval is whatever tool the agent actually calls; the default for files and workspace corpora is trivial lexical search over live files (`glob`/`find` for names and paths, `rg`/`grep` for content, then `read` on candidates). A semantic index is an inferior-priority branch that activates only when trivial search fails.

> **Context engineering relation**: This pattern is the Select/Compress route of [context engineering](context-engineering.md); see Context-Window Governance for the broader discipline.

## When to Activate

**Routing note**: When all relevant corpus fits in the context window, direct long-context injection can outperform retrieval (arXiv 2407.16833, 9 datasets). Retrieval remains required for dynamic or fast-evolving data and for audit or permission-control needs. Route per situation, not as a universal default: the MEANS may be live tools, trivial lexical search, full-corpus injection, or a semantic index, with the choice stated. Rows marked **Required** below keep their verification obligation regardless of the means.

**Recency-first routing**: for fast-moving or highly time-sensitive topics, route the query to real-time tools/APIs (function calling, live connectors, live search) rather than a static index. Keep the index fresh via incremental indexing on update streams (refresh only changed documents, not a full rebuild), and cache frequently queried results with a TTL plus active invalidation on source update; expose freshness so staleness is observable, not assumed.

**Trivial-first default (files and workspace)**: For file corpora — source code, docs, configs, the workspace — retrieval starts with the simplest exact tools: `glob`/`find` for names and paths, `rg`/`grep` for content patterns, then `read` on candidates. Follow references (imports, includes, symbol definitions) and refine the query before escalating. Agentic grep/glob retrieval reaches RAG-level fidelity for most code-search scenarios without any vector store (arXiv 2602.23368); treat a standing semantic index as the exception.

**Semantic/vector branch (inferior priority)**: Activate this branch only after trivial grep/glob search has demonstrably failed, for example paraphrase-level concept queries over a large, stable corpus. When both a lexical hit and a semantic hit exist for the same need, prefer the lexical/grep result as the more authoritative source: it reflects the live corpus, while a vector index is derivative and lagging. Known vector-branch caveats:

- Drifting or stale index: each commit can invalidate part of the index, and rebuilds lag behind the live corpus.
- Single-shot top-k misses: one retrieval pass is brittle; if the first query misses, the answer is silently absent.
- Exact-match errors: embedding similarity is not relevance; it can return look-alike identifiers and miss true definitions.
- Index as a data copy: a private-corpus index is a standing copy with its own access-control and residency surface.
- Flattened structure: chunked embeddings erase explicit relations (imports, call graphs, types) that lexical tools can traverse.

| Scenario | RAG Activation |
|----------|---------------|
| Recommending specific library versions or APIs | **Required** |
| Citing technical specifications or standards | **Required** |
| Providing code examples for specific frameworks | **Required** |
| Describing best practices that evolve over time | **Required** |
| Answering questions about recent changes (last 1-2 years) | **Required** |
| General algorithmic or architectural concepts | Optional |
| Common programming patterns widely documented | Optional |

## The RAG Workflow

```
One-shot pipeline (index-era shape; brittle when the first query misses):
User Query → Retrieval Query Formulation → Top-k Retrieval → Context Integration →
Grounded Generation → Attribution → Verification

Agentic retrieval loop (default for files and workspace):
User Query → Tool Query (glob/find/rg) → Read Candidates → Evaluate →
Follow References / Refine Query → Repeat until sufficient →
Context Integration → Grounded Generation → Attribution → Verification
```

**Agentic loop rules**:

- Start with the cheapest precise tool; escalate only when results show a concrete gap.
- Prefer exact matching for identifiers and symbols (`rg`/`glob`) over semantic similarity — similarity is not relevance.
- Treat each result as a probe: read candidates, follow imports/definitions/cross-references, and reformulate the query from what you see; never rely on a single top-k shot.
- Read live files over any index whose freshness or coverage you cannot verify; live reads bypass stale-index drift.
- Stop when the question is answerable and keep outputs token-lean. (Agentic loops cost more tokens and latency than precomputed lookup; pay that cost only when task value justifies it.)
- Then run Phases 3-5 for integration, generation, and attribution.

### Phase 1: Retrieval Query Formulation

Transform the user's request into effective search queries:

- **Decompose**: Break complex questions into atomic search queries
- **Keyword optimize**: Use technical terminology, version numbers, official names
- **Multi-angle**: Formulate 2-3 queries from different angles for coverage
- **Temporal awareness**: Include recency qualifiers for fast-moving topics

**Example**:
```
User: "What's the best way to handle authentication in a React app?"
Queries:
1. "React authentication best practices 2024 2025"
2. "React OAuth JWT implementation patterns"
3. "React auth library comparison clerk auth0"
```

### Phase 2: Source Retrieval

Establish Source Authority before retrieval: check workspace files, then system-scope files, then web search results only when the user has broadly authorized web search. Search system-scope files with `find` or `rg`; never assume a package path. On multiple system candidates, stop and ask which one is used unless the compiler/interpreter/library is explicitly declared.

For code and workspace corpora, search live files with `glob`/`find`/`rg` first; these tools are exact, fresh, and index-free. Consult a semantic index only after trivial search demonstrably fails, and state why.

Record provenance and version anchors for any retrieved source that affects output: `Scope`, `Location`, `Version`, `Retrieved`. Mark `Version` as `unverified` when it cannot be established. When local/system and web versions conflict, surface the mismatch and ask.

Execute searches and collect candidate sources. Apply the source hierarchy from Reference Verification Protocol:

1. **Primary sources first**: Official docs, source code, RFCs
2. **Cross-reference**: Find 2+ independent sources confirming the same claim
3. **Recency filter**: Prefer sources within the last 2 years
4. **Diversity**: Mix documentation, tutorials, and source code references

**Permission isolation at the data layer**: enforce access control at retrieval time, not by prompt-level prohibition alone. Attach ACL/permission metadata (identity/role/department/permission groups) to documents/chunks/embeddings, and inject the authenticated principal's entitlements as filter conditions into retrieval queries (never from user-supplied text). Unauthorized content must never enter the model context.

### Phase 3: Context Integration

Integrate retrieved information into the generation context:

```markdown
## Retrieved Context

### Source 1: [Title] ([URL])
[Relevant excerpt or summary]

### Source 2: [Title] ([URL])
[Relevant excerpt or summary]

## Synthesis
[Integrated understanding from all sources]
```

**Rules**:
- Quote directly for precise claims
- Summarize for general understanding
- **Rank and disclose conflicts**: when sources contradict, rank the conflicting evidence by source authority, then recency, then permission level; run an explicit conflict-detection check over retrieved chunks before generation, and **disclose the conflict in the output with citations** rather than silently blending
- Note recency and deprecation warnings
- Place long reference documents first and the user query last when assembling retrieved context (up to +30% response quality per Anthropic long-context guidance)

### Phase 4: Grounded Generation

Generate response using only retrieved context + general reasoning:

- **Attribute every claim**: Link each technical statement to its source
- **Distinguish sourced vs. inferred**: Mark inferred conclusions clearly
- **Handle gaps**: If retrieved context is insufficient, state the gap rather than falling back to unsourced knowledge
- **Prefer sandbox verification**: For code behavior claims, test in isolated environment when retrieval is ambiguous

### Phase 5: Attribution Output Format

Every RAG-grounded response must include source attribution:

```markdown
[Technical claim or recommendation] [^1^](https://source-url)

---
**Sources**:
- [^1^] [Title](https://url) — [relevance note]
- [^2^] [Title](https://url) — [relevance note]
```

## RAG vs. Reference Verification

| Aspect | Reference Verification | RAG Pattern |
|--------|----------------------|-------------|
| **When** | After making a claim | Before/during generation |
| **Scope** | Claim-by-claim fact-check | Full-context grounding |
| **Source usage** | Validate existing content | Build content from retrieval |
| **Integration** | Phase V (Verify) of CTAGV | Phase A (Acquire) + G (Generate) |

**Combine them**: Use RAG during acquisition and generation, then apply Reference Verification during the Verify phase for double-checking.

## Failure Modes and Handling

| Failure | Detection | Response |
|---------|-----------|----------|
| No relevant sources found | Empty or irrelevant search results | State the gap; recommend user provides reference material |
| Conflicting sources | Two sources make contradictory claims | Rank by source authority, then recency, then permission; disclose the conflict with citations in the output and let the user decide or seek an authoritative source |
| Outdated sources | All sources are >2 years old for fast-moving tech | Flag obsolescence risk; recommend verification |
| paywall/blocking | Sources are inaccessible | Search for open-access alternatives; state limitation |

## Anti-Patterns

- **RAG theater**: Citing sources that were not actually consulted
- **Cherry-picking**: Selecting only sources that support a pre-formed conclusion
- **Source laundering**: Using secondary sources without checking primaries
- **Context stuffing**: Including irrelevant retrieved content that dilutes focus
- **Index reflex (vector-by-default)**: Standing up an embedding index where `glob`/`grep`/`read` already answer the question.
