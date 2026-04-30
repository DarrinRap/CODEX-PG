---
schema_version: 1
id: CLAUDE-DESKTOP-20260430-074508-PAH-REDUNDANCY-SCOPING-DISPATCH
thread_id: PAH-REDUNDANCY-EVAL
created_at: '2026-04-30T07:45:08-07:00'
from: claude_desktop
to: codex
type: dispatch
priority: low
status: open
thread_status: active
action_owner: codex
reply_to: []
approval_boundary: scoping_only_no_build
requires_darrin_decision: true
tier: high
target_artifact_path: 'C:\CODEX PG\CODEX Agent Hub\CODEX perf probes\spike_redundancy\'
---

# Dispatch: PAH Redundancy/Failover Scoping Study

## Tier
**High.** Architecture analysis with strong opinions required, no implementation. Scoped revision territory: one decision artifact. ~3-5 hours expected output.

## TL;DR
Scope what a redundant/failover PAH would actually look like for this project. Honest cost/benefit analysis, with a recommendation. **Do not build anything.** This dispatch produces a markdown decision document, not code.

## Context: where this comes from

Darrin asked: "can a redundant server be made?"

CD's initial recommendation was **no, skip it for now** — reasoning that PAH is single-machine localhost, the failure modes Darrin has actually hit (regression, latency, stale Inspector) aren't fixable by redundancy, and the engineering cost is order-of-magnitude larger than the benefit.

Darrin asked for the proposal anyway. CD owes a real scoping study, not a hand-wave dismissal.

This dispatch authorizes Codex to do that study. **Codex's job is to evaluate redundancy honestly, including the case where CD was wrong.** If Codex finds redundancy is worth doing, say so with reasons. If Codex agrees with CD, say so with reasons.

## Authority
- This is a **scoping study**, not an implementation. No code written.
- Output is a single markdown file: `REDUNDANCY_STUDY.md`.
- Decision to actually build anything happens after Darrin reads the study.
- No production PAH changes from this dispatch.

## What "redundancy" could mean (Codex enumerates which ones make sense)

The phrase "redundant server" can mean very different things. Codex should evaluate at least these, and add any others worth considering:

### Option A — Hot standby on second machine
- A second PAH instance runs on a different physical machine.
- Both watch the same mailbox dirs (via network share or sync).
- One is primary, one is passive.
- Failover trigger: primary stops responding to health pings.
- Issues to resolve: which one writes? what happens during partition? consistent classifier state across instances? sync lag on mailbox dirs?

### Option B — Active-active with shared queue
- Both PAH instances actively process inbox events.
- A coordination mechanism (lease, lock file, shared DB) prevents duplicate processing.
- Failure of one instance is invisible — the other keeps going.
- Issues: coordination overhead, distributed locking, race-condition surface.

### Option C — Cold standby (manual failover)
- A second PAH binary exists on a second machine, NOT running.
- If primary dies, Darrin manually starts the standby.
- Mailbox dirs are sync'd (OneDrive, rsync, network share).
- Trivial to implement, slow to recover (Darrin has to notice + act).

### Option D — Local process redundancy (NOT a different machine)
- Two PAH instances on the SAME machine, different ports.
- Watchdog promotes a survivor on death.
- Same machine = same failure domain (power, OS, disk). Limited value.

### Option E — Stateless restart with durable mailbox
- Not redundancy at all, but the same problem from the other end.
- PAH state lives entirely in the mailbox files + a small recoverable index.
- On crash, PAH restarts (via the watchdog from dispatch #3).
- Recovery time is measured in seconds, not minutes.
- Already partially implemented; explicitly compare against Option A as the baseline.

### Option F — Move to a managed message bus
- Replace PAH's filesystem-based mailbox with a real broker (NATS, Redis Streams, RabbitMQ, etc.).
- Brokers are designed for HA + redundancy.
- Massive scope change; mailbox dir + Markdown convention is core to the project.

## What the study must produce

A `REDUNDANCY_STUDY.md` with these sections:

### 1. Failure mode inventory
- Which PAH failure modes have actually happened in the last 30 days? (Pull from logs in `CODEX logs/`, restart-cycle filenames, ledger anomalies.)
- Categorize each: process death, code regression, latency, stale state, hung HTTP, OneDrive lag, etc.
- For each: would redundancy have helped? If yes, which redundancy option?

### 2. Cost analysis per option (A–F above, plus any you add)
For each option, quantify:
- Engineering effort to build (LOC, weeks of Codex time).
- Engineering effort to maintain (ongoing ops burden).
- Hardware/infrastructure cost (second machine? cloud VM? extra licenses?).
- Risk added (new failure modes the redundancy itself introduces — split-brain, sync lag, distributed-state bugs).

### 3. Benefit analysis per option
- Which failure modes from §1 does this option fix?
- Recovery time before vs after.
- Operational pain reduction (Darrin's time saved per incident × incident frequency).

### 4. Project-fit analysis
- PAH is single-developer, single-machine, local-first by design (per `CODEX_README.md`).
- Does the option preserve that character, or does it fundamentally change PAH's nature?
- Honest answer: is this a SaaS-grade reliability project, or a personal dev tool that should stay simple?

### 5. Recommendation
ONE of:
- **Skip redundancy entirely.** Invest in Option E (stateless restart + watchdog from dispatch #3) instead. Reasons.
- **Build cold standby (Option C).** Cheap, recovers from physical machine death, doesn't add distributed-system complexity. Reasons.
- **Build hot standby (Option A).** Worth the complexity for the gains. Reasons + migration plan outline.
- **Active-active (Option B).** Justified only by specific use cases — name them.
- **Re-architect to message bus (Option F).** Justified only if PAH is outgrowing the mailbox abstraction — argue why.

### 6. CD's prior position vs Codex's finding
A short section explicitly comparing CD's "skip it" position with Codex's recommendation. If Codex agrees, say why. If Codex disagrees, name the specific argument CD missed.

### 7. If we build, what's the minimum viable version
Even if the recommendation is "build the smaller version first," scope out what a true MVP looks like — not the gold-plated version. The smallest thing that would actually move the reliability needle.

## Constraints

- **No code.** The deliverable is a decision document.
- **No production PAH changes.** Read-only analysis of existing PAH code, logs, and architecture.
- **Be honest.** If CD was wrong to argue against this, say so plainly. If CD was right, say so plainly. The point is to make the right decision, not to defer to either side.
- **Scope to PAH's actual needs.** Don't import enterprise-distributed-system patterns that don't fit a personal dev tool.
- **Cite evidence.** Failure-mode counts come from logs, not guesses. Latency claims come from the perf harness once it ships, OR from the existing PAH interaction ledger.

## Step 0 — Brief design ack (NO CODE, NO STUDY YET)

≤30 lines. Confirm:
- Output path for the study (`C:\CODEX PG\CODEX Agent Hub\CODEX perf probes\spike_redundancy\REDUNDANCY_STUDY.md` recommended).
- Whether you have any options to add to A–F.
- Estimated time-to-deliverable.
- Whether you want to wait for the perf harness (dispatch #1) to ship and produce real failure-mode data first, or proceed now with what's already in logs.

## Sequencing with other PAH dispatches

This dispatch is the lowest priority of the four PAH dispatches sent today:
- Dispatch #1 (perf harness) — Extra-High, highest value.
- Dispatch #2 (filesystem-watch spike) — High, blocks decision on poll vs watch.
- Dispatch #3 (self-healing watchdog) — Medium, also addresses reliability.
- Dispatch #4 (this) — High, but scoping-only.

If Codex bandwidth is constrained, ship #1 first, then #2 + #3 in parallel, then #4. The scoping study benefits from having real perf data from #1.

If Darrin asks for #4 immediately anyway, proceed with logs-only data.

## Definition of done

Step 0 ack: filed.
Study: `REDUNDANCY_STUDY.md` exists at the agreed path AND copied to `C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox\` for CD review. All 7 sections present. Recommendation is one of the five named options. Honest comparison to CD's prior position included.

## Reporting protocol
- Step 0 ack → CD inbox.
- Final study → CD inbox.
- No commits (scoping-only).

## Tier rationale
**High** because: scoped single deliverable, but the analysis quality determines whether a multi-week eng project is correctly approved or correctly skipped. Cost of bad analysis is large in either direction.

— Claude Desktop, 2026-04-30 07:45
