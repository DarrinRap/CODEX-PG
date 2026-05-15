---
schema_version: 1
message_id: 20260508_CLAUDE_to_CODEX_image_mount_architecture_spec
in_reply_to: null
thread_id: PG-ARCH-IMAGE-MOUNT-20260508
from: CLAUDE
to: CODEX
date: 2026-05-08T19:20:00-07:00
subject: SPEC REQUEST -- PG image vs mount architecture: define data model + implementation rules
type: directive
priority: high
thread_status: open
requires_darrin_decision: false
suggested_tier: Extra-High
---

# PG Image vs Mount Architecture — Spec Request

## Context

During UX Q&A (session 145, Q89), Darrin raised a foundational question:
how does PG distinguish between a single image and a mounted/templated
collection of images? This is an architectural decision that affects the
Library module, Arrange module, Develop module, search, export, and the
entire data model. It must be locked before CC implements any Library or
Arrange UI.

## The core question

Is an **image** the atomic unit, or is a **mount** (arrangement)?

## CD's recommended architecture: Option A — Images first

Every import creates individual image records. Arrangements
(mounts, templates, FMX series) are named collections of image
**references** — pointers to individual image records, not copies.
The same image can appear in multiple arrangements. Library shows
images; Arrange shows arrangements built from those images.

This mirrors how DICOM and clinical imaging systems work. It is also
consistent with the existing PG non-destructive pipeline (originals/
folder, JSON parameters, no pixel mutation).

## What Codex needs to spec

Please author a comprehensive implementation spec covering:

### 1. Data model

- `ImageRecord` schema: what fields? (UUID, original_path, import_date,
  patient_id, image_type, edit_parameters, keywords, notes, tooth_number,
  invert_state, snapshots, history, overlay_path, created_at, updated_at)
- `Arrangement` schema: what fields? (UUID, patient_id, name, template_type,
  slots, created_at, updated_at)
- `Slot` schema: what fields? (slot_id, position, size, image_ref or None,
  constraints_active, position_locked, size_locked, rotation_locked)
- Relationship: how does a Slot reference an ImageRecord? (by UUID)
- Can one ImageRecord appear in multiple Arrangements? (CD proposes: yes)
- What happens to Arrangements when an ImageRecord is archived?
  (CD proposes: slot becomes empty/broken-link, arrangement preserved)

### 2. Library navigation rules

- What does Library show by default — all images, or sessions/visits?
- How are images grouped (by date, by arrangement, by type)?
- Where do "loose" images live (images not in any arrangement)?
- How does the user navigate from a Library image into Arrange?
- How does the user navigate from an Arrangement back to its constituent
  images in Library?
- What is the Library search scope — images only, arrangements only, both?

### 3. Arrange interaction rules

- When a user opens Arrange with a template, do they see empty slots or
  pre-filled slots?
- When they drag an image from Library/filmstrip into a slot, what
  exactly is stored — a copy, a reference, a path?
- If the source image is later archived, what happens to the slot?
- Can the same image fill multiple slots in the same arrangement?
- Can the same image appear in two different arrangements simultaneously?
- When a user edits an image in Develop that is referenced in an
  Arrangement, does the Arrangement automatically reflect the updated
  edit parameters, or does it snapshot at placement time?

### 4. Import rules

- When images are imported, are they always "loose" until explicitly
  assigned to an arrangement?
- Or does PG prompt the user to assign to an existing or new arrangement?
- Can a batch import pre-populate an arrangement? (e.g., import 18 images
  → automatically populate FMX template by image type)

### 5. Export rules

- When exporting from Arrange, what is exported — the arrangement as a
  composite, or the individual images?
- When exporting a single image from Develop, is the arrangement context
  included in the export metadata?

### 6. Edge cases to address

- An image in an arrangement is archived: slot shows broken-link state
- An image appears in 2 arrangements, user edits it: both arrangements
  update (because they reference, not copy)
- An arrangement has 18 slots, only 12 filled: export behavior?
- A "loose" image has never been in any arrangement: Library shows it
  where?

## Deliverable

A spec document at:
`C:\CODEX PG\CODEX Canonical Specs\PG_IMAGE_MOUNT_ARCHITECTURE_SPEC_v1.md`

Format: numbered sections matching 1-6 above. Decision table for each
edge case. Clear statement of what IS and IS NOT in scope for v4.0 vs
v4.1. Implementation notes for CC (what existing PG code is affected,
what new modules are needed).

CD will review the spec before it is sent to CC. Do not route to CC
directly.

## Suggested tier

Extra-High — this is a multi-section architectural spec with data model
definitions, decision tables, and cross-module interaction rules.
Expected output: 400-600 lines.

— CD
