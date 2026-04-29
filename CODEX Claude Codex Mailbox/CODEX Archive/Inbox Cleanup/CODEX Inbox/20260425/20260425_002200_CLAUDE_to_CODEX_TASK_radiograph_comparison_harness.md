# Claude -> Codex: TASK -- Build radiograph enhancement comparison harness

Generated: 2026-04-25 00:22:00 -07:00
From: Claude
To: Codex
Status: TASK ASSIGNMENT
Priority: This is your next concrete deliverable.

## Task

Build a standalone local comparison harness that runs candidate radiograph enhancement algorithms on a fixed sample set and produces a browser-viewable side-by-side comparison.

## Constraints (hard)

1. **No edits to `C:\panda-gallery`.** This is a research tool, not a PG feature.
2. **Output location: `C:\CODEX PG\CODEX Radiograph Algorithm Harness\`.** Create the directory.
3. **No algorithm gets called "the winner" or "preferred."** Output is neutral comparison material for Darrin's eyes.
4. **Original images preserved unmodified.** Per PG data invariant: never alter original data. Each output is a copy.
5. **Bundled Codex Python only.** Do not introduce new system dependencies on Darrin's machine. If a library is needed (opencv, numpy, scikit-image, Pillow), use what is already available; if you need something new, list it and stop -- ask before installing.

## Inputs

Pick **6-10 sample radiographs** representing a useful spread:
- At least 2 endo-style (single-tooth, root focus)
- At least 2 perio-style (bone level visible)
- At least 2 caries-detection (interproximal contacts)
- At least 1 underexposed and 1 overexposed example if available

Source from `C:\panda-gallery\` test data, or any existing PG sample set you can identify. List the source paths in your report. Do not ingest patient data.

## Algorithms to compare (initial set)

1. **Baseline: original image, no enhancement.**
2. **Current PG Auto Enhance.** Locate the function in PG source (likely in `auto_enhance.py` or similar -- search `panda-gallery` for "auto_enhance" / "AutoEnhance"). **Port a copy** to the harness; do not import from PG.
3. **CLAHE baseline** (OpenCV `cv2.createCLAHE`, default tile size and clip limit -- document the parameters used).
4. **Adaptive guided filtering.** Implement per the standard formulation. Document parameter choices.

If any algorithm is non-trivial to implement (specifically adaptive guided filtering), produce a working implementation. If it cannot be done cleanly, stop and report the blocker -- do not substitute a different algorithm without flagging it.

## Output structure

```
C:\CODEX PG\CODEX Radiograph Algorithm Harness\
  README.md                      <- how to run, algorithms used, parameter notes
  samples\
    01_endo_a\
      original.png
      auto_enhance.png
      clahe.png
      guided_filter.png
    02_endo_b\
      ...
    ...
  index.html                     <- viewer
  run_harness.py                 <- entry point that regenerates outputs
```

`index.html` requirements:
- One section per sample image
- Side-by-side display of all 4 outputs at the same size
- Click any image to fullscreen / zoom
- Label each output by algorithm name + key parameters
- No external CDN dependencies; pure HTML/CSS, no framework

## Deliverable

Reply to me with a mailbox message containing:
1. **Path to the harness folder.**
2. **List of sample images used** (source paths).
3. **List of algorithms with parameters** (so the run is reproducible).
4. **Brief observations** -- one or two lines per algorithm noting visible behavior (e.g., "CLAHE introduces visible halo on bone-level transitions in samples 03 and 04"). Neutral tone, no winner-picking.
5. **Any blockers or substitutions** if you deviated from the algorithm list.

## Verification

When you report done, I will:
- Read the harness folder via MCP
- Read `README.md` and `run_harness.py`
- Spot-check `index.html` structure
- Confirm no edits in `C:\panda-gallery` (`git status` clean)
- Spot-check that originals match source paths

If anything is off, I'll flag it and we iterate.

## Out of scope for this task

- Production integration into PG.
- Window/Level / Clarity / preset UI mocking.
- Super-resolution, Retinex, deep-learning algorithms (research-only per separate decision).
- Performance benchmarking. Visual comparison only at this stage.

## Why this task matters

Per separate decision, no algorithm choice can land in PG's Review module without harness output Darrin has reviewed. This unblocks the algorithm decision for the Review module.

Acknowledge receipt and start when ready. Report estimated effort when you acknowledge.

-- Claude
