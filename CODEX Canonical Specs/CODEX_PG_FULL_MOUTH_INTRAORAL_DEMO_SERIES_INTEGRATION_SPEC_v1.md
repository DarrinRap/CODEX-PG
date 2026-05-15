# CODEX PG Full-Mouth Intraoral Demo Series Integration Spec v1

Status: Ready for CD review and CC implementation routing
Date: 2026-05-10
Owner lane: Spec/audit/report by Codex; code/data integration only after CD routes to CC or Darrin explicitly authorizes Codex code edits

## Purpose

Add a real, license-safe, full-mouth intraoral photo series to Panda Gallery's reproducible demo seed so the app can demonstrate clinical photo handling, not only radiograph handling or isolated one-off intraoral examples.

The target series is the five-view same-patient set already curated locally by Codex:

- Source folder: `C:\panda-gallery\originals\demo_full_mouth_intraoral_series_open_license`
- Manifest: `SOURCE_LICENSE_MANIFEST_ZENODO_FULL_MOUTH_SERIES.json`
- Source record: https://zenodo.org/records/14827784
- Source article: https://www.nature.com/articles/s41597-025-05647-9
- License: Creative Commons Attribution 4.0 International, https://creativecommons.org/licenses/by/4.0/

## Current-State Findings

1. `scripts/seed_demo.py` is the canonical reproducible demo reset path. It backs up `panda_gallery.db`, `originals/`, and `thumbnails/`, wipes patient-referencing state, inserts four installer demo patients, imports fixture files from `demo_images/patient1` through `demo_images/patient4`, spreads captured dates, adds sample annotations/edits, and mounts existing radiograph series.
2. `phase_e_import_images()` imports every file directly inside each patient's fixture directory by iterating `fixture_dir.iterdir()` and filtering only `f.is_file()`. It does not recurse into subfolders, and it currently does not filter by image extension before calling `DatabaseManager.import_image()`.
3. `DatabaseManager.import_image()` copies a source image into `originals/{patient_id}/`, creates a thumbnail under `thumbnails/{patient_id}/`, and writes a `patient_images` row. Default category is `ImageCategory.PHOTOGRAPH`; grayscale/radiograph detection may override only if the image appears grayscale.
4. `PatientImage.display_label` exists and is shown under thumbnails when non-empty. This is the right place to expose canonical view labels such as `Frontal` and `Maxillary occlusal`.
5. `demo_images/patient4` is currently empty, and the existing project reference says patients 3 and 4 were intentionally left empty until fixtures are added. Patient 4 is therefore the cleanest low-risk demo host for a new photo series. Create the directory if it is absent.
6. The curated files under `originals/demo_full_mouth_intraoral_series_open_license` are not enough by themselves for PG. The app's user-visible demo data comes from the seeded database and import flow, not from arbitrary loose folders under `originals/`. Also note that a real `seed_demo.py` run wipes `originals/`, so this curated staging folder is temporary source material, not durable demo state.

## Non-Goals

- Do not scrape or ship random copyrighted dental-office photos.
- Do not directly insert rows into `panda_gallery.db` as the primary implementation path.
- Do not manually copy final assets into `originals/{patient_id}/` or `thumbnails/{patient_id}/`; let `DatabaseManager.import_image()` own those derivatives.
- Do not alter Vellum, PAH, tray, watcher, mailbox, or active CC work.
- Do not convert this five-photo clinical series into a radiograph `Full Mouth Series` template mount unless CD/Darrin separately approves a photo-series presentation feature.

## Required Implementation

### 0. Harden Fixture File Selection

Before adding attribution files beside patient fixtures, update `scripts/seed_demo.py` so both real import and dry-run counting use one supported-image filter.

Recommended constant near `DEMO_IMAGES_DIR`:

```python
SUPPORTED_DEMO_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif"}
```

Recommended helper, used by both `phase_e_import_images()` and `dry_run()`:

```python
def _demo_fixture_images(fixture_dir: Path) -> list[Path]:
    if not fixture_dir.exists():
        return []
    return sorted(
        f for f in fixture_dir.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_DEMO_IMAGE_EXTENSIONS
    )
```

Then replace the inline file scans in both `phase_e_import_images()` and `dry_run()` with this helper. This prevents README/license files from being counted in dry-run or becoming broken `patient_images` rows in a real seed.

### 1. Add Fixture Assets

Copy the five scrubbed local JPEGs from:

`C:\panda-gallery\originals\demo_full_mouth_intraoral_series_open_license`

into:

`C:\panda-gallery\demo_images\patient4\`

Use stable, view-sortable filenames:

- `full_mouth_intraoral_01_maxillary_occlusal_CC-BY-4.0.jpg`
- `full_mouth_intraoral_02_mandibular_occlusal_CC-BY-4.0.jpg`
- `full_mouth_intraoral_03_left_lateral_CC-BY-4.0.jpg`
- `full_mouth_intraoral_04_right_lateral_CC-BY-4.0.jpg`
- `full_mouth_intraoral_05_frontal_CC-BY-4.0.jpg`

Do not add nested folders under `demo_images/patient4` unless `seed_demo.py` is also intentionally changed to recurse. The current seed script is non-recursive. Non-image attribution files in `demo_images/patient4` are acceptable only after the image-extension filter in Step 0 is implemented.

### 2. Preserve Attribution With Fixtures

Add a compact attribution file beside the fixtures:

`C:\panda-gallery\demo_images\patient4\README_FULL_MOUTH_INTRAORAL_CC_BY_4.md`

The README must include:

- Zenodo record URL
- Scientific Data article URL
- DOI `10.5281/zenodo.14827784`
- License `CC BY 4.0`
- A note that the local copies were pixel-rendered/scrubbed by Codex before fixture use
- The anonymous source series id from the manifest: `anonymous_003-007-1002-01_1731041206649`

Do not include patient-identifying claims beyond what the dataset itself exposes. Treat the source as anonymous research/dataset imagery.

### 3. Add Seed Labels For Patient 4 Images

Update `scripts/seed_demo.py` so imported patient4 intraoral photos receive useful thumbnail labels after import.

Recommended minimal implementation:

- Add a small filename-to-label mapping near `PATIENTS` or near `phase_e_import_images()`.
- After each successful `db.import_image(...)`, if `src.name` exists in the mapping, update that `patient_images` row's `display_label` and optional `tags`/`notes` through the existing database session or a small sqlite update.

Required labels:

- Maxillary occlusal
- Mandibular occlusal
- Left lateral
- Right lateral
- Frontal

Recommended tags: `demo,intraoral,full-mouth,cc-by-4.0`

Recommended note prefix: `Open-license demo intraoral series. Source attribution in demo_images/patient4/README_FULL_MOUTH_INTRAORAL_CC_BY_4.md.`

### 4. Keep Patient 4 As The Demo Host

Use existing patient 4 (`PT-000004`, Bob Williams) for this first integration. Do not add a fifth patient in this task unless CD chooses a broader demo-data redesign.

Rationale: patient 4 is already in the canonical seed and currently empty, so this produces visible new value with minimal seed-script churn.

### 5. Do Not Mount Into Existing Radiograph Templates

Leave the images in the library as clinical photographs. The existing `phase_h_series()` mounts Carol and Alice radiographs into radiograph-oriented templates. A five-photo intraoral set does not fit the current 18-slot radiographic full-mouth template without a separate photo-series layout decision.

Optional future task: define a clinical photo presentation template with exactly five expected slots:

1. Maxillary occlusal
2. Mandibular occlusal
3. Left lateral
4. Right lateral
5. Frontal

That should be a separate spec because it affects template vocabulary, slot expectations, presentation behavior, and demo QA.

## Acceptance Criteria

AC1. `python scripts/seed_demo.py --dry-run` reports patient4 has five fixture images and the total fixture count increases by five. README/license files are not counted as importable fixtures because `dry_run()` uses the same `_demo_fixture_images()` helper as real import.

AC2. Running `python scripts/seed_demo.py` creates backups, imports the five patient4 JPEGs through `DatabaseManager.import_image()`, and generates five matching thumbnails under `thumbnails/4/`.

AC3. In SQLite, patient4 has exactly five active `patient_images` rows for the full-mouth intraoral files after a clean seed run; no README/license/manifest file appears as a `patient_images` row.

Suggested verification query:

```sql
SELECT p.patient_number, p.first_name, p.last_name,
       i.original_filename, i.category, i.image_type, i.display_label,
       i.width, i.height, i.status
FROM patient_images i
JOIN patients p ON p.id = i.patient_id
WHERE p.patient_number = 'PT-000004'
ORDER BY i.original_filename;
```

Expected display labels, in filename order:

- Maxillary occlusal
- Mandibular occlusal
- Left lateral
- Right lateral
- Frontal

AC4. Opening PG after seeding shows Bob Williams with five clinical photo thumbnails in the library. Each thumbnail opens in the editor without a missing-file or no-preview state.

AC5. The files remain categorized as photographs, not radiographs, unless existing auto-detection genuinely classifies a grayscale-looking file as a radiograph. If any are misclassified, fix with an explicit seed-script category correction for these five filenames.

AC6. `SOURCE_LICENSE_MANIFEST_ZENODO_FULL_MOUTH_SERIES.json` or its README-derived attribution survives in the repo-adjacent fixture area. The final demo should not contain source images without attribution.

AC7. No changes are made to `originals/` or `thumbnails/` by hand as committed source files. Those folders remain generated outputs from `seed_demo.py` and runtime import behavior.

## Suggested Tests

1. Dry-run seed:

```powershell
cd C:\panda-gallery
python scripts\seed_demo.py --dry-run
```

2. Real seed, only when CD/Darrin authorizes the destructive reset behavior:

```powershell
cd C:\panda-gallery
python scripts\seed_demo.py
```

3. Database verification:

```powershell
@'
import sqlite3
conn = sqlite3.connect(r'C:\panda-gallery\panda_gallery.db')
rows = conn.execute('''
SELECT i.original_filename, i.category, i.image_type, i.display_label, i.width, i.height, i.status
FROM patient_images i
JOIN patients p ON p.id = i.patient_id
WHERE p.patient_number = 'PT-000004'
ORDER BY i.original_filename
''').fetchall()
for row in rows:
    print(row)
assert len(rows) == 5, rows
assert all(r[6] == 'ACTIVE' for r in rows)
assert [r[3] for r in rows] == [
    'Maxillary occlusal', 'Mandibular occlusal', 'Left lateral', 'Right lateral', 'Frontal'
]
'@ | python -
```

4. Visual smoke: launch PG, select Bob Williams, confirm all five thumbnails render, open each image, and confirm no missing image/no preview state.

5. Git hygiene check:

```powershell
git -C C:\panda-gallery status --short -- demo_images scripts/seed_demo.py originals thumbnails panda_gallery.db
```

Expected source changes should be limited to `demo_images/patient4/*` and `scripts/seed_demo.py` unless CD requests a separate central attribution file. `originals/`, `thumbnails/`, and `panda_gallery.db` may be dirty after running the real seed locally but should not be committed unless CD explicitly requests a demo-state snapshot.

## Implementation Notes For CC

- Use `shutil.copy2` or normal file copy only for adding source fixtures to `demo_images/patient4`; do not re-download from Zenodo during implementation.
- Preserve the exact local curated images already produced by Codex; they have been metadata-scrubbed and verified.
- If a fixture filename collides with existing files in `demo_images/patient4`, stop and ask CD before replacing anything.
- Do not rely on `originals/demo_full_mouth_intraoral_series_open_license` after a real seed run; `phase_b_wipe()` removes all children of `originals/`. Preserve fixture copies and attribution under `demo_images/patient4` before any real seed.
- Because `seed_demo.py` is destructive by design, always dry-run first and do not run the real seed unless CD/Darrin accepts the reset/backups.

## Open Questions

1. Should Bob Williams remain the host patient, or should CD/Darrin rename patient4 to a more explicit demo case such as `Demo Intraoral Series` in a later seed-data redesign?
2. Should a five-slot intraoral photo template be added later, or is library visibility enough for the current demo need?
3. Should the demo bundle include the full Zenodo attribution manifest, or is the compact README enough for distributed builds?





