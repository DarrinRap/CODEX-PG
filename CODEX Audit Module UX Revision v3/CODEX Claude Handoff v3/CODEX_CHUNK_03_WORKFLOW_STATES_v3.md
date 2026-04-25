# CODEX Chunk 03 - Workflow States v3

Core flow:

`dropbox_waiting -> package_detected -> completeness_check -> analysis_running -> findings_ready -> finding_review -> response_draft -> response_approved -> code_task_ready -> fix_waiting -> verification_review -> archived`

Human gates are required before sending/exporting a sender response, handing a task to Claude Code, closing a finding as verified, or archiving a package as final.
