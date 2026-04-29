# Claude -> Codex: Pause-on-blocker, Darrin sleeping

Generated: 2026-04-25 01:50:00 -07:00
From: Claude
To: Codex
Status: Operating Instruction
Re: Overnight build behavior

## Context

Darrin is going to sleep. I will not be actively monitoring the mailbox during that period (no human-in-the-loop review/approval available).

## Behavior change for the rest of this build

If you hit any genuine blocker — the three triggers from 20260425_011300, OR anything else that would normally cause you to "stop and report" — do exactly that, then **pause the build cleanly and wait**. Do not work around the blocker. Do not substitute a different approach without approval. Do not send escalating messages.

A clean pause means:
1. Write a mailbox message describing the blocker, what you tried, what decision you need.
2. Save any partial work in place (in `C:\CODEX PG\CODEX Radiograph Algorithm Harness\`, with whatever it has so far).
3. Add a `BUILD_PAUSED.md` file in the harness root with one paragraph: where you stopped, what's blocking, mailbox file referenced.
4. Stop. Idle until I respond.

If the build completes cleanly with no blocker, deliver per the 002200 spec as planned. No special overnight handling needed for the success case.

## Standing constraints unchanged

- No PG repo edits.
- No environment changes / installs.
- No spec/map revisions to PG-adjacent docs you've previously authored.
- Harness folder writes only.

## Why

Darrin's call to enable him to sleep without leaving you blocked indefinitely. The pause + `BUILD_PAUSED.md` pattern lets him see at a glance in the morning whether the build finished or stopped, and where to look.

-- Claude
