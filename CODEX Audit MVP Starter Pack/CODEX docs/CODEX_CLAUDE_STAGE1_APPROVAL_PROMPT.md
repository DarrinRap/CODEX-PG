# Claude Stage 1 Approval Prompt

Use this only if Darrin approves Claude to begin Stage 1 implementation.

```text
Claude, approved to begin Stage 1 implementation only.

Use your Stage 1 plan and Codex's response at:
C:\CODEX PG\CODEX Claude Share Package\CODEX Prompts\CODEX_CODEX_RESPONSE_TO_CLAUDE_STAGE1_ALIGNMENT.md

Stage 1 scope:
- Add a narrow local-only Audit package builder integration into C:\panda-gallery.
- Create new top-level package C:\panda-gallery\codex_audit\.
- Add one CLI entry point: python panda_gallery.py --build-audit-package.
- Output only to C:\CODEX PG\CODEX Audit Prototype\CODEX Session Packages\.
- Keep package IDs deterministic as pkg_local_<session_id> for Stage 1.
- Keep mock issue extraction, local approval record, draft-only email record, and archive JSONL local-only.

Do not:
- build the final dashboard,
- add Dropbox upload,
- call a real AI provider,
- send email,
- process real PHI,
- rewrite instruction_pane.py, workflow_capture.py, results_writer.py, main_window.py, or panda_gallery.py wholesale,
- touch v4 clinical UI work,
- mutate existing workflow outputs, screenshots, transcripts, or archives.

Expected touched files only:
- C:\panda-gallery\codex_audit\__init__.py
- C:\panda-gallery\codex_audit\package_builder.py
- C:\panda-gallery\codex_audit\validation.py
- C:\panda-gallery\codex_audit\issue_extraction.py
- C:\panda-gallery\codex_audit\review_records.py
- C:\panda-gallery\codex_audit\cli.py
- C:\panda-gallery\panda_gallery.py, one argparse flag/route only
- C:\panda-gallery\tests\codex_audit\test_package_builder.py
- C:\panda-gallery\tests\codex_audit\fixtures\synthetic_workflow\...
- C:\panda-gallery\BUGS.md, one shipped-note entry only if this matches PG convention
- C:\panda-gallery\CLAUDE.md, one-line ownership/output note only if this matches PG convention

Verification required:
1. Record git status before changes.
2. Run tests for the new module.
3. Run python panda_gallery.py --build-audit-package against a safe current workflow output.
4. Confirm validation.ok == true and issue_validation.ok == true.
5. Confirm output path is under C:\CODEX PG\CODEX Audit Prototype\.
6. Confirm C:\panda-gallery\workflows\ is byte-identical before and after.
7. Report every changed file and every command run.
8. Stop and ask before expanding scope.
```
