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

## Verification Requirements

### Minimum Standard

| Requirement | Rule |
|-------------|------|
| Source count | Minimum 2 independent sources per perspective |
| Source quality | Official docs, reputable technical blogs, academic papers, source code |
| Cross-reference | Sources must independently confirm the same claim |
| Recency | Prefer sources dated within last 2 years for fast-moving tech |
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

## Session Output Format

For each externally verified perspective, include:

```markdown
[Claim statement] [^1^](https://source1-url) [^2^](https://source2-url)
```

Links must be visitable. Prefer direct links over shortened URLs.

When answering from retrieved content, quote the relevant source passage before making the claim (quote-grounding, per Anthropic guidance).
