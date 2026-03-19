# Dashboard Layout Consistency — Design Spec

**Date:** 2026-03-18
**Branch:** feat/hardware-abstraction-debug-mode

## Problem

After moving thresholds into per-metric card collapses and device modes into per-device card collapses, two elements were left inconsistent:

1. **Aux temperature sensors** (Sensor 1/2/3) live in a standalone `.sensors` section between the device row and the Controls panel. They feel orphaned — not visually associated with temperature.
2. **Controls panel** now only contains Fan Schedule. The `<details>` wrapper with the "⚙ Controls" summary is misleading overhead for a single form.

## Chosen Approach

**Option B:** Aux temps move into the Temp card; Controls panel replaced with a flat, always-visible Fan Schedule section.

## Changes

### 1. Aux Sensors → Temp Card

- Add a `<details class="threshold-details">` at the bottom of the Temperature metric card, after the existing Thresholds collapse.
- Summary text: "Aux Sensors"
- Body contains the existing S1/S2/S3 sensor bar rows (same markup, reusing `.sensor-row`, `.sensor-bar-track`, `.sensor-bar-fill`, `.sensor-value` classes).
- **Auto-open behaviour:** In `refresh()`, after updating the aux bars, set `auxDetails.open = hasAux` where `hasAux = t1 !== null || t2 !== null || t3 !== null`. This auto-expands when any aux value arrives and auto-collapses when all are null (e.g. after a debug state clear).
- Remove the standalone `.sensors` section from the HTML entirely.

### 2. Controls Panel → Flat Fan Schedule Section

- Remove the `<details class="controls-panel">` wrapper and `<div class="controls-body">` entirely.
- Replace with `<div class="schedule-section">` containing:
  - A `<div class="schedule-section-heading">Fan Schedule</div>` label.
  - The existing `#fan-schedule-form` and `.schedule-hint` unchanged.
- The section is always visible — no collapse.
- Style `.schedule-section` as a card: same `background: var(--surface)`, `border`, `border-radius`, `padding` as other cards, with `margin: 8px 16px`.

### 3. CSS Cleanup

Remove now-unused rules:
- `.controls-panel`
- `.controls-panel summary` and pseudo-elements
- `.controls-body`
- `.controls-section-heading`
- `.controls-divider`

Add:
- `.schedule-section` — card-style container for the fan schedule
- `.schedule-section-heading` — label styled like `.threshold-summary` (muted uppercase)

## Final Page Order

1. Navbar
2. Status row (Online badge + timestamp)
3. Metric cards: CO₂ · Temperature (with Thresholds + Aux Sensors collapses) · Humidity
4. Device cards: Heater · Fan · Humidifier (each with Mode collapse)
5. Fan Schedule section (always visible card)

## Out of Scope

- Debug value injection UI on the dashboard — injection is handled via `PUT /api/debug/state` curl calls, which already support `temperature_1`, `temperature_2`, `temperature_3`.
- Any changes to API, backend, or hardware drivers.
- Fan Schedule collapse behaviour — it becomes always-visible intentionally.

## Files Changed

| File | Change |
|------|--------|
| `src/static/index.html` | Move aux sensor rows into Temp card; remove `.sensors` section; replace controls panel with `.schedule-section` |
| `src/static/style.css` | Remove unused controls-panel rules; add `.schedule-section` and `.schedule-section-heading` |
