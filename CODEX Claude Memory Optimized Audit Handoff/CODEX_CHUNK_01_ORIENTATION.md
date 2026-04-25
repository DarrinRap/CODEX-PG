# CODEX Chunk 01 - Orientation

## Goal

The Audit MVP turns Panda Gallery testing sessions into structured, reproducible evidence packages for implementation work.

It answers:

- What happened?
- What was expected?
- Where did it fail?
- What evidence proves it?
- What should Claude Code fix?

## Core Workflow

Testing Audit Panel -> Workflow Capture -> Region capture Review -> FAIL Detail Panel -> Session Package -> Claude Handoff

## First MVP Scope

Build a local-only vertical slice:

1. Load a completed or active PG testing session.
2. Capture or import full screenshot evidence.
3. Capture or import manual region evidence.
4. Let tester mark PASS, FAIL, or SKIP.
5. Require observed and expected behavior for FAIL.
6. Build a deterministic local session package.
7. Validate evidence links and package schema.
8. Generate a Claude-ready handoff prompt.

## Hard Boundaries

- Do not upload files.
- Do not call AI APIs.
- Do not send email.
- Do not process real PHI without a compliance decision.
- Do not broadly rewrite PG UI.
- Do not delete evidence files during ordinary discard; mark `discarded: true`.
- Do not mutate source testing artifacts during packaging; copy into package folder.

## Best First Implementation Slice

Add a read-only Audit Panel that scans a selected session and can build/validate a local package from existing test output. Then add interaction states around capture and FAIL detail.
