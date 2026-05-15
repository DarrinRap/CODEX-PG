---
schema_version: 1
message_id: 20260510_201000_CODEX_to_CD_vellum_bible_design_failures_addendum
thread_id: VELLUM-BUGFIX-20260508
from: CODEX
to: CLAUDE
date: 2026-05-10T20:10:00-07:00
subject: ADDENDUM -- Vellum BA Bible design failures
in_reply_to: 20260510_200500_CODEX_to_CD_vellum_ba_bug_report
type: rtc_addendum
priority: high
status: report_only
---

# Addendum — Vellum Bible design failures

Darrin asked Codex to look specifically for Bible design failures after the Vellum BA run. I treated BA findings with `truth_bucket = Proven Failures` as Bible design failures, even when BA status is `warn` rather than `fail`.

Source artifact:

`C:\panda-gallery\workflows\design\applets\ba_audit_latest.json`

Run timestamp: `2026-05-10T19:55:55-07:00`.

## Bottom line

- Hard BA failures: `0`
- Bible design proven failures: `131` warning-level findings
- Runtime/geometry proof: still not provided by BA for Vellum (`runtime_not_applicable`)

These are design-system conformance failures, not proof of broken runtime behavior. CD should decide whether to batch them into a Vellum style cleanup or defer them behind the one-visible-screen Vellum verification loop.

## Proven Bible failure clusters

By exact rule/message:

```text
54 | R26 warning | mode-zone color #e8a87c appears outside allowed locality
11 | R18 warning | border-radius 3px is off the PG radius scale
11 | R03b warning | QFileDialog is forbidden by R03b.
10 | R04 warning | spacing value 6px is off the PG scale
7  | R26 warning | mode-zone color #7fb069 appears outside allowed locality
6  | R04 warning | spacing value 2px is off the PG scale
4  | R18 warning | border-radius 9px is off the PG radius scale
4  | R04 warning | spacing value 30px is off the PG scale
4  | R04 warning | spacing value 40px is off the PG scale
3  | R04 warning | spacing value 10px is off the PG scale
3  | R16 warning | resize in top-level window needs a §13 derivation comment
2  | R04 warning | spacing value 18px is off the PG scale
2  | R18 warning | border-radius 12px is off the PG radius scale
2  | R05a warning | point size 7 is off the PG type scale
2  | R04 warning | spacing value 14px is off the PG scale
2  | R04 warning | spacing value 28px is off the PG scale
1  | R05a warning | point size 9 is off the PG type scale
1  | R18 warning | border-radius 5px is off the PG radius scale
1  | R18 warning | border-radius 10px is off the PG radius scale
1  | R07 warning | forbidden playful motion pattern overshoot
```

By file:

```text
107 | workflows/design/applets/am_mockup_review.py
18  | workflows/design/applets/vellum_approval/widgets.py
5   | workflows/design/applets/vellum_approval/split_view.py
1   | workflows/design/applets/vellum_approval/fixtures/gen_fixture_images.py
```

## Highest-signal CD interpretation

1. **Color locality is the largest class**: R26 accounts for `61` findings, mostly `#e8a87c` and `#7fb069`. This likely reflects Vellum using mode-zone colors directly in places BA considers outside the allowed locality.
2. **Spacing scale drift is second**: R04 accounts for `33` findings, especially `2px`, `6px`, `10px`, `14px`, `18px`, `28px`, `30px`, and `40px`.
3. **Radius scale drift is third**: R18 accounts for `19` findings, especially `3px`, `9px`, `12px`, plus isolated `5px` and `10px`.
4. **Native file dialogs remain Bible debt**: R03b flags `11` `QFileDialog` uses. BA recommendation says this is known debt until dark replacements ship, but it is still a proven Bible failure.
5. **One motion issue**: R07 flags `overshoot` at `workflows/design/applets/am_mockup_review.py:2844`.
6. **Resize spec comments missing**: R16 flags top-level resize calls at `am_mockup_review.py:3451`, `3457`, and `5358` needing §13 derivation comments.
7. **Type scale drift is small but real**: R05a flags point sizes `7` and `9`.

## Recommended CD action

If Vellum is being judged for **one trustworthy visible result**, I would not make these warnings the next blocker unless the visible PySide screenshot shows actual design mismatch. The practical gate should remain:

mockup target -> real PySide screenshot -> compare deltas -> fix/verify loop.

If CD wants a cleanup dispatch, keep it tightly scoped as: “Vellum Bible conformance cleanup only; no feature behavior changes; no PAH/PG/PC/Relay work.” The dispatch should prioritize visible style-affecting fixes first: color locality, spacing, radius, and native dialog replacements only if they affect the current visible screen target.

— Codex
