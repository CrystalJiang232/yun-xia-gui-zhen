# Reference Verification Protocol

## Overview

All technical claims, factual statements, and implementation guidance must be externally verifiable. Do not rely solely on training data.

## When to Activate

Activate when producing ANY of:
- Technical recommendations (libraries, frameworks, approaches)
- Factual claims (statistics, specifications, version numbers)
- Code samples that depend on specific APIs or behaviors
- Best practice recommendations
- Comparison between technologies

## Source Authority

Resolve every external claim in this order unless the user explicitly designates another source:

1. **Workspace files** — repo-local docs, specs, schemas, generated types, lockfiles, and project notes.
2. **System-scope files** — headers, includes, shared libraries, interpreter files, and system package files.
3. **Web search results** — only after the user broadly authorizes web search.

Workspace search is default-granted. Web search is default-denied unless the user authorizes it with broad phrasing such as "search online", "look it up on the web", or "check online". Search system-scope files with `find` or `rg`; never assume a package path. On multiple system candidates, stop and ask which one is used, unless the compiler/interpreter/library is explicitly declared in a Makefile, script head, or shebang.

System ambiguity anchors:

- Target
- Kind
- Candidates
- Action
- Request
- Exemption already satisfied

Provenance and version anchors:

- Scope
- Location
- Version
- Retrieved

Record these anchors for any claim that affects output. Mark `Version` as `unverified` when it cannot be established, and do not assert version-dependent behavior. When local/system and web versions conflict, surface the mismatch and ask which version is authoritative.

Authority is selected before quantity. More lower-tier sources do not compensate for a missing higher-authority match.

Subagents inherit the same rule and may run web search only when the parent mandate explicitly authorizes it. Otherwise they rely only on parent-provided information.

## Verification Requirements

### Minimum Standard

| Requirement | Rule |
|-------------|------|
| Source count | Minimum 2 independent sources per perspective |
| Source quality | Official docs, reputable technical blogs, academic papers, source code |
| Cross-reference | Sources must independently confirm the same claim |
| Recency | Prefer sources dated within last 2 years for fast-moving tech (tunable default; tier by claim volatility per the qualitative validity tiers in rag-pattern.md) |
| Attribution | Every claim must have a visitable link attached |

### Source Hierarchy

1. **Primary**: Official documentation, source code, RFCs, standards
2. **Secondary**: Authoritative technical blogs (company engineering blogs, recognized experts), academic papers
3. **Tertiary**: Community documentation, Stack Overflow, GitHub issues

Never use tertiary sources as the sole verification. Always pair with primary or secondary.

## Prohibited Practices

- **Training data reliance**: "Based on my knowledge..." without external verification is prohibited
- **Hallucinated citations**: Never fabricate URLs or source attributions
- **Single-source claims**: One source is insufficient for any perspective
- **Circular references**: Two sources citing each other do not count as independent

## Handling Unverifiable Content

When external verification cannot be obtained:

1. **Drop the content** — Preferred option
2. **Downgrade confidence** — State "unverified; recommend independent confirmation" with clear marking
3. **Use sandbox testing** — If the claim is about code behavior, test it in an isolated environment and report results as empirical evidence

## Handling Conflicting Sources

When two or more verified sources make contradictory claims:

1. **Rank** the conflicting evidence by **source authority**, then **recency**, then **permission level**; more lower-tier sources do not outweigh a missing higher-authority match.
2. **Do not silently blend or pick a favorite** — run an explicit conflict check and, in the output, **disclose the conflict with citations** and state which source you relied on and why.
3. If no source clearly dominates, present the conflict to the user and let them decide or designate an authoritative source.

## Session Output Format

For each externally verified perspective, include:

```markdown
[Claim statement] [^1^](https://source1-url) [^2^](https://source2-url)
```

Links must be visitable. Prefer direct links over shortened URLs.

When answering from retrieved content, quote the relevant source passage before making the claim (quote-grounding, per Anthropic guidance).
