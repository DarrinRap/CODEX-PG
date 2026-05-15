---
schema_version: 1
message_id: 20260510_201500_CODEX_to_CD_vellum_bible_failures_line_list
thread_id: VELLUM-BUGFIX-20260508
from: CODEX
to: CLAUDE
date: 2026-05-10T20:15:00-07:00
subject: ADDENDUM -- Full line-level Vellum Bible design failure list
in_reply_to: 20260510_201000_CODEX_to_CD_vellum_bible_design_failures_addendum
type: rtc_addendum
priority: high
status: report_only
---

# Addendum — Full line-level Vellum Bible design failure list

Darrin asked whether CD received precise, actionable detail for the 131 warning-level Bible design failures. This addendum supplies the complete line-level list from the current BA JSON artifact.

Source artifact: `C:\panda-gallery\workflows\design\applets\ba_audit_latest.json`

Run timestamp: `05/10/2026 19:56:10`

Total proven Bible design failures listed here: `131`

## Repair Guidance By Rule

- R26: Replace or localize direct mode-zone color use; use approved tokens/locality or document a legitimate suppression.
- R04: Move spacing values onto the PG spacing scale.
- R18: Move border-radius values onto the PG radius scale.
- R03b: Replace native `QFileDialog` surfaces with approved dark/PG-native dialog surfaces when this screen is in scope; BA notes this as known debt until dark replacements ship.
- R16: Add section 13 derivation comments for top-level resize behavior or route through approved computed size helpers.
- R05a: Move point sizes onto the PG type scale.
- R07: Replace forbidden playful motion/timing pattern `overshoot` with Bible-approved timing/easing.

## Full Actionable List

| # | BA ID | Rule | File:line | Failure | Action |
|---:|---|---|---|---|---|
| 1 | BA-LINT-VELLUM-0001 | R26 warning | `workflows/design/applets/am_mockup_review.py:275` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 2 | BA-LINT-VELLUM-0002 | R26 warning | `workflows/design/applets/am_mockup_review.py:278` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 3 | BA-LINT-VELLUM-0003 | R26 warning | `workflows/design/applets/am_mockup_review.py:281` | mode-zone color #7fb069 appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 4 | BA-LINT-VELLUM-0004 | R26 warning | `workflows/design/applets/am_mockup_review.py:284` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 5 | BA-LINT-VELLUM-0006 | R26 warning | `workflows/design/applets/am_mockup_review.py:1395` | mode-zone color #7fb069 appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 6 | BA-LINT-VELLUM-0007 | R26 warning | `workflows/design/applets/am_mockup_review.py:2207` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 7 | BA-LINT-VELLUM-0008 | R26 warning | `workflows/design/applets/am_mockup_review.py:2352` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 8 | BA-LINT-VELLUM-0009 | R26 warning | `workflows/design/applets/am_mockup_review.py:2601` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 9 | BA-LINT-VELLUM-0010 | R26 warning | `workflows/design/applets/am_mockup_review.py:2674` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 10 | BA-LINT-VELLUM-0011 | R07 warning | `workflows/design/applets/am_mockup_review.py:2844` | forbidden playful motion pattern overshoot | Use a Bible-approved timing. |
| 11 | BA-LINT-VELLUM-0012 | R26 warning | `workflows/design/applets/am_mockup_review.py:3062` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 12 | BA-LINT-VELLUM-0013 | R26 warning | `workflows/design/applets/am_mockup_review.py:3063` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 13 | BA-LINT-VELLUM-0014 | R26 warning | `workflows/design/applets/am_mockup_review.py:3064` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 14 | BA-LINT-VELLUM-0015 | R26 warning | `workflows/design/applets/am_mockup_review.py:3065` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 15 | BA-LINT-VELLUM-0016 | R26 warning | `workflows/design/applets/am_mockup_review.py:3066` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 16 | BA-LINT-VELLUM-0017 | R26 warning | `workflows/design/applets/am_mockup_review.py:3068` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 17 | BA-LINT-VELLUM-0018 | R26 warning | `workflows/design/applets/am_mockup_review.py:3071` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 18 | BA-LINT-VELLUM-0019 | R26 warning | `workflows/design/applets/am_mockup_review.py:3072` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 19 | BA-LINT-VELLUM-0020 | R26 warning | `workflows/design/applets/am_mockup_review.py:3074` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 20 | BA-LINT-VELLUM-0021 | R26 warning | `workflows/design/applets/am_mockup_review.py:3075` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 21 | BA-LINT-VELLUM-0022 | R26 warning | `workflows/design/applets/am_mockup_review.py:3149` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 22 | BA-LINT-VELLUM-0025 | R16 warning | `workflows/design/applets/am_mockup_review.py:3451` | resize in top-level window needs a §13 derivation comment | Address the lint violation or document a legitimate suppression. |
| 23 | BA-LINT-VELLUM-0026 | R16 warning | `workflows/design/applets/am_mockup_review.py:3457` | resize in top-level window needs a §13 derivation comment | Address the lint violation or document a legitimate suppression. |
| 24 | BA-LINT-VELLUM-0027 | R26 warning | `workflows/design/applets/am_mockup_review.py:3464` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 25 | BA-LINT-VELLUM-0028 | R04 warning | `workflows/design/applets/am_mockup_review.py:3468` | spacing value 6px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 26 | BA-LINT-VELLUM-0029 | R26 warning | `workflows/design/applets/am_mockup_review.py:3604` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 27 | BA-LINT-VELLUM-0030 | R18 warning | `workflows/design/applets/am_mockup_review.py:3611` | border-radius 3px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 28 | BA-LINT-VELLUM-0031 | R26 warning | `workflows/design/applets/am_mockup_review.py:3623` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 29 | BA-LINT-VELLUM-0032 | R26 warning | `workflows/design/applets/am_mockup_review.py:3638` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 30 | BA-LINT-VELLUM-0033 | R26 warning | `workflows/design/applets/am_mockup_review.py:3650` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 31 | BA-LINT-VELLUM-0034 | R26 warning | `workflows/design/applets/am_mockup_review.py:3677` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 32 | BA-LINT-VELLUM-0035 | R26 warning | `workflows/design/applets/am_mockup_review.py:3693` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 33 | BA-LINT-VELLUM-0036 | R26 warning | `workflows/design/applets/am_mockup_review.py:3696` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 34 | BA-LINT-VELLUM-0037 | R26 warning | `workflows/design/applets/am_mockup_review.py:3697` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 35 | BA-LINT-VELLUM-0038 | R18 warning | `workflows/design/applets/am_mockup_review.py:3707` | border-radius 5px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 36 | BA-LINT-VELLUM-0039 | R26 warning | `workflows/design/applets/am_mockup_review.py:3712` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 37 | BA-LINT-VELLUM-0040 | R18 warning | `workflows/design/applets/am_mockup_review.py:3770` | border-radius 3px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 38 | BA-LINT-VELLUM-0041 | R26 warning | `workflows/design/applets/am_mockup_review.py:3774` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 39 | BA-LINT-VELLUM-0042 | R18 warning | `workflows/design/applets/am_mockup_review.py:3778` | border-radius 3px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 40 | BA-LINT-VELLUM-0043 | R18 warning | `workflows/design/applets/am_mockup_review.py:3783` | border-radius 3px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 41 | BA-LINT-VELLUM-0044 | R26 warning | `workflows/design/applets/am_mockup_review.py:3797` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 42 | BA-LINT-VELLUM-0045 | R26 warning | `workflows/design/applets/am_mockup_review.py:3798` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 43 | BA-LINT-VELLUM-0046 | R18 warning | `workflows/design/applets/am_mockup_review.py:3812` | border-radius 3px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 44 | BA-LINT-VELLUM-0047 | R26 warning | `workflows/design/applets/am_mockup_review.py:3833` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 45 | BA-LINT-VELLUM-0048 | R26 warning | `workflows/design/applets/am_mockup_review.py:3833` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 46 | BA-LINT-VELLUM-0049 | R18 warning | `workflows/design/applets/am_mockup_review.py:3836` | border-radius 3px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 47 | BA-LINT-VELLUM-0050 | R18 warning | `workflows/design/applets/am_mockup_review.py:3874` | border-radius 3px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 48 | BA-LINT-VELLUM-0051 | R26 warning | `workflows/design/applets/am_mockup_review.py:3880` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 49 | BA-LINT-VELLUM-0052 | R26 warning | `workflows/design/applets/am_mockup_review.py:3913` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 50 | BA-LINT-VELLUM-0053 | R18 warning | `workflows/design/applets/am_mockup_review.py:3915` | border-radius 3px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 51 | BA-LINT-VELLUM-0054 | R26 warning | `workflows/design/applets/am_mockup_review.py:3916` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 52 | BA-LINT-VELLUM-0055 | R26 warning | `workflows/design/applets/am_mockup_review.py:3918` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 53 | BA-LINT-VELLUM-0056 | R18 warning | `workflows/design/applets/am_mockup_review.py:3919` | border-radius 3px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 54 | BA-LINT-VELLUM-0057 | R26 warning | `workflows/design/applets/am_mockup_review.py:3934` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 55 | BA-LINT-VELLUM-0058 | R26 warning | `workflows/design/applets/am_mockup_review.py:3961` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 56 | BA-LINT-VELLUM-0059 | R26 warning | `workflows/design/applets/am_mockup_review.py:3977` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 57 | BA-LINT-VELLUM-0060 | R26 warning | `workflows/design/applets/am_mockup_review.py:3985` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 58 | BA-LINT-VELLUM-0061 | R26 warning | `workflows/design/applets/am_mockup_review.py:4218` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 59 | BA-LINT-VELLUM-0062 | R26 warning | `workflows/design/applets/am_mockup_review.py:4221` | mode-zone color #7fb069 appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 60 | BA-LINT-VELLUM-0064 | R26 warning | `workflows/design/applets/am_mockup_review.py:4442` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 61 | BA-LINT-VELLUM-0065 | R26 warning | `workflows/design/applets/am_mockup_review.py:4444` | mode-zone color #7fb069 appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 62 | BA-LINT-VELLUM-0066 | R05a warning | `workflows/design/applets/am_mockup_review.py:4463` | point size 7 is off the PG type scale | Address the lint violation or document a legitimate suppression. |
| 63 | BA-LINT-VELLUM-0067 | R05a warning | `workflows/design/applets/am_mockup_review.py:4528` | point size 9 is off the PG type scale | Address the lint violation or document a legitimate suppression. |
| 64 | BA-LINT-VELLUM-0068 | R04 warning | `workflows/design/applets/am_mockup_review.py:4609` | spacing value 2px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 65 | BA-LINT-VELLUM-0069 | R04 warning | `workflows/design/applets/am_mockup_review.py:4609` | spacing value 2px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 66 | BA-LINT-VELLUM-0070 | R04 warning | `workflows/design/applets/am_mockup_review.py:4610` | spacing value 2px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 67 | BA-LINT-VELLUM-0071 | R04 warning | `workflows/design/applets/am_mockup_review.py:4837` | spacing value 6px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 68 | BA-LINT-VELLUM-0072 | R26 warning | `workflows/design/applets/am_mockup_review.py:5008` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 69 | BA-LINT-VELLUM-0073 | R26 warning | `workflows/design/applets/am_mockup_review.py:5012` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 70 | BA-LINT-VELLUM-0074 | R26 warning | `workflows/design/applets/am_mockup_review.py:5022` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 71 | BA-LINT-VELLUM-0075 | R05a warning | `workflows/design/applets/am_mockup_review.py:5054` | point size 7 is off the PG type scale | Address the lint violation or document a legitimate suppression. |
| 72 | BA-LINT-VELLUM-0076 | R26 warning | `workflows/design/applets/am_mockup_review.py:5098` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 73 | BA-LINT-VELLUM-0077 | R26 warning | `workflows/design/applets/am_mockup_review.py:5119` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 74 | BA-LINT-VELLUM-0078 | R18 warning | `workflows/design/applets/am_mockup_review.py:5120` | border-radius 12px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 75 | BA-LINT-VELLUM-0079 | R26 warning | `workflows/design/applets/am_mockup_review.py:5123` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 76 | BA-LINT-VELLUM-0080 | R26 warning | `workflows/design/applets/am_mockup_review.py:5139` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 77 | BA-LINT-VELLUM-0081 | R26 warning | `workflows/design/applets/am_mockup_review.py:5143` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 78 | BA-LINT-VELLUM-0082 | R26 warning | `workflows/design/applets/am_mockup_review.py:5147` | mode-zone color #7fb069 appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 79 | BA-LINT-VELLUM-0083 | R18 warning | `workflows/design/applets/am_mockup_review.py:5148` | border-radius 10px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 80 | BA-LINT-VELLUM-0084 | R26 warning | `workflows/design/applets/am_mockup_review.py:5151` | mode-zone color #7fb069 appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 81 | BA-LINT-VELLUM-0088 | R04 warning | `workflows/design/applets/am_mockup_review.py:5171` | spacing value 10px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 82 | BA-LINT-VELLUM-0087 | R04 warning | `workflows/design/applets/am_mockup_review.py:5171` | spacing value 14px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 83 | BA-LINT-VELLUM-0086 | R04 warning | `workflows/design/applets/am_mockup_review.py:5171` | spacing value 10px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 84 | BA-LINT-VELLUM-0085 | R04 warning | `workflows/design/applets/am_mockup_review.py:5171` | spacing value 14px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 85 | BA-LINT-VELLUM-0089 | R04 warning | `workflows/design/applets/am_mockup_review.py:5172` | spacing value 2px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 86 | BA-LINT-VELLUM-0090 | R04 warning | `workflows/design/applets/am_mockup_review.py:5226` | spacing value 40px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 87 | BA-LINT-VELLUM-0091 | R04 warning | `workflows/design/applets/am_mockup_review.py:5226` | spacing value 30px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 88 | BA-LINT-VELLUM-0092 | R04 warning | `workflows/design/applets/am_mockup_review.py:5226` | spacing value 40px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 89 | BA-LINT-VELLUM-0093 | R04 warning | `workflows/design/applets/am_mockup_review.py:5226` | spacing value 30px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 90 | BA-LINT-VELLUM-0094 | R04 warning | `workflows/design/applets/am_mockup_review.py:5284` | spacing value 40px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 91 | BA-LINT-VELLUM-0095 | R04 warning | `workflows/design/applets/am_mockup_review.py:5284` | spacing value 30px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 92 | BA-LINT-VELLUM-0096 | R04 warning | `workflows/design/applets/am_mockup_review.py:5284` | spacing value 40px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 93 | BA-LINT-VELLUM-0097 | R04 warning | `workflows/design/applets/am_mockup_review.py:5284` | spacing value 30px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 94 | BA-LINT-VELLUM-0098 | R04 warning | `workflows/design/applets/am_mockup_review.py:5285` | spacing value 10px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 95 | BA-LINT-VELLUM-0099 | R04 warning | `workflows/design/applets/am_mockup_review.py:5328` | spacing value 28px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 96 | BA-LINT-VELLUM-0100 | R04 warning | `workflows/design/applets/am_mockup_review.py:5328` | spacing value 18px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 97 | BA-LINT-VELLUM-0101 | R04 warning | `workflows/design/applets/am_mockup_review.py:5328` | spacing value 28px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 98 | BA-LINT-VELLUM-0102 | R04 warning | `workflows/design/applets/am_mockup_review.py:5328` | spacing value 18px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 99 | BA-LINT-VELLUM-0104 | R16 warning | `workflows/design/applets/am_mockup_review.py:5358` | resize in top-level window needs a §13 derivation comment | Address the lint violation or document a legitimate suppression. |
| 100 | BA-LINT-VELLUM-0107 | R03b warning | `workflows/design/applets/am_mockup_review.py:6494` | QFileDialog is forbidden by R03b. | Known debt until dark replacements ship; avoid new uses when possible. |
| 101 | BA-LINT-VELLUM-0108 | R03b warning | `workflows/design/applets/am_mockup_review.py:6521` | QFileDialog is forbidden by R03b. | Known debt until dark replacements ship; avoid new uses when possible. |
| 102 | BA-LINT-VELLUM-0109 | R03b warning | `workflows/design/applets/am_mockup_review.py:7786` | QFileDialog is forbidden by R03b. | Known debt until dark replacements ship; avoid new uses when possible. |
| 103 | BA-LINT-VELLUM-0110 | R03b warning | `workflows/design/applets/am_mockup_review.py:7787` | QFileDialog is forbidden by R03b. | Known debt until dark replacements ship; avoid new uses when possible. |
| 104 | BA-LINT-VELLUM-0111 | R03b warning | `workflows/design/applets/am_mockup_review.py:7829` | QFileDialog is forbidden by R03b. | Known debt until dark replacements ship; avoid new uses when possible. |
| 105 | BA-LINT-VELLUM-0112 | R03b warning | `workflows/design/applets/am_mockup_review.py:7830` | QFileDialog is forbidden by R03b. | Known debt until dark replacements ship; avoid new uses when possible. |
| 106 | BA-LINT-VELLUM-0113 | R03b warning | `workflows/design/applets/am_mockup_review.py:7905` | QFileDialog is forbidden by R03b. | Known debt until dark replacements ship; avoid new uses when possible. |
| 107 | BA-LINT-VELLUM-0114 | R03b warning | `workflows/design/applets/am_mockup_review.py:7910` | QFileDialog is forbidden by R03b. | Known debt until dark replacements ship; avoid new uses when possible. |
| 108 | BA-LINT-VELLUM-0117 | R26 warning | `workflows/design/applets/vellum_approval/fixtures/gen_fixture_images.py:13` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 109 | BA-LINT-VELLUM-0122 | R03b warning | `workflows/design/applets/vellum_approval/split_view.py:35` | QFileDialog is forbidden by R03b. | Known debt until dark replacements ship; avoid new uses when possible. |
| 110 | BA-LINT-VELLUM-0123 | R26 warning | `workflows/design/applets/vellum_approval/split_view.py:108` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 111 | BA-LINT-VELLUM-0125 | R04 warning | `workflows/design/applets/vellum_approval/split_view.py:346` | spacing value 6px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 112 | BA-LINT-VELLUM-0127 | R03b warning | `workflows/design/applets/vellum_approval/split_view.py:458` | QFileDialog is forbidden by R03b. | Known debt until dark replacements ship; avoid new uses when possible. |
| 113 | BA-LINT-VELLUM-0128 | R03b warning | `workflows/design/applets/vellum_approval/split_view.py:474` | QFileDialog is forbidden by R03b. | Known debt until dark replacements ship; avoid new uses when possible. |
| 114 | BA-LINT-VELLUM-0129 | R26 warning | `workflows/design/applets/vellum_approval/widgets.py:56` | mode-zone color #e8a87c appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 115 | BA-LINT-VELLUM-0130 | R26 warning | `workflows/design/applets/vellum_approval/widgets.py:58` | mode-zone color #7fb069 appears outside allowed locality | Address the lint violation or document a legitimate suppression. |
| 116 | BA-LINT-VELLUM-0132 | R18 warning | `workflows/design/applets/vellum_approval/widgets.py:148` | border-radius 9px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 117 | BA-LINT-VELLUM-0133 | R18 warning | `workflows/design/applets/vellum_approval/widgets.py:165` | border-radius 9px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 118 | BA-LINT-VELLUM-0134 | R18 warning | `workflows/design/applets/vellum_approval/widgets.py:170` | border-radius 12px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 119 | BA-LINT-VELLUM-0135 | R18 warning | `workflows/design/applets/vellum_approval/widgets.py:180` | border-radius 9px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 120 | BA-LINT-VELLUM-0136 | R18 warning | `workflows/design/applets/vellum_approval/widgets.py:211` | border-radius 9px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 121 | BA-LINT-VELLUM-0137 | R18 warning | `workflows/design/applets/vellum_approval/widgets.py:216` | border-radius 3px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 122 | BA-LINT-VELLUM-0138 | R18 warning | `workflows/design/applets/vellum_approval/widgets.py:218` | border-radius 3px is off the PG radius scale | Address the lint violation or document a legitimate suppression. |
| 123 | BA-LINT-VELLUM-0139 | R04 warning | `workflows/design/applets/vellum_approval/widgets.py:337` | spacing value 6px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 124 | BA-LINT-VELLUM-0140 | R04 warning | `workflows/design/applets/vellum_approval/widgets.py:426` | spacing value 6px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 125 | BA-LINT-VELLUM-0141 | R04 warning | `workflows/design/applets/vellum_approval/widgets.py:426` | spacing value 6px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 126 | BA-LINT-VELLUM-0142 | R04 warning | `workflows/design/applets/vellum_approval/widgets.py:427` | spacing value 2px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 127 | BA-LINT-VELLUM-0143 | R04 warning | `workflows/design/applets/vellum_approval/widgets.py:556` | spacing value 6px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 128 | BA-LINT-VELLUM-0144 | R04 warning | `workflows/design/applets/vellum_approval/widgets.py:633` | spacing value 2px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 129 | BA-LINT-VELLUM-0145 | R04 warning | `workflows/design/applets/vellum_approval/widgets.py:641` | spacing value 6px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 130 | BA-LINT-VELLUM-0146 | R04 warning | `workflows/design/applets/vellum_approval/widgets.py:737` | spacing value 6px is off the PG scale | Address the lint violation or document a legitimate suppression. |
| 131 | BA-LINT-VELLUM-0147 | R04 warning | `workflows/design/applets/vellum_approval/widgets.py:757` | spacing value 6px is off the PG scale | Address the lint violation or document a legitimate suppression. |

## CD Dispatch Note

If CD dispatches this, recommend a narrow style-only cleanup pass. Do not bundle feature behavior changes, runtime BA framework work, PAH, PG overhaul, PC, Relay, or mailbox cleanup into this Vellum pass.

— Codex
