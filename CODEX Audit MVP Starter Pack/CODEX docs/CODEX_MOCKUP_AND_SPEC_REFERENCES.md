# CODEX Audit MVP Mockup And Spec References

Use these references when Claude begins integration or UI planning.

## Canonical Specs

- `C:\CODEX PG\CODEX Canonical Specs\CODEX_MASTER_SPEC_INDEX.md`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_SESSION_PACKAGE_SCHEMA_v1.md`
- `C:\CODEX PG\CODEX Canonical Specs\CODEX_AUDIT_ISSUE_SCHEMA_v1.md`

## Starter Pack

- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX_AUDIT_MVP_STARTER_PACK_README.md`
- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\audit_mvp_reference_builder.py`
- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX scripts\validate_audit_mvp_contracts.py`
- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\expected_package\session_package_session_20260424_194422\session_package_manifest.json`
- `C:\CODEX PG\CODEX Audit MVP Starter Pack\CODEX samples\sample_audit_issue_extraction_v1.json`

## UX Review And Contact Sheets

- `C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX_CLAUDE_SCREENSHOT_UX_MOCKUP_REVIEW.md`
- `C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX_recent_mockups_contact_sheet.png`
- `C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX_v4_0_mockups_contact_sheet.png`
- `C:\CODEX PG\CODEX Claude UX Mockup Review\CODEX_all_claude_mockups_contact_sheet.png`

## Specific Claude Mockups To Inspect Before UI Work

Testing and audit capture:

- `C:\panda-gallery\workflows\design\instruction_pane_redesign_v1.html`
- `C:\panda-gallery\workflows\design\pane_action_bar_v2_mockup_v1.html`
- `C:\panda-gallery\workflows\design\region_capture_v1.html`
- `C:\panda-gallery\workflows\design\review_dialog_sizing_v1.html`
- `C:\panda-gallery\workflows\design\dialog_sizing_v1.html`
- `C:\panda-gallery\workflows\design\stats_row_mic_bar_mockup_v1.html`

Clinical app direction that should influence later dashboard taste, not this starter pack:

- `C:\panda-gallery\workflows\design\v4_0\v4_0_shell_mockup_v1_library.html`
- `C:\panda-gallery\workflows\design\v4_0\v4_0_arrange_canvas_mockup.html`
- `C:\panda-gallery\workflows\design\v4_0\v4_0_edit_image_mockup.html`
- `C:\panda-gallery\workflows\design\v4_0\v4_0_comparison_mockup.html`
- `C:\panda-gallery\workflows\design\v4_0\v4_0_template_editor_mockup.html`
- `C:\panda-gallery\workflows\design\v4_0\v4_0_right_panel_study.html`

## UI Principle For Later Audit Dashboard

The audit dashboard should borrow the v4 shell's discipline but not become a generic Adobe clone. It should be a compact evidence review and approval workspace:

- issue queue on the left,
- evidence preview center,
- issue detail and approval/email draft right,
- package/session context always visible,
- clear status lifecycle,
- no live email send until approval state is explicit,
- no real PHI until compliance rules are settled.
