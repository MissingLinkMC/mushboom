# MushBoom UI Rewrite — Design Spec

**Date:** 2026-03-16
**Status:** Approved

## Goals

Modernize the look and feel of the MushBoom web UI (visual redesign) and improve usability on mobile devices (UX improvement). The backend API and Python source are unchanged.

## Architecture

**Approach:** Shared CSS + lean HTML pages (Option B).

A single `src/static/style.css` file provides the shared earthy theme. Each HTML page imports it via `<link rel="stylesheet" href="/style.css">` and contains only page-specific markup and JavaScript. This eliminates CSS duplication across pages and makes theme changes single-source.

### New files

| File | Purpose |
|------|---------|
| `src/static/style.css` | Shared earthy theme — colors, typography, navbar, cards, buttons, form inputs |
| `src/static/index.html` | Main dashboard — rewritten |
| `src/static/logs.html` | Logs page — rewritten |
| `src/static/memory.html` | Memory monitor — rewritten |

### Backend change

One new route added to `src/api.py`. The `content_type` kwarg must be specified so browsers apply the stylesheet correctly:

```python
@app.get("/style.css")
async def stylesheet(request):
    return send_file("/static/style.css", content_type="text/css")
```

No other backend changes. The existing template substitution in `index.html` (`USE_FAHRENHEIT`, `REMOTE_DASHBOARD_LINK`) is preserved as-is.

### Template substitution scope

Template substitution (`render_template`) is only applied to `index.html` (served via the `/` route). `logs.html` and `memory.html` are served via `send_file()` with no template processing — this is unchanged. Consequently, the `REMOTE_DASHBOARD_LINK` (ThingSpeak) navbar link is only present on `index.html`, as it is today. `logs.html` and `memory.html` do not show the Dashboard link.

## Visual Design

**Theme:** Earthy / Natural dark

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | `#1c1a14` | Page background |
| `--surface` | `#2a2518` | Card / panel background |
| `--border` | `#3d3420` | Card borders, dividers |
| `--bg-deep` | `#13110d` | Navbar background |
| `--text` | `#e8d9a8` | Primary text |
| `--text-muted` | `#9c8a5a` | Labels, secondary text |
| `--text-dim` | `#6b5f3a` | Threshold labels, dim info |
| `--amber` | `#d4a853` | Brand color, temperature metric color |
| `--green` | `#8fcb7a` | CO₂, online status, active state |
| `--green-bg` | `#3a5c2e` | Active/on badge backgrounds |
| `--blue` | `#7ab3e8` | Humidity metric color |
| `--blue-bg` | `#1e3a5a` | Blue badge backgrounds |

**Note on warning color:** `getBarColor()` returns hardcoded hex strings (`#27ae60`, `#f1c40f`, `#e74c3c`, `#3498db`) directly — these are not mapped to CSS variables. This is intentional: the function is pure JS logic and adding a CSS var → JS mapping layer would be unnecessary complexity.

**Typography:** `system-ui, sans-serif`. Mobile-first — designed for 390px viewport width, scales naturally wider.

**Page titles:** Each page's `<title>` tag is preserved as-is from the current implementation.

## Page Layouts

### Shared: Navigation bar

Top bar with `--bg-deep` background and bottom border. Left: `🍄 MushBoom` as a link to `/` (serves as the "Home" link — no separate "Home" text link). Right: "Logs" (`/logs.html`), "Memory" (`/memory.html`), and (on `index.html` only, via template substitution) "Dashboard ↗" to ThingSpeak when `THINGSPEAK_ENABLED` is true.

### index.html — Main Dashboard

**Layout reorganization from current:** The threshold On/Off inputs that currently appear below each metric bar are removed from the metric cards entirely. They are relocated into the Controls panel (section 5) → Thresholds sub-section. The current section order (metrics → ranges form → modes → schedule → icons) is replaced with the new order below.

**Section order:**

1. **Status row** — "● Online" green badge on the left; "Last update: [timestamp]" on the right (absolute locale string, updated on each poll cycle — preserves existing `id="timestamp"` behavior).

2. **Primary metrics** (3 cards, stacked vertically: CO₂, Temperature, Humidity)

   Each card contains:
   - Top row: metric label (uppercase, `--text-muted`) on left; value (large, colored) on right
   - Progress bar (8px tall) with colored fill and two threshold marker lines (on/off)
   - Status text row below bar: on/off threshold values on the ends, status word ("in range", "near threshold", etc.) centered

   Element IDs preserved: `co2-bar`, `co2-value`, `co2-on-indicator`, `co2-off-indicator`, `temp-bar`, `temp-value`, `temp-on-indicator`, `temp-off-indicator`, `rh-bar`, `rh-value`, `rh-on-indicator`, `rh-off-indicator`.

   **`getBarColor()` refactor:** The current implementation detects CO₂ by DOM-scraping `.metric-label` text, which breaks in the new markup. `getBarColor()` is updated to accept an explicit `metric` string parameter (`'co2'`, `'temp'`, `'rh'`, or `null`). Updated signature:

   ```js
   function getBarColor(val, onVal, offVal, metric)
   ```

   `updateBar()` gains a corresponding `metric` parameter:

   ```js
   function updateBar(val, min, max, barId, valueId, onVal, offVal, metric)
   ```

   Each `updateBar()` call in `refresh()` passes the metric name explicitly. Secondary sensor bars pass `null` (no status coloring).

   Color per metric: CO₂ value → `#8fcb7a`, Temperature value → `#d4a853`, Humidity value → `#7ab3e8`. Temperature respects `USE_FAHRENHEIT`.

3. **Device status row** — 3 equal cards side by side (Heater, Fan, Humidifier).

   Each card: device SVG icon + status label div. Status label text is `"ON"` (green) when active, `"OFF"` (dim) when inactive.

   The existing JS drives icon coloring via `deviceDiv.classList.toggle('active', device.on)`. `style.css` must include analogous `.device.active` rules for each device icon so the unchanged JS continues to work:

   ```css
   .device svg { color: var(--text-dim); }
   .device.active #heater-svg { color: #e74c3c; }
   .device.active #fan-svg { color: var(--green); }
   .device.active #humidifier-svg { color: var(--blue); }
   ```

   SVG element IDs preserved: `heater-svg`, `fan-svg`, `humidifier-svg`.

4. **Secondary temperature sensors** — compact section with muted heading "Temp Sensors". Each of Sensor 1/2/3 shown as a single row: label + thin 5px bar + value. Uses `--text-dim` color throughout. Element IDs preserved: `temp1-bar`, `temp1-value`, `temp2-bar`, `temp2-value`, `temp3-bar`, `temp3-value`. Bar fill uses `#6b5f3a` (no status coloring; `metric` = `null` passed to `updateBar`).

5. **Controls panel** — uses native HTML `<details>`/`<summary>` for collapse behavior (no custom JS needed). Collapsed by default. Summary text: "⚙ Controls". Expanded body contains three sub-sections separated by `<hr>` dividers:

   - **Thresholds** — one row per metric (CO₂, Temp, Humidity): metric label, "On" `<input type="number">`, "Off" `<input type="number">`, unit label. Input element IDs preserved: `co2-on`, `co2-off`, `temp-on`, `temp-off`, `rh-on`, `rh-off`. Single "Save Thresholds" `<button type="submit">` submits `range-form` (`id="range-form"`). Inputs are not overwritten while focused (existing `inputState` focus-tracking logic preserved).
   - **Device Modes** — one row per device (Heater, Fan, Humidifier): device label on left, ON/AUTO/OFF segmented button group on right. Active mode highlighted: ON → green, AUTO → blue, OFF → dim. Clicking fires `PUT /api/modes` immediately — no save button. Existing `.toggle-group`, `data-device`, `data-mode` structure preserved so `setupModeToggles()` and `loadModes()` work without change.
   - **Fan Schedule** — enable checkbox (`id="fan-schedule-enabled"`), "Run for X min every Y min" inputs (`id="fan-schedule-duration"`, `id="fan-schedule-interval"`), "Save Schedule" button submits `fan-schedule-form` (`id="fan-schedule-form"`). Inputs disabled when checkbox unchecked. Hint text: "Fan still runs if CO₂ exceeds threshold." Existing `setFanScheduleInputs()` / `loadFanScheduleForm()` logic preserved.

### logs.html

Same earthy theme and navbar (without Dashboard link). Sections (matching current structure, visual rewrite only):
- Heading: "Log Files"
- Refresh controls row: single "Refresh Now" button
- App log section: heading "Application Log", `<pre id="app-log">` block
- Error log section: heading "Error Log", `<pre id="error-log">` block

Existing JS (`fetchLogs()`, `refreshLogs()`) preserved unchanged.

### memory.html

Same earthy theme and navbar (without Dashboard link). Sections (matching current structure, visual rewrite only):
- Heading: "Memory Usage Monitor"
- Stats grid: 4 cards — Current Usage, Maximum Usage, Since Startup, Trend
- "Refresh Data" button
- "Last updated: [timestamp]" line

Existing JS (`fetchData()`, 60-second `setInterval`) preserved unchanged. Element IDs preserved: `current-percent`, `current-used`, `current-total`, `max-percent`, `max-time`, `change-since-startup`, `startup-percent`, `trend`, `trend-details`, `last-update`.

## Data / API Contract

No changes to any API endpoints or payloads. All existing JavaScript logic (polling, color computation, unit conversion, form submission, mode toggles) is preserved and adapted to the new markup structure, with one exception: `getBarColor()` is updated to accept an explicit `metric` parameter instead of DOM-scraping for CO₂ detection, and `updateBar()` gains the corresponding parameter.

Poll interval remains 5 seconds.

## Out of Scope

- No new API endpoints
- No new features or data displayed
- No JavaScript framework or build tooling
- No changes to Python backend beyond the single new `style.css` route
