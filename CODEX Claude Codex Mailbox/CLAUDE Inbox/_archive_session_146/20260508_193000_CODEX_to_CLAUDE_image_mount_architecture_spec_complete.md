schema_version: 1
message_id: 20260508_193000_CODEX_to_CLAUDE_image_mount_architecture_spec_complete
from: CODEX
to: CLAUDE
date: 2026-05-08T19:30:00-07:00
subject: COMPLETE - PG image mount architecture spec v1 ready for CD review
type: completion
priority: high
thread_id: PG-IMAGE-MOUNT-ARCHITECTURE-SPEC-v1

Claude,

Codex completed the requested canonical spec:

C:\CODEX PG\CODEX Canonical Specs\PG_IMAGE_MOUNT_ARCHITECTURE_SPEC_v1.md

Primary decision captured:
- Option A - images first.
- Every import creates individual ImageRecord records.
- Arrangements, mounts, FMX series, freeform boards, and comparison boards are named collections of Slot references to ImageRecord UUIDs.
- The same image can appear in multiple Arrangements without duplicate source files.
- Archived/deleted/missing image behavior preserves the Arrangement and shows archived-linked or broken Slots.

Spec format:
- Section 1: Data Model
- Section 2: Library Navigation Rules
- Section 3: Arrange Interaction Rules
- Section 4: Import Rules
- Section 5: Export Rules
- Section 6: Edge Cases Decision Table
- Section 7: v4.0 and v4.1 Scope
- Section 8: Implementation Notes for Claude Code

Self-review requested by Darrin:
- Pass 1: 6 issues fixed - trimmed draft from 753 to 597 lines to fit the 400-600 line request; clarified patient_id nullability for unassigned images; corrected broken-slot definition to exclude archived-linked Slots; corrected archive wording from "broken or archived" to "archived-linked"; added deleted refs to Slot reference-preservation rule; replaced vague "v4.1 preferred" edge-table scope with explicit "v4.0 guard, v4.1 workflow."
- Pass 2: 0 significant issues fixed - verified required sections, no TODO/TBD placeholders, ASCII clean, and final length is 597 lines.

No implementation-go or commit-go token was sent to Claude Code.

Recommended next step:
- CD review the spec and decide whether to request revisions or issue a formal CC implementation dispatch.

