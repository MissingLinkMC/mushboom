# Dashboard Layout Consistency — Design Spec

**Date:** 2026-03-18
**Branch:** feat/hardware-abstraction-debug-mode

## Problem

After moving thresholds into per-metric card collapses and device modes into per-device card collapses, two elements were left inconsistent:

1. **Aux temperature sensors** (Sensor 1/2/3) live in a standalone `.sensors` section between the device row and the Controls panel. They feel orphaned — not visually associated with temperature.
2. **Controls panel** now only contains Fan Schedule. The `<details>` wrapper with the "⚙ Controls" summary is misleading overhead for a single form.

## Chosen Approach

**Option B:** Aux temps move into the Temp card; Controls panel replaced with a flat, always-visible Fan Schedule card.

## Changes

### 1. Aux Sensors → Temp Card

Add a `<details class="threshold-details" id="aux-sensors-details">` at the bottom of the Temperature metric card, after the existing Thresholds collapse. Do **not** include the `open` attribute in the HTML — it starts collapsed.

- Summary: `<summary class="threshold-summary">Aux Sensors</summary>`
- Body contains the existing S1/S2/S3 sensor bar rows, reusing `.sensor-row`, `.sensor-bar-track`, `.sensor-bar-fill`, `.sensor-value` classes unchanged. The `id` attributes (`temp1-bar`, `temp1-value`, etc.) are preserved — only the containing element moves.
- The existing `updateBar()` calls for aux sensors remain unchanged: no threshold indicators, no color coding, same `tempMin`/`tempMax` scale.

**Auto-open behaviour:** Inside the `try` block in `refresh()`, after the three aux `updateBar()` calls, add:

```js
const auxDetails = document.getElementById('aux-sensors-details');
const hasAux = t1 !== null || t2 !== null || t3 !== null;
auxDetails.open = hasAux;
```

This auto-expands when any aux value is non-null and auto-collapses when all are null (e.g. after a debug state clear).

Remove the standalone `.sensors` section from the HTML entirely.

### 2. Controls Panel → Flat Fan Schedule Card

Remove the `<details class="controls-panel">` wrapper and `<div class="controls-body">` entirely. Replace with:

```html
<div class="schedule-section">
  <div class="schedule-section-heading">Fan Schedule</div>
  <!-- existing #fan-schedule-form unchanged -->
  <!-- existing .schedule-hint unchanged -->
</div>
```

The section is always visible — no collapse.

`.schedule-section` is styled as a card matching the metric and device cards:
- `background: var(--surface)` — this is intentionally the same flat surface as all other cards, replacing the previous two-tone look (controls body used `var(--bg)`, darker than `var(--surface)`).
- `border: 1px solid var(--border)`
- `border-radius: 8px`
- `padding: 12px`
- `margin: 8px 16px`

`.schedule-section-heading` matches `.threshold-details summary` styling: `color: var(--text-dim)`, `font-size: 0.65em`, `text-transform: uppercase`, `letter-spacing: 0.5px`, `margin-bottom: 8px`.

### 3. CSS Cleanup

Remove now-unused rules:
- `.controls-panel` and all sub-rules (summary, pseudo-elements, `[open]` variant)
- `.controls-body`
- `.controls-section-heading`
- `.controls-divider` (already a dead rule — no `<hr class="controls-divider">` remains in the HTML)
- `.sensors` and `.sensors-heading` (become dead once the `.sensors` section is removed from HTML)

Add:
- `.schedule-section`
- `.schedule-section-heading`

## Final Page Order

1. Navbar
2. Status row (Online badge + timestamp)
3. Metric cards: CO₂ · Temperature (with Thresholds collapse + Aux Sensors collapse) · Humidity
4. Device cards: Heater · Fan · Humidifier (each with Mode collapse)
5. Fan Schedule card (always visible)

## Out of Scope

- Debug value injection UI on the dashboard — injection is handled via `PUT /api/debug/state` curl calls, which already support `temperature_1`, `temperature_2`, `temperature_3`.
- Any changes to API, backend, or hardware drivers.

## Files Changed

| File | Change |
|------|--------|
| `src/static/index.html` | Move aux sensor rows into Temp card `<details>`; remove `.sensors` section; replace controls panel with `.schedule-section` div |
| `src/static/style.css` | Remove unused rules (controls-panel, controls-body, controls-section-heading, controls-divider, sensors, sensors-heading); add `.schedule-section` and `.schedule-section-heading` |
