# Edit-Time CAS Gate (Write Safety & Edit Consistency)

Single-file owner of write-time consistency semantics: CAS (Compare-And-Swap) hash checks, Edit/Write tool preference, and data-race handling.
Keep this file as one unit for now; the numbered sections are the intended split points if restructuring is needed later.

## 1. Hash Register

- Record `sha256(<absolute path>)` after every successful write that changes an existing file, keyed by the normalized absolute path. Apply to edit-tool writes and script/command mutations alike.
- Prefer the session state file (e.g. `.agent/state/cas-register.md`); it survives compaction. In-session memory is acceptable only as a fallback and must be treated as fragile.
- New files: no baseline until the first write completes; record the hash immediately after that write. The first re-edit of the file then enters the gate.
- Reuse the `Before-state`/`After-state` fields of the Protection Status Registry (pre-edit-safety.md) as the audit trail; the CAS register is the active pre-write baseline.

## 2. Pre-Work Detection

Before opening a new edit group on a file that has a recorded hash:

1. Re-hash the file on disk and compare with the register.
2. On match, proceed. On mismatch, unreadable file, or missing file, the content changed outside this agent's view: do NOT edit from memory.
3. Re-read before editing:
   - Whole file when below 100 KB (default; honor user override).
   - Larger files: read the targeted edit section plus anchor context.
   - Escalate to a whole-file re-read for core/architecture code, global edits, or small projects where whole-file reads are cheap. Scale conservativeness with importance: prefer fuller re-reads for core sections over utilities/helpers.
4. The re-read becomes the new edit baseline; record its hash after the next successful write.

## 3. In-Work Detection

- Do NOT re-hash before every individual edit call. Treat one logical edit operation (baseline read -> apply edits) as an atomic group; the hash check runs at group boundaries (per-round), not per call.
- Per-edit protection is delegated to the edit tool's own atomicity and failure semantics where available (tool-level backstop).
- If the edit tool FAILS for a non-system reason — content/match failure, "file has changed", hunk/old_string mismatch, ambiguous match — treat it as a suspected data race: overhaul-read before the next write, then re-express the edit from fresh content. Permission, sandbox, network, and disk errors are not race signals; apply the standard retry path for those.

## 4. Post-Edit Self-Check

- Prefer the edit tool's own return value/stdout when it confirms that the change applied; treat that as the self-check.
- If the tool does not confirm success, verify with a targeted grep/read of the new marker before proceeding. Never claim success on an unverified edit.

## 5. Edit vs Write Tool Preference

Choose deliberately per file, never by habit:

| Situation | Preferred tool |
|---|---|
| Existing file, scoped change (< ~50% of content) | Edit (anchored, minimal diff) |
| Existing file, wholesale rewrite (> ~50% or entirely different content) | Write, only after a full re-read |
| New file | Write; first re-edit then enters the CAS gate |
| Auto-generated output (lockfiles, manifests, formatter/linter results) | script/Write; record hash afterwards |

Degradation ladder (when the preferred tool fails for a non-system reason):

1. Verify anchors/old_string against a fresh targeted read; split the change; retry, bounded (at most 3 attempts).
2. On persistent mismatch, widen the anchor context, or use `replace_all` only when uniqueness is verified.
3. Only after a full re-read may Edit degrade to Write — never write from memory.

## 6. Scoped Edits over Global Substitution

- Prefer scoped, line/region-anchored edits over global substitution.
- Global substitution is allowed only after a full-file re-read, when pattern uniqueness is verified (e.g. exact-match count), or for authorized mechanical refactors and auto-generated content.

## 7. Data-Race Handling

### Red flags

- Pre-work: hash/mtime/size mismatch; file deleted or unreadable; unexpected `git status` modifications.
- In-work: edit-tool failure for a non-system reason; tool result contradicting expectation; `STALE` report from a chunk/subagent; lock conflict.
- Post-edit: self-check/verification shows the change did not land.

### Response ladder

1. Stop the edit group. Never silently overwrite; never write from memory.
2. Classify the conflict: external writer (user/IDE/process), self-conflict, or subagent conflict.
3. Re-read (whole file for KB-scale files; targeted section otherwise), re-express the edit from fresh content, and retry (bounded, at most 3 attempts).
4. On persistent conflict or an identifiable external writer, report, preserve state, and escalate via interactive clarification. NEVER auto-merge.

## 8. Beyond Re-Hashing

- Prefer diff-aware/three-way apply where the harness supports it; hash plus re-read remains the portable baseline.
- Multi-agent concurrency: prefer advisory locks or disjoint file ownership (prevention) over detection.
- CRDT/OT merge infrastructure supersedes file-level CAS where available; record as future work, not a skill-level requirement.
- The hash-check-then-edit sequence has a narrow TOCTOU window; it is a guardrail, not a lock. Definitive backstops: the edit tool's own failure semantics (in-work detection), the Protection Status Registry, and git.

## 9. Integration

- SKILL.md: entry bullet under the Universal Pre-Edit Safety Gate.
- context-drift-governance.md: Phase G re-hash rule; chunked execution is the special case of this gate applied per chunk.
- subagent-orchestration.md: Pattern F staleness guard is the chunked/Mode B form of this gate.
- pre-edit-safety.md: registry Before/After fields are the audit trail for this gate's active baseline.
