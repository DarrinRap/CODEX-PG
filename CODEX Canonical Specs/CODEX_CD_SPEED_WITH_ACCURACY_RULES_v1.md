# CODEX CD Speed With Accuracy Rules v1

Status: READY
Owner: Codex
Audience: Claude Desktop (CD), Codex, Claude Code (CC) coordination lanes
Created: 2026-05-10
Scope: Process, mail, context, and evidence strategy only. This spec does not authorize code changes, PAH starts, CC dispatch, commits, or edits to `C:\panda-gallery`.

## 1. Purpose

CD is slowing down because it is being asked to carry too much context, inspect too many stale files, and re-derive status from large mailbox and repository surfaces. The goal is to make CD faster without lowering correctness, traceability, or coordination discipline.

Speed must come from smaller inputs, better indexes, terminal-state cleanup, and explicit evidence levels. It must not come from guessing, skipping required proof, ignoring fresh mail, or hiding uncertainty.

## 2. Non-Negotiable Accuracy Rules

1. Evidence beats memory. If a fact affects an instruction, dispatch, commit-go, or user-facing status, cite the current file, thread, commit, API result, or command output used.
2. Recency must be explicit. For active campaigns, distinguish current evidence from archived evidence and name the newest message or commit checked.
3. No inferred authorization. Mail, ACKs, summaries, or stale approvals do not authorize code, commits, PAH starts, CC dispatch, or `C:\panda-gallery` writes unless the current directive explicitly grants that action.
4. Uncertainty must be labeled. Use `confirmed`, `inferred`, `not checked this pass`, or `held` rather than burying uncertainty in prose.
5. Speed shortcuts require a fallback. Any bounded scan or cached digest must state the condition that triggers deeper inspection.

## 3. Default Fast Startup Routine For CD

CD should start from a narrow current-state packet, not from mailbox archaeology.

Required startup sequence:

1. Read the current handoff or active-thread digest.
2. Read only direct inbox files newer than the last processed checkpoint.
3. Read active open thread files named by the digest.
4. Check only the git branch and latest commit for repositories involved in the active thread.
5. Defer archive, full-repo, and broad-mailbox scans unless a direct signal requires them.

Startup output should be a four-line status:

```text
Active thread:
Newest mail checked:
Current blocker or next action:
Evidence level:
```

## 4. Active Thread Digest Rule

Maintain a small active-thread digest so CD does not reread every mailbox root.

Digest requirements:

- File name should be stable, for example `CURRENT_ACTIVE_THREADS.md` or the existing project handoff equivalent.
- Include only active, held, blocked, and waiting-on-user threads.
- For each thread, include `thread_id`, owner, current status, next action, newest relevant mail path, and last evidence timestamp.
- Remove or archive shipped, superseded, closed, and acknowledged-only threads from the active digest within the next cleanup pass.
- Link to long reports instead of embedding them.

A digest entry should fit this shape:

```text
thread_id:
owner:
status:
next_action:
newest_evidence:
hold_reason:
```

## 5. Mailbox Speed Rules

1. Root inboxes are for active work only. Terminal messages belong in archive folders once ACKed, shipped, superseded, or explicitly held.
2. Prefer thread-level reads over folder-level reads. Read the newest file for a thread first, then follow `in_reply_to` only if the newest file is ambiguous.
3. Do not reread long historical mail bodies by default. Use subject, frontmatter, and digest first; open the body only when it changes the next action.
4. Keep status mail short. Put long diagnostics in linked reports or specs.
5. One consolidated nudge per agent per check cycle. Do not send repeated pings for the same stale item unless a deadline or user blocker changed.
6. When a root inbox count differs from thread count, treat it as a reporting issue, not proof of unread work, until checked against thread state.

## 6. Context Budget Rules

CD should work within explicit context budgets during active campaigns.

Default budgets:

- Direct inbox scan: newest 20 files unless an active-thread digest points elsewhere.
- Thread body reads: newest message plus at most two ancestors before summarizing and asking for the missing link.
- Repo inspection: exact named files first; `rg` targeted searches second; broad recursive scans last.
- Logs: newest relevant log first; avoid loading full logs unless the failure line is not enough.
- Screenshots: inspect the exact screenshot tied to the active report; do not review screenshot folders broadly unless asked.

Escalate beyond these budgets when:

- the newest message references missing evidence,
- a contradiction appears between digest, mailbox, and git state,
- safety, data loss, or authorization is unclear,
- a test failure cannot be explained from the narrow evidence,
- Darrin explicitly asks for a full audit.

## 7. Repository Inspection Strategy

1. Use `git status --short --branch` and `git log --oneline -5` before interpreting repo state.
2. Use `rg` or exact path reads before recursive file enumeration.
3. Read diffs by path, not whole-repo diffs, unless the task is specifically a repo-wide review.
4. Never clean, revert, stage, or commit unrelated dirty work to make status simpler.
5. For active CC work in `C:\panda-gallery`, Codex and CD should treat the repo as CC-owned unless explicitly assigned otherwise.

## 8. Dispatch And Spec Strategy

1. Dispatches should be small and executable. Put background context behind links.
2. Every dispatch must say whether it is `diagnose-only`, `spec-only`, `commit-go`, `implementation-go`, `hold`, or `report-only`.
3. Every commit-go should list exact files in scope and exact files out of scope.
4. Every spec should include acceptance criteria and a verification gate. Do not make CD infer what done means.
5. For multi-cluster campaigns, use one thread per cluster or one digest row per cluster. Avoid mixing unrelated clusters in a single long mail unless it is a summary.

## 9. Accuracy-Preserving Summary Format

Use compact status blocks that preserve proof and uncertainty.

Recommended format:

```text
Status: confirmed / inferred / held / blocked
Evidence: path or commit or command
Next action: one sentence
Do not do: one sentence if there is a known hazard
```

Avoid long narrative status unless the user explicitly asks for a postmortem.

## 10. Tooling Rules For Speed

1. Parallelize independent reads when possible.
2. Prefer metadata lists before full file reads.
3. Prefer structured frontmatter parsing over free-text scanning for mail triage.
4. Prefer current API endpoints or exact log files over UI observation when the question is state, not layout.
5. Do not start GUI apps, PAH, tray, watchers, or servers just to answer a status question. Passive checks first.
6. If a live check would change state, say so and require explicit authorization.

## 11. Token Economy Without Accuracy Loss

Token economy means reducing repeated, irrelevant, or over-broad context. It does not mean omitting evidence needed for a correct decision.

1. Start with a compact state packet. Prefer one digest row, one newest mail, one commit, and one next-action sentence before opening history.
2. Quote paths and IDs, not full bodies. Link or name long specs, logs, screenshots, and mail files instead of pasting their contents unless the exact wording matters.
3. Summarize stable history once. Do not restate old background in every message; refer to the active digest or handoff.
4. Use delta summaries. When updating CD, say what changed since the last checkpoint rather than re-describing the entire campaign.
5. Read in layers. First read metadata/frontmatter, then newest body, then linked evidence, then archives only if the narrow read is insufficient.
6. Prefer structured tables only when they reduce prose. Avoid giant tables that repeat obvious fields.
7. Keep ACKs tiny. A good ACK should include receipt, understood boundary, next action or hold reason, and no extra narrative.
8. Keep diagnostics separate from coordination. Mail should point to the diagnostic file and include only the conclusion, confidence, and next gate.
9. Avoid duplicate evidence. Cite one authoritative source per fact unless sources conflict or the decision is high risk.
10. Use evidence labels instead of long caveats. `confirmed`, `inferred`, `held`, `blocked`, and `not checked this pass` are cheaper and clearer than paragraph-length hedging.
11. Ask narrow questions. If blocked, ask the smallest question that unblocks the next step; do not bundle speculative future questions.
12. Cache only with invalidation. A cached digest is acceptable only if it records newest checked mail/commit and the condition that invalidates it.
13. Do not compress away hazards. Authorization limits, dirty worktree warnings, process-start risks, and data-loss risks must remain explicit even in short messages.
14. Use appendices for bulk evidence. Keep main status short; put large command output, long stack traces, and full audit findings in linked reports.
15. Prefer one high-signal final answer over repeated micro-updates when the task is quick. For longer work, send brief progress updates but avoid narrating every file read.

A token-economical status should fit this shape:

```text
Changed: one sentence
Evidence: one path / commit / command
Next: one sentence
Boundary: one sentence, only if relevant
```

Escalate to a fuller explanation when:

- evidence conflicts,
- user trust was recently damaged by a related mistake,
- the action is irreversible or authorization-sensitive,
- a bug diagnosis depends on subtle reasoning,
- the user asks for the reasoning.

## 12. Archive And Holding Queue Policy

Held work should be visible but lightweight.

- Use a holding queue for real but deferred work.
- Include why it is held, who can unblock it, and what evidence should be read when resumed.
- Do not keep held items in the root inbox forever if the active digest points to the holding queue.
- Do not archive items that are merely read. Archive only terminal or explicitly held/superseded items according to the PAH archive-policy rule.

## 13. Anti-Patterns That Slow CD Down

Avoid:

- Asking CD to reread all inboxes after every tiny update.
- Putting full specs or full diagnostics inside mailbox bodies when a linked file will do.
- Mixing ACKs, implementation decisions, and unrelated findings in one mail.
- Treating stale unread counts as work without checking active thread state.
- Running broad recursive scans when exact file paths are known.
- Reopening closed history because a root inbox still contains old files.
- Starting PAH or GUI processes to answer a question that a passive status check can answer.

## 14. Minimum Viable Accuracy Gate

Before CD answers or routes work, it must know:

1. What is the newest relevant evidence?
2. Who owns the next action?
3. Is this action authorized now?
4. What is held, blocked, or out of scope?
5. What would trigger a deeper scan?

If any answer is missing, CD should state the gap instead of expanding into a broad scan by reflex.

## 15. Speed Metrics To Track

Track these lightly, not as bureaucracy:

- Time from new direct mail to ACK or disposition.
- Number of root inbox files left active after cleanup.
- Number of times CD had to open archives for a current answer.
- Number of status replies that cite a current evidence path.
- Number of repeated pings for the same stale item.
- Number of preventable broad scans avoided by active-thread digest.

## 16. Recommended Immediate Adoption For Current PG Work

For the current Vellum and PAH state:

1. Keep PAH held unless Darrin explicitly reopens it.
2. Use the Vellum campaign messages as the active thread source of truth.
3. Keep Codex direct mail responses limited to ACK, hold, or audit/report unless CD requests a spec or Darrin authorizes code.
4. Add PAH deferred items to the holding queue, not repeated mailbox reminders.
5. When Vellum closes, create one fresh PAH active-thread digest before restarting PAH work.

## 17. Self-Review Record

Pass 1: 5 issues fixed - added explicit authorization boundary; added fallback conditions for bounded scans; added passive-check rule for PAH/processes; clarified root inbox count mismatch is not proof of work; added minimum viable accuracy gate.
Pass 2: 3 issues fixed - separated digest rules from mailbox rules; added exact compact status format; added active-campaign budgets with escalation criteria.
Pass 3: 2 issues fixed - clarified held-item archive policy so read-only items are not incorrectly archived; added current PG adoption section to avoid ambiguity about PAH vs Vellum priority.
Pass 4: 0 significant issues fixed - no remaining blocking errors, omissions, inconsistencies, or ambiguities found.
Pass 5: 4 issues fixed - added token-economy section; added explicit no-accuracy-loss boundary; added invalidation rule for cached digests; added escalation criteria for fuller reasoning.
Pass 6: 1 issue fixed - added missing blank line before the Archive section heading so the new token-economy section renders cleanly.
Pass 7: 0 significant issues fixed - amendment does not weaken evidence, authorization, or hazard-reporting requirements.


