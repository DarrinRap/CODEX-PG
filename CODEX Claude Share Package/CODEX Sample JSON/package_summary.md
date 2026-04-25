# Package Summary: pkg_sample_session_20260424_194422

Session: `session_20260424_194422`
Run: `run_20260424_194435`
State: `local_ready`

## Steps

- Step 1: FAIL - Capture region screenshot (evidence: ev_region_0001, ev_step_auto_0001)
- Step 2: PASS - Verify action bar stays reachable (evidence: none)
- Step 3: ACK - Open Testing Settings dialog (evidence: none)
- Step 4: PASS - Confirm mic status indicator (evidence: ev_region_0002)

## Evidence

- `ev_region_0001` - region_screenshot - Step 1 manual region capture
- `ev_step_auto_0001` - step_auto_screenshot - Step 1 automatic failure screenshot
- `ev_region_0002` - region_screenshot - Step 4 manual region capture
- `ev_transcript_span_0001` - transcript_span - Transcript span describing Step 1 placement issue
