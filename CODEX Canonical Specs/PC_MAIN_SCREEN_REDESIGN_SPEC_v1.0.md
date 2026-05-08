# PANDA Collaborator — Main Screen Redesign Spec
# Version: 1.0
# Date: 2026-05-04
# Owner: Darrin (PandaPerio) / CD
# Audience: CC — mockup only, no production code
# Depends on: CODEX_PC_UI_UX_RED_DESIGN_SPEC_v1.md, PC_HANDOFF_PROGRESS_SPEC_v1.1.md
# Approved locked mockups: C:\CODEX PG\CODEX PANDA Collaborator\mockups\pc_redesign_v1\

---

## 1. Why This Spec Exists

Darrin eyeballed Phase 1 live and rejected the layout. Verbatim feedback:

> "no obvious changes. i want this screen to be mocked up from scratch in order to have it flow
> from left to right taking into account the sequence of events required based on earlier spec.
> status message view needs to be front and center not hidden. must also adhere to bible design,
> but colors different for user 1 vs user 2. general palette needs to match color palette and
> button design etc of our bible. the design of app must follow logical path of user through the app."

The current layout fails on four counts:
1. The 5-panel grid truncates labels ("RE...", "REGI...", "COLLABORA...", "Start Session / S...") — unreadable
2. Status Messages is a narrow panel at the bottom — the single most important live feedback surface is buried
3. The workflow columns have no spatial hierarchy — everything looks equally important
4. Large wasted whitespace inside panels (panels 1, 2 are mostly empty)

This spec defines a ground-up layout for the **main operational view** of PC. CC produces an HTML mockup. No production code.

---

## 2. The Logical User Path (Layout Must Reflect This)

The PC workflow has a clear sequence. The layout must make this sequence legible at a glance:

```
STEP 1        STEP 2         STEP 3             STEP 4              STEP 5
Register  →   Scan repo  →   Handover / Start  →  Work + monitor  →  End + handoff
users         + confirm       session               status             package
(one-time)    working tree    incoming user
```

The new layout weights space according to operational importance during a live session:

- **Steps 1–2** (setup + repo): compact — done once
- **Step 3** (identity + handover): moderate — visible but not dominant
- **Step 4** (status + activity): **dominant** — primary feedback surface
- **Step 5** (handoff): prominent — primary action when work is done

---

## 3. Layout Architecture

### 3.1 Top-level zones (left to right)

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  HEADER  (42px: app name | active user | repo pills | statusbar pills | controls)     │
├──────────────────────────────────────────────────────────────────────────────────────┤
│  WORKFLOW RAIL  (32px: 5 steps as compact progress rail with semantic state dots)     │
├──────────────┬───────────────────────────────────────┬───────────────────────────────┤
│              │                                       │                               │
│   LEFT COL   │          CENTER PANEL                 │       RIGHT PANEL             │
│   ~280px     │          flex-grow (largest)          │       ~360px                  │
│              │                                       │                               │
│  ┌─────────┐ │  ┌──────── STATUS MESSAGES ────────┐  │  ┌── CREATE SAFE HANDOFF ──┐  │
│  │ WORKING │ │  │  (primary feedback surface;      │  │  │  (dominant primary      │  │
│  │ TREE    │ │  │   takes ~70% of center height)   │  │  │   action; green=ready;  │  │
│  │  path   │ │  │  scrollable, color-coded rows    │  │  │   grey+reason=blocked)  │  │
│  │  scan   │ │  │                                  │  │  │  metadata pills         │  │
│  │  branch │ │  │                                  │  │  │  Title / Agent inputs   │  │
│  │  HEAD   │ │  └──────────────────────────────────┘  │  │  Notes textarea         │  │
│  │  dirty  │ │  ┌── QUICK MESSAGE ───────────────────┐ │  │  [CREATE SAFE HANDOFF] │  │
│  ├─────────┤ │  │  textarea + Save Message           │ │  │  [End Session]         │  │
│  │ USER 1  │ │  │  [ Start Session ] (40px, green)   │ │  └─────────────────────── ┘ │
│  │ identity│ │  └────────────────────────────────────┘ │  ┌── LAST PACKAGE ───────┐   │
│  │ Switch  │ │                                       │  │  (collapsible, r-only) │   │
│  ├─────────┤ │                                       │  └───────────────────────┘   │
│  │ USER 2  │ │                                       │                               │
│  │ identity│ │                                       │                               │
│  │ Switch  │ │                                       │                               │
│  └─────────┘ │                                       │                               │
├──────────────┴───────────────────────────────────────┴───────────────────────────────┤
│  FOOTER  (28px: Safety rules pill | No stash · No force push · No destructive git | Last backup: —)  │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Column proportions

| Zone | Width | Rationale |
|---|---|---|
| Left column | ~260–280px fixed | Setup + identity — compact, done once |
| Center panel | flex-grow (fills remaining) | Status messages must dominate |
| Right panel | ~340–360px fixed | Handoff action — needs room for metadata |

Minimum operational width: 860px.

---

## 4. Zone-by-Zone Specification

### 4.1 Header (42px)

**Left:** `PANDA Collaborator` (13px, weight 500, UI font) + thin `|` separator.

**Center-left:** Active user indicator — `● Darrin` where `●` is a 6px filled circle in the user's identity color (amber for User 1, cyan for User 2). Name in sentence case, 14px, weight 600, identity color text. NOT uppercase.

**Center:** Passive repo status pills (monospace, 11px): `main` branch · `a3f8c1` HEAD · `clean` / `dirty` / `unknown` state. Non-clickable chips only.

**Right:** `Start Test Mode` (28px, muted grammar) + `Setup Users` (28px, muted grammar) + `Emergency Pause` (28px, red/error grammar — always visible in header; single instance across the entire screen).

### 4.2 Workflow Rail (32px)

Five steps as a compact horizontal progress rail. Each step: 20px numbered dot + 2–3 word label. 8px chevron separators between steps.

| Step | Label | Dot color |
|---|---|---|
| 1 | Register | Green when complete; amber when setup needed |
| 2 | Confirm repo | Green when scanned; amber when not scanned |
| 3 | Hand over | Green when handover complete; amber when pending |
| 4 | Working | `#e8a87c` amber when User 1 active; `#4dd9e0` cyan when User 2 active; grey when session not started |
| 5 | Hand off | Green when handoff ready; grey otherwise |

No cards. No body copy. No border boxes. Rail only.

### 4.3 Left Column (~280px)

**Working Tree section** (top ~40%):

- Section header: `WORKING TREE` (peach-caps, 10px, muted)
- Repo path (monospace, 11px, middle-ellipsis) + `Browse` button (28px, right-aligned, muted grammar)
- `Scan Working Tree` button (full-width, 28px, `var(--ok)` = `#6da850` green when path set, grey when not)
- Status pills row: branch · 7-char SHA · dirty/clean/unknown · untracked count
- Last scan time (11px, monospace, muted) + scan error in amber text if applicable

**User 1 section** (middle ~30%):

- Section header: `USER 1` with 3px left border stripe in `#e8a87c`
- Display name (13px, weight 600, `#e8a87c` text)
- Registration status pill: `Registered` (green border) or `Setup needed` (amber border)
- Git identity: `name <email>` (11px, monospace, muted)
- **State B:** `Switch to Darrin` button (28px, full-width). Border: `1px solid #e8a87c` vivid when enabled (User 2 active); `1px solid rgba(232,168,124,0.25)` dim when disabled (User 1 already active). Background always `var(--pane-raised)` = `#22223a`. Identity color does NOT fill the button background.
- **State A:** `Register User 1` button replaces `Switch to Darrin` (same 28px grammar, opens setup modal)

**User 2 section** (bottom ~30%):

- Identical structure with `#4dd9e0` cyan as identity accent
- **State B:** `Switch to [User 2 Name]` button with cyan border; enabled when User 1 is active, disabled when User 2 active
- **State A:** `Register User 2` button replaces switch

**Identity rule:** Border stripe + display name = identity color. Button backgrounds = always dark `var(--pane-raised)`. Identity color never fills a button.

### 4.4 Center Panel (flex-grow — largest zone)

**Status Messages** (~70% of center height):

- Section header: `STATUS MESSAGES` + aggregate state chip at right (`Error` red / `Warning` amber / `OK` green)
- Scrollable list — single scrollbar on this container only; no nested scroll regions
- Each row: 4px left border color-coded by type:
  - Info: `#555577` · Success: `var(--ok)` green · Warning: `#f39c12` amber · Error: `#e74c3c` red · Waiting: dim + spinner
- Row content: message text (13px, UI font) + timestamp (11px, monospace, muted) + author chip
- Empty state: `No messages yet. Start a session to see activity.` (centered, muted)
- **This is the largest single surface on the screen**

**Quick Message** (~30% of center height):

- Section header: `QUICK MESSAGE`
- Textarea (3–4 lines visible): placeholder `Short note, concern, achievement, or next step`
- `Save Message` button (28px, full-width, green grammar)
- `Start Session` button (full-width, 40px, `var(--ok)` green when ready, grey + inline blocked-reason text when not)

### 4.5 Right Panel (~360px)

**Create Safe Handoff** (top ~60%):

- Section header: `CREATE SAFE HANDOFF`
- Passive metadata pills (stacked, monospace 11px):
  - `Root: C:\CODEX PG` (truncated) · `Branch: main` · `HEAD: a3f8c1`
  - `Protection: —` · `Patches: —` · `Files: —` · `Manifest: —`
- `Title` input (28px height, pre-filled: `AI workstation handoff`)
- `Agent` input (28px height, pre-filled: `Codex`)
- `Notes` textarea (3 lines): placeholder `Current intent, risks, next action`
- **`Create Safe Handoff` button** — full-width, 48px, `var(--ok)` = `#6da850` green when ready, grey with inline blocked-reason text when not. Dominant primary action.
- `End Session / Handoff` — full-width, 28px, amber border secondary grammar (below Create Safe Handoff)

**Last Package** (bottom ~40%, collapsible):

- `▶ LAST PACKAGE` when collapsed; `▼ LAST PACKAGE` when expanded (triangle rotates)
- Collapsed by default when no package exists; expanded when package present
- Expanded content: package ID (monospace 11px), created timestamp, source branch/HEAD, file count, patch count
- Action buttons (28px, muted secondary grammar, in a row): `Open Folder` · `Copy ID` · `View Manifest`
- No restore, apply, delete, or mutation controls

### 4.6 Footer (28px)

Full-width persistent bar. Emergency Pause does NOT appear here as a button — it is in the header only.

- Left: `Safety rules: Always enforced` (green border passive pill)
- Center: `No stash · No force push · No destructive git` (11px, monospace, muted)
- Right: `Last backup: —` (monospace, 11px, muted passive pill)

**When Emergency Pause is active:** footer expands to 40px, full red/error band — `⚠ EMERGENCY PAUSE ACTIVE — [reason] — [Clear Pause button]`. The `Clear Pause` button inside the footer is the only action in the footer and only appears in this state.

---

## 5. User Identity Color System

### 5.1 Key token values (all defined in Phase 0 `:root`)

| Token | Value | Use |
|---|---|---|
| `--user1` | `#e8a87c` | User 1 amber identity |
| `--user2` | `#4dd9e0` | User 2 cyan identity |
| `--ok` | `#6da850` | Enabled safe action green |
| `--pane-raised` | `#22223a` | Button backgrounds, raised surfaces |
| `--canvas` | `#14141f` | Deepest background |
| `--chrome` | `#161625` | Header/footer/rail background |
| `--pane` | `#1a1a2e` | Panel background |
| `--pane-2` | `#22223a` | Panel-within-panel background |
| `--warn` | `#f39c12` | Warning amber |
| `--err` | `#e74c3c` | Error/danger red |

### 5.2 Identity color application

| Element | User 1 | User 2 |
|---|---|---|
| Section header left border stripe | `#e8a87c` 3px | `#4dd9e0` 3px |
| Display name text | `#e8a87c` | `#4dd9e0` |
| Header active-user dot | `#e8a87c` filled | `#4dd9e0` filled |
| Workflow rail Step 4 dot | `#e8a87c` filled | `#4dd9e0` filled |
| Switch button border (enabled) | `1px solid #e8a87c` vivid | `1px solid #4dd9e0` vivid |
| Switch button border (disabled) | `1px solid rgba(232,168,124,0.25)` | `1px solid rgba(77,217,224,0.25)` |
| Switch button background | `var(--pane-raised)` dark | `var(--pane-raised)` dark |

### 5.3 What identity color never touches

- Button backgrounds (always dark `var(--pane-raised)`)
- Panel backgrounds
- The `Create Safe Handoff` button
- Status message row borders (semantic: info/success/warning/error)
- Workflow rail dots for steps 1–3 and 5 (semantic: green/amber/grey)

---

## 6. Three Mockup States

Radio toggle at the top of the HTML mockup:

`[● Setup needed]  [○ Operational]  [○ Emergency Pause]`

**State A — Setup needed:**
- Left: Both users show `Setup needed` amber pill + `Register User 1` / `Register User 2` buttons
- Center: Status Messages shows amber warning row: `⚠ Complete setup before starting a session.`; `Start Session` grey, reason: `Setup incomplete`
- Right: `Create Safe Handoff` grey, inline reason: `Setup incomplete — register both users and scan a repository`
- Workflow rail: Step 1 dot amber, all others grey

**State B — Operational:**
- Left: User 1 shows `Registered` green pill + `Darrin <darrin@example.com>` git identity + `Switch to Darrin` button (greyed, User 1 active). User 2 shows `Registered` + `Switch to Adam` button (enabled, cyan border).
- Center: Status Messages shows 4 sample rows — 1 info (session started), 1 success (repo scanned), 1 warning (dirty state), 1 error (mock fetch error). `Start Session` green.
- Right: `Create Safe Handoff` green, metadata pills populated with sample values. Notes textarea shows placeholder.
- Workflow rail: Steps 1–3 green dots, Step 4 amber dot (User 1 active), Step 5 grey dot.

**State C — Emergency Pause:**
- All of State B remains visible, plus:
- Footer expands to 40px red band: `⚠ EMERGENCY PAUSE ACTIVE — Darrin triggered pause at 14:22 — [Clear Pause button]`
- `Start Session` grey, reason: `Emergency Pause active`
- `Create Safe Handoff` grey, reason: `Emergency Pause active`
- Header `Emergency Pause` button: red filled, label `● Paused`

---

## 7. What the Mockup Must NOT Include

- No 5-equal-column card grid
- No panel headers taller than 28px
- No visible label truncation in any state
- No whitespace-heavy empty panel areas
- No uppercase or display-weight hero text for the active user name
- No status messages buried below the fold or in a narrow bottom strip
- No light, cream, or white panel backgrounds
- No linear-gradient button fills
- No identity-colored button backgrounds (amber/cyan fill = violation)
- No duplicate `Emergency Pause` button — header only; footer shows active state band only

---

## 8. Bible Compliance Checklist (CC must verify each before filing RTC)

- [ ] All surfaces use Bible dark tokens from §5.1 token table
- [ ] No font-size > 14px in chrome elements (header, rail, footer); body content max 13px
- [ ] Monospace ONLY for: paths, branch, SHA, timestamps, package IDs, counts
- [ ] All action buttons rectangular with `var(--radius-md)` ≈ 4px radius
- [ ] All passive status indicators are pill-shaped and non-clickable
- [ ] Green (`var(--ok)`) = enabled safe action only; grey = disabled; amber = warning; red = danger/emergency
- [ ] User 1 amber and User 2 cyan used as identity markers only (border, dot, name text)
- [ ] `Create Safe Handoff` is visually dominant — largest green element on the right panel
- [ ] `Emergency Pause` appears exactly once (header); active state shown in footer band only
- [ ] Status Messages is the largest single surface on the screen
- [ ] Zero page-level vertical scroll at 1366×768

---

## 9. Mockup Deliverables

Single HTML file, radio-button state switcher at top:

```
Output: C:\CODEX PG\CODEX PANDA Collaborator\mockups\pc_main_screen_v1\pc_main_screen_v1.html
States: [● Setup needed]  [○ Operational]  [○ Emergency Pause]
```

**Mockup only — zero production code changes:**
- ❌ `web/index.html` — do not touch
- ❌ `tests/test_panda_collaborator.py` — do not touch
- ❌ All other production files — do not touch

File RTC to CLAUDE inbox with browser path. Darrin approves before any implementation begins.

---

## 10. Open Items (not blocking the mockup)

- Exact collapsed height of Package Inspector when no package exists
- Whether `Start Session` button belongs in center panel (current spec) or right panel
- Whether Quick Message textarea should be above or below Status Messages
- Breakpoint stacking order at 940px
