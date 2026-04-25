# CODEX Claude Handoff Prompt: Panda Gallery Testing + Audit

Copy this prompt to Claude / Claude Code when Claude is ready.

```text
Claude, please review the Codex handoff package for Panda Gallery Testing + Audit.

Shared package path:
C:\CODEX PG\CODEX Claude Share Package

If you do not have local file access, ask Darrin for:
C:\CODEX PG\CODEX Claude Share Package.zip

Start by reading:
1. C:\CODEX PG\CODEX Claude Share Package\CODEX_READ_ME_FIRST.md
2. Then follow the read order inside that file exactly.

Critical boundaries:
- Do not edit C:\panda-gallery yet.
- Do not claim Panda Gallery v4 is complete.
- Do not add Dropbox upload.
- Do not call a real AI provider.
- Do not send email.
- Do not process real PHI.
- Do not build the final dashboard yet unless Darrin explicitly approves that stage.
- Do not rewrite large existing PG modules wholesale.
- Preserve current PG outputs; do not mutate results_latest.json, screenshots, transcripts, or archived session data.

Design/quality gate:
- Match the redesign direction you already developed for Panda Gallery v4 and that Codex reviewed.
- Treat the reviewed mockups and CODEX_CLAUDE_SCREENSHOT_UX_MOCKUP_REVIEW.md as the visual target.
- Notify Darrin before implementing if anything conflicts with the redesign, MVP scope, evidence integrity, privacy/compliance, testability, maintainability, or code quality.
- Push back clearly on rushed, risky, over-broad, or under-specified implementation choices.
- Excellence takes time. Do not trade audit integrity or maintainability for speed.

Current Codex status:
- Canonical Testing + Audit specs are complete for package schema, issue schema, architecture, dashboard UX, and compliance guardrails.
- A local-only Python scaffold exists in the share package at:
  C:\CODEX PG\CODEX Claude Share Package\CODEX Desktop App Scaffold
- The live working scaffold is at:
  C:\CODEX PG\CODEX Desktop App
- The scaffold can package current read-only PG workflow output from C:\panda-gallery\workflows.
- The scaffold supports local mock issue extraction, approval records, draft-only email records, archive JSONL, validation, and archive search helpers.
- Codex test result: 8 tests passed.
- Codex live smoke result against C:\panda-gallery\workflows: package validation ok:true, issue validation ok:true, local review records generated.

Recommended development stages:
1. Local Package Builder hardening.
2. Local Review Records and archive helpers.
3. Read-only Audit Dashboard prototype.
4. Reviewer workflow editing and event history.
5. Dropbox mock queue, then real Dropbox only after compliance/account decisions.
6. AI mock pipeline, then real AI only after provider/privacy decisions.
7. Live email and production archive hardening only after approval/compliance rules are settled.

Your first task is review/planning only:
1. Read the handoff package.
2. Summarize what you understand.
3. Identify any missing files, contradictory requirements, or risks.
4. Confirm whether the Codex scaffold is enough to proceed with the next stage.
5. Recommend the safest next implementation stage and explain why.
6. Propose a small implementation plan, but do not edit files until Darrin approves.

If Darrin approves implementation later, the safest first implementation target is one of these, depending on his preference:
- integrate the local package builder scaffold into C:\panda-gallery as a narrow command/module, or
- build a minimal read-only audit dashboard prototype over the local records.

Either way, keep Dropbox, real AI, live email, PHI, and broad v4 clinical UI work out of the first implementation pass.

At the end of your response, report:
- files/docs you read,
- what is ready,
- what is not ready,
- concerns/pushback,
- recommended stage,
- exact files you would touch only if implementation is approved.
```
