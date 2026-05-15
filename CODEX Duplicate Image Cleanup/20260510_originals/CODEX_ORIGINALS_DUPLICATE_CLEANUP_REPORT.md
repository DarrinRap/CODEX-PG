# CODEX Originals Duplicate Cleanup Report

Date: 2026-05-10
Target: `C:\panda-gallery\originals`
Mode: safe cleanup by exact SHA-256 duplicate hash

## Result

- Initial image files: 113
- Exact duplicate hash groups found: 44
- Duplicate files beyond one-per-hash initially: 69
- Files moved out of `originals`: 35
- Bytes moved: 816,446
- Remaining image files in `originals`: 78
- Remaining duplicate hash groups: 29
- Remaining duplicate files beyond one-per-hash: 34
- Missing live DB `patient_images.file_path` targets after cleanup: 0

## Safety Policy Used

Only exact byte-for-byte duplicate image files were moved.

A duplicate file was kept if it was live-referenced by either:

- `panda_gallery.db` via `patient_images.file_path`, or
- text/source/mockup files containing the exact filename.

This avoids breaking current patient image records or PG overhaul mockup HTML files that hardcode `file:///C:/panda-gallery/originals/...` paths.

## Quarantine

Moved files were not permanently deleted. They were moved to:

`C:\CODEX PG\CODEX Duplicate Image Cleanup\20260510_originals\quarantine`

Manifests:

- Analysis summary: `C:\CODEX PG\CODEX Duplicate Image Cleanup\20260510_originals\analysis_summary.json`
- Cleanup plan: `C:\CODEX PG\CODEX Duplicate Image Cleanup\20260510_originals\duplicate_cleanup_plan.csv`
- Moved files: `C:\CODEX PG\CODEX Duplicate Image Cleanup\20260510_originals\moved_files.csv`

## Remaining Duplicates

34 duplicate-content files remain because they are referenced. Removing those safely would require an aggressive consolidation pass that updates database and/or mockup/source references to canonical files first.
