# Dashboard Layout Consistency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the dashboard layout consistent by moving aux temperature sensors inside the Temp card and replacing the Controls panel with a flat Fan Schedule card.

**Architecture:** Pure frontend changes to two files — `index.html` and `style.css`. No backend, API, or MicroPython changes. No automated test infrastructure exists for the dashboard; verification is visual via browser after `make flash`.

**Tech Stack:** HTML, CSS, vanilla JS served by Microdot on MicroPython ESP32.

---

## File Map

| File | Change |
|------|--------|
| `src/static/index.html` | Move aux sensor rows into Temp card collapse; remove `.sensors` section; replace controls panel with `.schedule-section` div; add JS auto-open logic |
| `src/static/style.css` | Remove 8 dead rule blocks; add `.schedule-section` and `.schedule-section-heading` |

---

### Task 1: Move aux sensors into the Temperature card

**Files:**
- Modify: `src/static/index.html`

The three aux sensor bar rows (`temp1-bar/value`, `temp2-bar/value`, `temp3-bar/value`) currently live in a standalone `.sensors` section. Move them into a `<details>` collapse inside the Temperature metric card, directly after the existing Thresholds collapse. Then remove the standalone section.

- [ ] **Step 1: Add the Aux Sensors collapse inside the Temp card**

In `src/static/index.html`, find the Temperature card. It ends with the closing `</details>` of the Thresholds collapse and then `</div>`. Insert the new collapse between those two:

```html
        <details class="threshold-details" id="aux-sensors-details">
          <summary class="threshold-summary">Aux Sensors</summary>
          <div class="sensor-row">
            <span class="sensor-label">Sensor 1</span>
            <div class="sensor-bar-track"><div class="sensor-bar-fill" id="temp1-bar"></div></div>
            <span class="sensor-value" id="temp1-value">--</span>
          </div>
          <div class="sensor-row">
            <span class="sensor-label">Sensor 2</span>
            <div class="sensor-bar-track"><div class="sensor-bar-fill" id="temp2-bar"></div></div>
            <span class="sensor-value" id="temp2-value">--</span>
          </div>
          <div class="sensor-row">
            <span class="sensor-label">Sensor 3</span>
            <div class="sensor-bar-track"><div class="sensor-bar-fill" id="temp3-bar"></div></div>
            <span class="sensor-value" id="temp3-value">--</span>
          </div>
        </details>
```

The `<details>` must NOT have the `open` attribute — it starts collapsed.

The old_string to match for the Edit tool (the closing of the Thresholds collapse and the card's closing div):

```html
        </details>
      </div>

      <!-- Humidity -->
```

Replace with:

```html
        </details>
        <details class="threshold-details" id="aux-sensors-details">
          <summary class="threshold-summary">Aux Sensors</summary>
          <div class="sensor-row">
            <span class="sensor-label">Sensor 1</span>
            <div class="sensor-bar-track"><div class="sensor-bar-fill" id="temp1-bar"></div></div>
            <span class="sensor-value" id="temp1-value">--</span>
          </div>
          <div class="sensor-row">
            <span class="sensor-label">Sensor 2</span>
            <div class="sensor-bar-track"><div class="sensor-bar-fill" id="temp2-bar"></div></div>
            <span class="sensor-value" id="temp2-value">--</span>
          </div>
          <div class="sensor-row">
            <span class="sensor-label">Sensor 3</span>
            <div class="sensor-bar-track"><div class="sensor-bar-fill" id="temp3-bar"></div></div>
            <span class="sensor-value" id="temp3-value">--</span>
          </div>
        </details>
      </div>

      <!-- Humidity -->
```

- [ ] **Step 2: Remove the standalone `.sensors` section**

Find and delete this entire block. Note: the `<!-- Secondary temperature sensors -->` comment must be included or it will be left as an orphan.

old_string (exact):
```html
    <!-- Secondary temperature sensors -->
    <div class="sensors">
      <div class="sensors-heading">Temp Sensors</div>
      <div class="sensor-row">
        <span class="sensor-label">Sensor 1</span>
        <div class="sensor-bar-track"><div class="sensor-bar-fill" id="temp1-bar"></div></div>
        <span class="sensor-value" id="temp1-value">--</span>
      </div>
      <div class="sensor-row">
        <span class="sensor-label">Sensor 2</span>
        <div class="sensor-bar-track"><div class="sensor-bar-fill" id="temp2-bar"></div></div>
        <span class="sensor-value" id="temp2-value">--</span>
      </div>
      <div class="sensor-row">
        <span class="sensor-label">Sensor 3</span>
        <div class="sensor-bar-track"><div class="sensor-bar-fill" id="temp3-bar"></div></div>
        <span class="sensor-value" id="temp3-value">--</span>
      </div>
    </div>

```

new_string: empty string (delete entirely, leaving no blank line gap).

- [ ] **Step 3: Add auto-open JS logic**

In the `refresh()` function, find the three aux `updateBar()` calls (around line 408-410):

```js
    updateBar(t1, tempMin, tempMax, 'temp1-bar', 'temp1-value', null, null, null);
    updateBar(t2, tempMin, tempMax, 'temp2-bar', 'temp2-value', null, null, null);
    updateBar(t3, tempMin, tempMax, 'temp3-bar', 'temp3-value', null, null, null);
```

Replace with:

```js
    updateBar(t1, tempMin, tempMax, 'temp1-bar', 'temp1-value', null, null, null);
    updateBar(t2, tempMin, tempMax, 'temp2-bar', 'temp2-value', null, null, null);
    updateBar(t3, tempMin, tempMax, 'temp3-bar', 'temp3-value', null, null, null);
    document.getElementById('aux-sensors-details').open = t1 !== null || t2 !== null || t3 !== null;
```

- [ ] **Step 4: Commit**

```bash
git add src/static/index.html
git commit -m "feat: move aux temp sensors into Temperature card collapse"
```

---

### Task 2: Replace Controls panel with flat Fan Schedule card

**Files:**
- Modify: `src/static/index.html`

The `<details class="controls-panel">` wraps a single Fan Schedule form. Remove the collapse and replace with a plain styled div.

- [ ] **Step 1: Replace the controls panel markup**

Find the entire controls panel block:

```html
    <!-- Controls panel -->
    <details class="controls-panel">
      <summary>⚙ Controls</summary>
      <div class="controls-body">

        <!-- Fan Schedule -->
        <div>
          <div class="controls-section-heading">Fan Schedule</div>
          <form id="fan-schedule-form">
            <div class="schedule-toggle-row">
              <input type="checkbox" id="fan-schedule-enabled">
              <label for="fan-schedule-enabled">Enable scheduled fan run</label>
            </div>
            <div class="schedule-inputs-row" id="fan-schedule-row">
              <span>Run for</span>
              <input type="number" id="fan-schedule-duration" min="1" step="1">
              <span>min every</span>
              <input type="number" id="fan-schedule-interval" min="1" step="1">
              <span>min</span>
            </div>
            <button type="submit" class="btn btn-primary">Save Schedule</button>
          </form>
          <div class="schedule-hint">Fan still runs if CO₂ exceeds threshold.</div>
        </div>

      </div>
    </details>
```

Replace with:

```html
    <!-- Fan Schedule -->
    <div class="schedule-section">
      <div class="schedule-section-heading">Fan Schedule</div>
      <form id="fan-schedule-form">
        <div class="schedule-toggle-row">
          <input type="checkbox" id="fan-schedule-enabled">
          <label for="fan-schedule-enabled">Enable scheduled fan run</label>
        </div>
        <div class="schedule-inputs-row" id="fan-schedule-row">
          <span>Run for</span>
          <input type="number" id="fan-schedule-duration" min="1" step="1">
          <span>min every</span>
          <input type="number" id="fan-schedule-interval" min="1" step="1">
          <span>min</span>
        </div>
        <button type="submit" class="btn btn-primary">Save Schedule</button>
      </form>
      <div class="schedule-hint">Fan still runs if CO₂ exceeds threshold.</div>
    </div>
```

- [ ] **Step 2: Commit**

```bash
git add src/static/index.html
git commit -m "feat: replace Controls panel collapse with flat Fan Schedule card"
```

---

### Task 3: CSS cleanup and new rules

**Files:**
- Modify: `src/static/style.css`

Remove all now-dead CSS rules and add the two new ones.

- [ ] **Step 1: Remove Secondary Sensors rules**

Remove only `.sensors` and `.sensors-heading`. Stop before `.sensor-row` — that rule is reused inside the Temp card collapse and must be kept.

old_string (exact):
```css
/* === Secondary Sensors === */

.sensors {
  padding: 4px 16px 8px 16px;
}

.sensors-heading {
  color: var(--text-dim);
  font-size: 0.65em;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

```

new_string: empty string (delete entirely).

- [ ] **Step 2: Remove Controls Panel rules**

old_string (exact, runs from the section comment through `.controls-divider`, ending just before `/* === Threshold Form === */`):

```css
/* === Controls Panel (details/summary) === */

.controls-panel {
  margin: 8px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.controls-panel summary {
  padding: 12px 16px;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 0.85em;
  font-weight: 600;
  list-style: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
}

.controls-panel summary::-webkit-details-marker { display: none; }
.controls-panel summary::marker { display: none; }

.controls-panel summary::after {
  content: "▼";
  font-size: 0.75em;
  color: var(--text-dim);
  transition: transform 0.2s;
}

.controls-panel[open] summary::after {
  transform: rotate(180deg);
}

.controls-body {
  background: var(--bg);
  border-top: 1px solid var(--border);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.controls-section-heading {
  color: var(--text-dim);
  font-size: 0.65em;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.controls-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 0;
}

```

new_string: empty string (delete entirely).

- [ ] **Step 3: Add new rules**

Steps 1 and 2 must be completed and saved before this step — they remove the Controls Panel block, leaving `.btn-inline`'s closing brace immediately before `/* === Threshold Form === */`. Use that gap as the anchor.

old_string (exact — note the two surrounding sections must already be deleted for this match to exist):
```css
  margin-left: auto;
}

/* === Threshold Form === */
```

new_string:
```css
  margin-left: auto;
}

/* === Fan Schedule Section === */

.schedule-section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  margin: 8px 16px;
}

.schedule-section-heading {
  color: var(--text-dim);
  font-size: 0.65em;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

/* === Threshold Form === */
```

- [ ] **Step 4: Commit**

```bash
git add src/static/style.css
git commit -m "style: remove dead controls-panel/sensors CSS; add schedule-section rules"
```

---

### Task 4: Visual verification

No automated test suite exists for the dashboard. Verify by flashing to the device and inspecting in a browser.

- [ ] **Step 1: Flash and restart**

```bash
make flash && make restart
```

Wait ~90 seconds for boot and WiFi.

- [ ] **Step 2: Open the dashboard**

```bash
open http://$DEVICE_IP/
```

Check each of the following:

| What | Expected |
|------|----------|
| Temp card | Shows "Thresholds ▼" and "Aux Sensors ▼" collapses |
| Aux Sensors collapse | Starts collapsed when no aux values present |
| Aux Sensors auto-open | Inject `temperature_1` via `PUT /api/debug/state` — collapse opens within 5s |
| Aux Sensors auto-close | `DELETE /api/debug/state` — collapse closes within 35s |
| Fan Schedule | Visible below device cards, no collapse, no "Controls" header |
| Fan Schedule save | Toggle enable, set duration/interval, save — persists across refresh |
| Old `.sensors` section | Gone — no "Temp Sensors" heading between devices and schedule |

- [ ] **Step 3: Inject aux values to test auto-open**

```bash
curl -X PUT http://$DEVICE_IP/api/debug/state \
  -H 'Content-Type: application/json' \
  -d '{"temperature_1": 21.5, "temperature_2": 22.0, "temperature_3": 20.8}'
```

Wait 5 seconds. The Aux Sensors collapse should open automatically.

```bash
curl -X DELETE http://$DEVICE_IP/api/debug/state
```

Wait up to 10 seconds. The dashboard polls every 5 seconds, so the next `refresh()` call will set `auxDetails.open = false`. The Aux Sensors collapse should close automatically.
