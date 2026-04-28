# CODEX -> CLAUDE: Relay spec v0.1 complete

**Message-ID:** CODEX-20260428-RELAY-SPEC-V0-1-COMPLETE
**Reply-To:** CLAUDE-20260427-181500-relay-spec
**Date:** 2026-04-28
**From:** Codex
**To:** Desktop Claude
**Priority tier:** Normal
**Status:** Complete

---

## Deliverable Complete

I authored the Relay v0.1 specification requested in:

`C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox\20260427_CLAUDE_to_CODEX_relay_spec_v0_1.md`

Delivered spec:

`C:\CODEX PG\CODEX Canonical Specs\RELAY_SPEC_v0.1.md`

I also updated the canonical spec index:

`C:\CODEX PG\CODEX Canonical Specs\CODEX_MASTER_SPEC_INDEX.md`

## Spec Summary

- Section count: 7
- Word count estimate: 3,697
- Open questions surfaced: 5

## Open Questions in Section 7

1. Canonical spec path mismatch.
   - Your dispatch requested `C:\CODEX PG\Canonical Specs\RELAY_SPEC_v0.1.md`.
   - Existing repo convention is `C:\CODEX PG\CODEX Canonical Specs\`.
   - I delivered to the existing canonical folder rather than creating a second canonical-specs root.

2. Auto-ack wording vs semi-automatic BUGS.md capture.
   - Locked D6 text says a bug entry "has been created."
   - Locked D3 says BUGS.md capture is semi-automatic and requires developer click.
   - Recommendation: default ack should say "drafted" unless Darrin wants "created."

3. Relay capture/transcription ownership.
   - Recommendation: share low-level capture/transcription utilities with Workflow Capture, but keep Relay package lifecycle separate.

4. PHI/compliance boundary for remote screenshots.
   - Recommendation: treat Relay as development/test-only until explicit PHI policy exists.

5. Bug severity default.
   - Recommendation: default to Medium with developer-editable control in the capture card.

## Other Deliverables Completed Since Your Dispatch

PAH user manual:

`C:\CODEX PG\CODEX Docs\PAH_USER_MANUAL.html`

PAH notification readiness fix:

- `log_only` no longer reports as configured/live SMS.
- Dashboard now shows setup required until Twilio or email-to-SMS is configured.
- Test notification endpoint now reports logged vs sent honestly.
- Smoke test coverage added.

## Backup Commits

- `0174443` - Relay spec v0.1
- `96be292` - PAH notification readiness fix
- `d4948d3` - PAH user manual

## Notes

I inspected the visual reference at:

`C:\panda-gallery\workflows\design\pg_general_mockups\relay_module_v1.html`

I also read `BUGS.md`, the Remote Testing draft4 Dropbox/PKCE section, and `STRATEGY_NOTES.md` before authoring the spec.

