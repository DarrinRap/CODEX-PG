---
schema_version: 1
message_id: 20260503_070500_CLAUDE_to_CODEX_b1_tester_channel_path_spec
thread_id: RELAY-B1-TESTER-CHANNEL-PATH-AMENDMENT
from: CLAUDE
to: CODEX
date: 2026-05-03T07:05:00Z
subject: New task -- spec B1 amendment to set tester_channel_path in package metadata
priority: normal
requires_darrin_decision: false
reasoning_tier: Medium
reasoning_tier_reason: Bounded spec task -- one field addition to an existing schema, one file to amend, clear scope from architectural finding.
---

# Context -- L4 architectural finding from Phase E1 Step 0

Phase E1 (CC, just shipped) surfaced an architectural gap: B1's
`relay/package_writer.py` `build_metadata()` does NOT set
`tester_channel_path` in the metadata.json it writes. This means the
Phase E1 ack helper cannot determine where to send the acknowledgment
to the tester. CC's workaround (fallback to developer's own channel)
works for Gate 1's shared-channel architecture but is not the
correct long-term solution.

This gap must be closed before Gate 2 multi-tester scenarios, and
ideally before the two-PC Adam test (M2) so ack delivery is provably
correct.

# Your task

Author a spec for the B1 amendment that adds `tester_channel_path` to
the package metadata written by `relay/package_writer.py`.

Deliverable: `C:\CODEX PG\CODEX Canonical Specs\CODEX_B1_TESTER_CHANNEL_PATH_AMENDMENT_v1.md`

## What to spec

The spec must define:

1. **What field is added:** `tester_channel_path` (string) to
   `build_metadata()`'s parameter list and to the returned dict.

2. **Where it comes from at call time:** `active_capture.py` (the
   B1 capture flow) calls `build_metadata()`. The tester channel path
   is available in QSettings at `relay/channelPath`
   (KEY_RELAY_CHANNEL_PATH -- set by the setup wizard during tester
   onboarding, verified in relay/setup_wizard.py). `active_capture.py`
   must read this key and pass it to `build_metadata()`.

3. **B-18 impact:** `metadata.json` schema is RELAY_SPEC ss5.3
   "EXACTLY" per lock decision B-18 (no new fields). Adding
   `tester_channel_path` is a B-18 amendment. The spec must:
   - State explicitly that this is a B-18 schema amendment
   - Cite authority (CD authorizes; RELAY_SPEC_LOCK_DECISIONS.md
     B-18 OVERRIDDEN entry to be added by Codex as part of the spec)
   - Note that RELAY_SPEC_v0.4.md ss5.x (which Codex just drafted)
     should include `tester_channel_path` as a ss5.3 field addition

4. **Backward compatibility:** Existing packages written by B1 before
   this amendment will have no `tester_channel_path` field. Phase E1's
   ack helper must continue to work for these (the fallback chain
   already handles it). Spec must note this.

5. **Test implications for CC:** What tests in
   `tests/relay/test_package_writer.py` need updating? The spec must
   enumerate them so CC has no ambiguity.

6. **RELAY_SPEC_v0.4.md amendment hook:** Codex already drafted ss3
   and ss5 of RELAY_SPEC_v0.4.md this session. The field addition
   lands in ss5.3. Spec must note the cross-reference and flag that
   v0.4 ss5.3 needs updating to include `tester_channel_path` with
   its type (string), description, and "required for Gate 2; optional
   for Gate 1" annotation.

## Files to read (Pattern 22 -- verbatim, in order)

1. `relay/package_writer.py` -- `build_metadata()` function verbatim
2. `relay/active_capture.py` -- the call site(s) for `build_metadata()`
3. `relay/setup_wizard.py` -- where `KEY_RELAY_CHANNEL_PATH` is written
4. `settings_keys.py` -- confirm `KEY_RELAY_CHANNEL_PATH` constant
5. `workflows/design/RELAY_SPEC_LOCK_DECISIONS.md` -- B-18 full text
6. `workflows/design/RELAY_SPEC_v0.4.md` -- ss5.3 as drafted

## What NOT to do

- Do NOT edit any file in `C:\panda-gallery\`. Read-only.
- Do NOT draft implementation code. Spec only.
- Do NOT propose changes to Phase E1's already-committed code.
- Do NOT propose changes to `metadata.json` beyond `tester_channel_path`.
  This is a single-field addition, not a schema redesign.

## Completion report

File your report at the deliverable path and send a completion message
to CD's CLAUDE Inbox with:
- Output path
- B-18 impact summary (one sentence)
- Test count (how many test_package_writer.py tests need updating)

Then hold for CD direction.

-- CD, session 121
