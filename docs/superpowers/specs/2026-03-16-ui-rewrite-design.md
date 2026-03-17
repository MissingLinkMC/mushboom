# MushBoom UI Rewrite — Design Spec

**Date:** 2026-03-16
**Status:** Approved

## Goals

Modernize the look and feel of the MushBoom web UI (visual redesign) and improve usability on mobile devices (UX improvement). The backend API and Python source are unchanged.

## Architecture

**Approach:** Shared CSS + lean HTML pages (Option B).

A single `src/static/style.css` file provides the shared earthy theme. Each HTML page imports it and contains only page-specific markup and JavaScript. This eliminates CSS duplication across pages and makes theme changes single-source.

### New files

| File | Purpose |
|------|---------|
| `src/static/style.css` | Shared earthy theme — colors, typography, navbar, cards, buttons, form inputs |
| `src/static/index.html` | Main dashboard — rewritten |
| `src/static/logs.html` | Logs page — rewritten |
| `src/static/memory.html` | Memory monitor — rewritten |

### Backend change

One new route added to `src/api.py`:

```python
@app.get("/style.css")
async def stylesheet(request):
    return send_file("/static/style.css")
```

No other backend changes. The existing template substitution in `index.html` (`USE_FAHRENHEIT`, `REMOTE_DASHBOARD_LINK`) is preserved as-is.

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
| `--amber` | `#d4a853` | Brand color, temperature |
| `--green` | `#8fcb7a` | CO₂, online status, active |
| `--green-bg` | `#3a5c2e` | Active/on badge backgrounds |
| `--blue` | `#7ab3e8` | Humidity |
| `--blue-bg` | `#1e3a5a` | Blue badge backgrounds |

**Typography:** `system-ui, sans-serif`. Mobile-first — designed for 390px viewport width, scales naturally wider.

## Page Layouts

### Shared: Navigation bar

Fixed top bar with `--bg-deep` background and bottom border. Left: `🍄 MushBoom` in amber. Right: text links to Logs, Memory, and (conditionally) Dashboard ↗ to ThingSpeak. The Dashboard link is rendered only when `THINGSPEAK_ENABLED` is true, identical to the existing template substitution mechanism.

### index.html — Main Dashboard

Sections in order (single scrolling page, no tabs):

1. **Status row** — "● Online" green badge on the left, "Updated Xs ago" dim timestamp on the right. Refreshed on every poll cycle.

2. **Primary metrics** (3 cards, stacked vertically)
   - CO₂, Temperature, Humidity
   - Each card: metric label (uppercase, muted) + value (large, colored) on top row; colored progress bar with two threshold marker lines (on/off) below; status text ("in range", "near threshold", etc.) centered under bar
   - Bar color follows the existing `getBarColor()` logic: green = in range, amber = warning, red = out of range, blue = well below
   - Temperature respects `USE_FAHRENHEIT` config flag

3. **Device status row** — 3 equal cards side by side (Heater, Fan, Humidifier). Each shows the device SVG icon, "ON" (green) or "OFF" (dim) label. Icon is full-color when active, desaturated/dimmed when off.

4. **Secondary temperature sensors** — compact section with muted heading "Temp Sensors". Each of Sensor 1/2/3 shown as a single row: label + thin 5px bar + value. Uses `--text-dim` color throughout — visually subordinate to primary metrics.

5. **Controls panel** — collapsible `<details>`/`<summary>` (or JS toggle). Collapsed by default showing "⚙ Controls ▼". Expanded reveals three sub-sections separated by dividers:
   - **Thresholds** — inline row per metric (CO₂, Temp, Humidity): label, On input, Off input, unit. Single "Save Thresholds" button below. Identical PUT /api/ranges payload as today.
   - **Device Modes** — one row per device (Heater, Fan, Humidifier): label on left, ON/AUTO/OFF segmented button group on right. Active mode highlighted (green=ON, blue=AUTO, dim=OFF). Immediate PUT /api/modes on click, no save button needed.
   - **Fan Schedule** — enable checkbox, inline "Run for X min every Y min" inputs (disabled when unchecked), "Save Schedule" button. PUT /api/fan-schedule payload unchanged.

### logs.html

Same earthy theme and navbar. Functional content unchanged — log file viewer with refresh controls. Rewrite is visual only.

### memory.html

Same earthy theme and navbar. Functional content unchanged — memory usage display. Rewrite is visual only.

## Data / API Contract

No changes to any API endpoints or payloads. The rewrite is purely frontend. All existing JavaScript logic (polling, color computation, unit conversion, form submission, mode toggles) is preserved and adapted to the new markup structure.

Poll interval remains 5 seconds.

## Out of Scope

- No new API endpoints
- No new features or data displayed
- No JavaScript framework or build tooling
- No changes to Python backend beyond the single new `style.css` route
