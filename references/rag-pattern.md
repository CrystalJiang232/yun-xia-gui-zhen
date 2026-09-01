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

> **Context engineering relation**: This pattern is the Select/Compress route of [context engineering](context-engineering.md); see Context-Window Governance for the broader discipline.

## When to Activate

**Routing note**: When all relevant corpus fits in the context window, direct long-context injection can outperform retrieval (arXiv 2407.16833, 9 datasets). RAG remains required for dynamic or fast-evolving data, cost/latency-sensitive cases, and audit or permission-control needs. Route per situation, not as a universal default: rows marked **Required** below keep their verification obligation, but the MEANS may be retrieval OR full-corpus injection, with the choice stated.

**Recency-first routing**: for fast-moving or highly time-sensitive topics, route the query to real-time tools/APIs (function calling, live connectors, live search) rather than a static index. Keep the index fresh via incremental indexing on update streams (refresh only changed documents, not a full rebuild), and cache frequently queried results with a TTL plus active invalidation on source update; expose freshness so staleness is observable, not assumed.

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
User Query → Retrieval Query Formulation → External Search →
Source Evaluation → Context Integration → Grounded Generation →
Attribution → Verification
```

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
