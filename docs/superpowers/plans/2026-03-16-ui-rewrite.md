# UI Rewrite Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the MushBoom web UI with an earthy dark theme and a shared CSS file, improving visual quality and mobile usability without changing any backend API or behavior.

**Architecture:** A single `style.css` serves as the shared theme (CSS variables, base styles, shared components). Each HTML page imports it and provides only page-specific markup and JS. All existing JavaScript logic and element IDs are preserved so behavior is unchanged.

**Tech Stack:** Vanilla HTML/CSS/JS, Microdot (Python static file serving), MicroPython/ESP32 target

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `src/api.py` | Modify | Add `/style.css` route |
| `src/static/style.css` | Create | Shared earthy theme: CSS vars, reset, navbar, cards, bars, buttons, inputs, forms |
| `src/static/index.html` | Rewrite | Main dashboard: metrics, device status, controls panel |
| `src/static/logs.html` | Rewrite | Log viewer — visual rewrite only |
| `src/static/memory.html` | Rewrite | Memory monitor — visual rewrite only |

---

## Chunk 1: Foundation — API route + style.css

### Task 1: Add `/style.css` route to `api.py`

**Files:**
- Modify: `src/api.py`
- Test: `tests/test_api_static.py` (create)

- [ ] **Step 1: Write a failing test for the new route**

Create `tests/test_api_static.py`:

```python
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_style_css_route_exists_in_api():
    """The /style.css route must be registered in api.py."""
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'api.py')) as f:
        source = f.read()
    assert '@app.get("/style.css")' in source, "Missing /style.css route in api.py"

def test_style_css_uses_correct_content_type():
    """The route must specify content_type='text/css'."""
    with open(os.path.join(os.path.dirname(__file__), '..', 'src', 'api.py')) as f:
        source = f.read()
    assert 'content_type="text/css"' in source, "Missing content_type='text/css' in style.css route"

def test_style_css_file_exists():
    """The actual CSS file must exist at the expected static path."""
    css_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'static', 'style.css')
    assert os.path.exists(css_path), f"style.css not found at {css_path}"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
uv run pytest tests/test_api_static.py -v
```

Expected: 3 failures — route not registered, content_type missing, file doesn't exist.

- [ ] **Step 3: Add the route to `src/api.py`**

In `src/api.py`, add after the existing `@app.get("/site.webmanifest")` route block (around line 63):

```python
@app.get("/style.css")
async def stylesheet(request):
    return send_file("/static/style.css", content_type="text/css")
```

- [ ] **Step 4: Run tests — expect 2 pass, 1 fail** (file doesn't exist yet)

```bash
uv run pytest tests/test_api_static.py -v
```

Expected: `test_style_css_route_exists_in_api` PASS, `test_style_css_uses_correct_content_type` PASS, `test_style_css_file_exists` FAIL.

- [ ] **Step 5: Commit the route change**

```bash
git add src/api.py tests/test_api_static.py
git commit -m "feat: add /style.css static route to api"
```

---

### Task 2: Create `src/static/style.css`

**Files:**
- Create: `src/static/style.css`

- [ ] **Step 1: Create the CSS file with full earthy theme**

Create `src/static/style.css`:

```css
/* ============================================================
   MushBoom — Shared Earthy Theme
   ============================================================ */

:root {
  --bg:        #1c1a14;
  --surface:   #2a2518;
  --border:    #3d3420;
  --bg-deep:   #13110d;
  --text:      #e8d9a8;
  --text-muted:#9c8a5a;
  --text-dim:  #6b5f3a;
  --amber:     #d4a853;
  --green:     #8fcb7a;
  --green-bg:  #3a5c2e;
  --blue:      #7ab3e8;
  --blue-bg:   #1e3a5a;
  --red:       #e74c3c;
}

/* === Reset / Base === */

*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text);
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 16px;
  line-height: 1.4;
}

a {
  color: var(--text-muted);
  text-decoration: none;
  font-weight: 600;
}

a:hover {
  color: var(--amber);
}

h1, h2, h3 {
  margin: 0 0 0.5em 0;
  color: var(--text);
}

/* === Layout === */

.page {
  max-width: 480px;
  margin: 0 auto;
  padding: 0 0 32px 0;
}

.page-wide {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 16px 32px 16px;
}

/* === Navbar === */

.navbar {
  background: var(--bg-deep);
  border-bottom: 1px solid var(--border);
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
}

.navbar-brand {
  color: var(--amber);
  font-weight: 700;
  font-size: 1em;
  letter-spacing: 1px;
  text-decoration: none;
}

.navbar-brand:hover {
  color: var(--amber);
}

.navbar-links {
  display: flex;
  gap: 16px;
  align-items: center;
}

.navbar-links a {
  color: var(--text-muted);
  font-size: 0.85em;
}

.navbar-links a.external {
  color: var(--amber);
}

/* === Cards === */

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
}

/* === Status Badge === */

.badge-online {
  background: var(--green-bg);
  color: var(--green);
  border-radius: 4px;
  padding: 3px 10px;
  font-size: 0.75em;
  font-weight: 600;
}

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px 8px 16px;
}

.timestamp {
  color: var(--text-dim);
  font-size: 0.7em;
}

/* === Metric Cards === */

.metrics {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 8px 16px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 6px;
}

.metric-label {
  color: var(--text-muted);
  font-size: 0.7em;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.metric-value {
  font-size: 1.4em;
  font-weight: 700;
}

.metric-unit {
  font-size: 0.5em;
  color: var(--text-muted);
  margin-left: 2px;
}

/* === Progress Bar === */

.bar-track {
  background: var(--bg);
  border-radius: 3px;
  height: 8px;
  position: relative;
  overflow: visible;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  width: 0%;
  transition: width 0.5s, background 0.5s;
}

.bar-indicator {
  position: absolute;
  top: -4px;
  width: 2px;
  height: 16px;
  border-radius: 1px;
  opacity: 0.7;
  pointer-events: none;
  transition: left 0.5s;
}

.bar-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}

.bar-threshold {
  color: var(--text-dim);
  font-size: 0.6em;
}

.bar-status {
  font-size: 0.6em;
  color: var(--text-muted);
}

/* === Device Status Row === */

.devices {
  display: flex;
  gap: 8px;
  padding: 8px 16px;
}

.device {
  flex: 1;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px;
  text-align: center;
}

.device svg {
  width: 2.4em;
  height: 2.4em;
  fill: currentColor;
  color: var(--text-dim);
  transition: color 0.3s;
  overflow: hidden;
}

.device.active #heater-svg { color: #e74c3c; }
.device.active #fan-svg    { color: var(--green); }
.device.active #humidifier-svg { color: var(--blue); }

.device-status {
  font-size: 0.65em;
  font-weight: 700;
  margin-top: 3px;
  color: var(--text-dim);
}

.device.active .device-status {
  color: var(--green);
}

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

.sensor-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.sensor-label {
  color: var(--text-dim);
  font-size: 0.65em;
  min-width: 56px;
}

.sensor-bar-track {
  flex: 1;
  background: var(--bg);
  border-radius: 2px;
  height: 5px;
}

.sensor-bar-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--text-dim);
  transition: width 0.5s;
}

.sensor-value {
  color: var(--text-dim);
  font-size: 0.7em;
  min-width: 40px;
  text-align: right;
}

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

/* === Threshold Form === */

.threshold-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.threshold-metric-label {
  color: var(--text-muted);
  font-size: 0.75em;
  min-width: 72px;
}

.threshold-sublabel {
  color: var(--text-dim);
  font-size: 0.7em;
}

.threshold-unit {
  color: var(--text-dim);
  font-size: 0.65em;
}

/* === Inputs === */

input[type="number"],
input[type="text"],
input[type="time"] {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text);
  padding: 4px 6px;
  font-size: 0.8em;
  width: 64px;
}

input:focus {
  outline: 1px solid var(--amber);
  border-color: var(--amber);
}

input:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* === Buttons === */

.btn {
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8em;
  font-weight: 600;
  padding: 8px 16px;
  transition: opacity 0.15s;
}

.btn:hover { opacity: 0.85; }

.btn-primary {
  background: var(--green-bg);
  color: var(--green);
  width: 100%;
  margin-top: 10px;
}

.btn-refresh {
  background: var(--blue-bg);
  color: var(--blue);
}

/* === Toggle Group (mode buttons) === */

.mode-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.mode-label {
  color: var(--text-muted);
  font-size: 0.8em;
}

.toggle-group {
  display: flex;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--border);
}

.toggle-btn {
  flex: 1;
  background: var(--surface);
  color: var(--text-dim);
  border: none;
  border-right: 1px solid var(--border);
  padding: 5px 10px;
  font-size: 0.7em;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.toggle-btn:last-child {
  border-right: none;
}

.toggle-btn.active[data-mode="on"]   { background: var(--green-bg); color: var(--green);  font-weight: 700; }
.toggle-btn.active[data-mode="auto"] { background: var(--blue-bg);  color: var(--blue);   font-weight: 700; }
.toggle-btn.active[data-mode="off"]  { background: var(--surface);  color: var(--text-dim); font-weight: 700; }

/* === Fan Schedule === */

.schedule-toggle-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.schedule-toggle-row label {
  color: var(--text-muted);
  font-size: 0.8em;
  cursor: pointer;
}

.schedule-inputs-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  font-size: 0.8em;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.schedule-inputs-row input {
  width: 52px;
}

.schedule-hint {
  color: var(--text-dim);
  font-size: 0.65em;
  margin-top: 8px;
}

/* === Checkbox === */

input[type="checkbox"] {
  width: auto;
  accent-color: var(--green);
}

/* === Log / Memory pages === */

.page-heading {
  padding: 20px 16px 8px 16px;
  font-size: 1.2em;
  font-weight: 700;
}

.refresh-bar {
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.log-section {
  padding: 0 16px;
  margin-bottom: 32px;
}

.log-section h2 {
  font-size: 0.9em;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

pre {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 14px;
  overflow-x: auto;
  max-height: 500px;
  font-size: 0.8em;
  line-height: 1.5;
  color: var(--text-muted);
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
  padding: 8px 16px;
}

.stat-value {
  font-size: 1.6em;
  font-weight: 700;
  color: var(--text);
}

.stat-value.good    { color: var(--green); }
.stat-value.warning { color: var(--amber); }
.stat-value.danger  { color: var(--red); }

.stat-title {
  color: var(--text-muted);
  font-size: 0.75em;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 6px;
}

.stat-details {
  color: var(--text-dim);
  font-size: 0.75em;
  margin-top: 4px;
}

.last-updated {
  color: var(--text-dim);
  font-size: 0.7em;
  padding: 8px 16px 0 16px;
}
```

- [ ] **Step 2: Run the third test to confirm it now passes**

```bash
uv run pytest tests/test_api_static.py -v
```

Expected: all 3 PASS.

- [ ] **Step 3: Run the full test suite to confirm no regressions**

```bash
uv run pytest -v
```

Expected: all existing tests still PASS.

- [ ] **Step 4: Commit**

```bash
git add src/static/style.css
git commit -m "feat: add shared earthy theme style.css"
```

---

## Chunk 2: index.html Rewrite

### Task 3: Rewrite `src/static/index.html`

**Files:**
- Rewrite: `src/static/index.html`

The rewrite must:
- Import `style.css`
- Preserve all element IDs (JS compatibility)
- Reorganize sections: status → metrics → devices → sensors → controls panel
- Move threshold inputs into the `<details>` controls panel
- Refactor `getBarColor()` to accept explicit `metric` parameter
- Update `updateBar()` signature to pass `metric` through

- [ ] **Step 1: Rewrite `src/static/index.html`**

Replace the entire file with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MushBoom Status 🍄💥</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="stylesheet" href="/style.css">
</head>
<body>

  <!-- Navbar -->
  <nav class="navbar">
    <a class="navbar-brand" href="/">🍄 MushBoom</a>
    <div class="navbar-links">
      <a href="/logs.html">Logs</a>
      <a href="/memory.html">Memory</a>
      {{REMOTE_DASHBOARD_LINK}}
    </div>
  </nav>

  <div class="page">

    <!-- Status row -->
    <div class="status-row">
      <span class="badge-online">● Online</span>
      <span class="timestamp" id="timestamp"></span>
    </div>

    <!-- Primary metrics -->
    <div class="metrics" id="metrics">

      <!-- CO₂ -->
      <div class="card">
        <div class="metric-header">
          <span class="metric-label">CO₂</span>
          <span class="metric-value" id="co2-value" style="color:#8fcb7a;">-- <span class="metric-unit">ppm</span></span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" id="co2-bar"></div>
          <div class="bar-indicator" id="co2-on-indicator"  style="background:var(--amber);"></div>
          <div class="bar-indicator" id="co2-off-indicator" style="background:var(--text-dim);"></div>
        </div>
        <div class="bar-footer">
          <span class="bar-threshold">on: <span id="co2-on-label">--</span></span>
          <span class="bar-status" id="co2-status"></span>
          <span class="bar-threshold">off: <span id="co2-off-label">--</span></span>
        </div>
      </div>

      <!-- Temperature -->
      <div class="card">
        <div class="metric-header">
          <span class="metric-label" id="temp-label">Temperature (°C)</span>
          <span class="metric-value" id="temp-value" style="color:#d4a853;">-- <span class="metric-unit" id="temp-unit">°C</span></span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" id="temp-bar"></div>
          <div class="bar-indicator" id="temp-on-indicator"  style="background:var(--amber);"></div>
          <div class="bar-indicator" id="temp-off-indicator" style="background:var(--text-dim);"></div>
        </div>
        <div class="bar-footer">
          <span class="bar-threshold">on: <span id="temp-on-label">--</span></span>
          <span class="bar-status" id="temp-status"></span>
          <span class="bar-threshold">off: <span id="temp-off-label">--</span></span>
        </div>
      </div>

      <!-- Humidity -->
      <div class="card">
        <div class="metric-header">
          <span class="metric-label">Humidity</span>
          <span class="metric-value" id="rh-value" style="color:#7ab3e8;">-- <span class="metric-unit">%RH</span></span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" id="rh-bar"></div>
          <div class="bar-indicator" id="rh-on-indicator"  style="background:var(--amber);"></div>
          <div class="bar-indicator" id="rh-off-indicator" style="background:var(--text-dim);"></div>
        </div>
        <div class="bar-footer">
          <span class="bar-threshold">on: <span id="rh-on-label">--</span></span>
          <span class="bar-status" id="rh-status"></span>
          <span class="bar-threshold">off: <span id="rh-off-label">--</span></span>
        </div>
      </div>

    </div><!-- /metrics -->

    <!-- Device status row -->
    <div class="devices" id="devices">
      <div class="device" id="heater-device">
        <svg id="heater-svg" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path d="M293.612329 280.116994c-6.824615 10.236922-3.412307 20.473844 3.412307 23.886152 3.412307 3.412307 6.824615 3.412307 10.236922 3.412307 6.824615 0 10.236922-3.412307 13.649229-6.824615 40.947688-61.421533 20.473844-109.193836 0-150.141524-17.061537-40.947688-34.123074-75.070762 0-122.843065 6.824615-6.824615 3.412307-17.061537-3.412307-23.886152-10.236922-6.824615-20.473844-3.412307-23.886151 3.412308-44.359996 64.83384-20.473844 112.606143-3.412308 156.966139 20.473844 40.947688 34.123074 71.658455 3.412308 116.01845zM464.227697 280.116994c-6.824615 6.824615-3.412307 17.061537 3.412307 23.886152 3.412307 3.412307 6.824615 3.412307 10.236922 3.412307 6.824615 0 10.236922-3.412307 13.64923-6.824615 40.947688-61.421533 20.473844-109.193836 0-150.141524-17.061537-40.947688-34.123074-75.070762 0-122.843065 6.824615-6.824615 3.412307-17.061537-3.412308-23.886152-10.236922-6.824615-20.473844-3.412307-23.886151 3.412308-40.947688 64.83384-20.473844 112.606143-3.412307 156.966139 20.473844 40.947688 34.123074 71.658455 3.412307 116.01845zM634.843065 280.116994c-6.824615 6.824615-3.412307 17.061537 3.412308 23.886152 3.412307 3.412307 6.824615 3.412307 10.236922 3.412307 6.824615 0 10.236922-3.412307 13.649229-6.824615 40.947688-61.421533 20.473844-109.193836 0-150.141524-17.061537-40.947688-34.123074-75.070762 0-122.843065 6.824615-6.824615 3.412307-17.061537-3.412307-23.886152-10.236922-6.824615-20.473844-3.412307-23.886152 3.412308-40.947688 64.83384-20.473844 112.606143-3.412307 156.966139 20.473844 40.947688 34.123074 71.658455 3.412307 116.01845zM904.415347 341.538527h-784.830694c-58.009225 0-102.369221 44.359996-102.369221 102.369221v375.35381c0 58.009225 44.359996 102.369221 102.369221 102.369221h68.246147v85.307684c0 10.236922 6.824615 17.061537 17.061537 17.061537s17.061537-6.824615 17.061537-17.061537V921.630779h545.969178v85.307684c0 10.236922 6.824615 17.061537 17.061537 17.061537s17.061537-6.824615 17.061537-17.061537V921.630779h102.369221c58.009225 0 102.369221-44.359996 102.369221-102.369221V443.907748c0-58.009225-44.359996-102.369221-102.369221-102.369221zM170.769263 853.384632c-10.236922 0-17.061537-6.824615-17.061536-17.061537v-409.476884c0-10.236922 6.824615-17.061537 17.061536-17.061537s17.061537 6.824615 17.061537 17.061537v409.476884c0 10.236922-6.824615 17.061537-17.061537 17.061537z m153.553832-17.061537c0 10.236922-6.824615 17.061537-17.061537 17.061537s-17.061537-6.824615-17.061537-17.061537v-409.476884c0-10.236922 6.824615-17.061537 17.061537-17.061537s17.061537 6.824615 17.061537 17.061537v409.476884z m136.492295 0c0 10.236922-6.824615 17.061537-17.061537 17.061537s-17.061537-6.824615-17.061537-17.061537v-409.476884c0-10.236922 6.824615-17.061537 17.061537-17.061537s17.061537 6.824615 17.061537 17.061537v409.476884z m136.492294 0c0 10.236922-6.824615 17.061537-17.061537 17.061537s-17.061537-6.824615-17.061537-17.061537v-409.476884c0-10.236922 6.824615-17.061537 17.061537-17.061537s17.061537 6.824615 17.061537 17.061537v409.476884z m136.492295 0c0 10.236922-6.824615 17.061537-17.061537 17.061537s-17.061537-6.824615-17.061537-17.061537v-409.476884c0-10.236922 6.824615-17.061537 17.061537-17.061537s17.061537 6.824615 17.061536 17.061537v409.476884z m136.492294 0c0 10.236922-6.824615 17.061537-17.061536 17.061537s-17.061537-6.824615-17.061537-17.061537v-409.476884c0-10.236922 6.824615-17.061537 17.061537-17.061537s17.061537 6.824615 17.061536 17.061537v409.476884z"/></svg>
        <div class="device-status">Heater</div>
      </div>
      <div class="device" id="fan-device">
        <svg id="fan-svg" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path d="M512.869998 74.931113a303.434324 303.434324 0 1 0 302.996325 303.433325A303.725324 303.725324 0 0 0 512.869998 74.932113z m43.721903 45.0339c60.045866-16.176964 104.788767 60.482865 100.269776 134.082701s-82.489816 142.826682-102.018772 131.895707-23.755947-49.989889-24.483946-90.213799c-1.019998-64.126857-79.866822-147.636671 25.358944-175.764609z m-126.649718 293.232347c-55.089877 33.082926-87.444805 142.972682-164.979633 66.019853-43.721903-43.721903 0-120.964731 66.021853-153.902657s164.979633 0 164.979633 22.006951-32.063929 45.471899-66.021853 65.875853z m292.358349 131.166708c-16.177964 60.045866-104.788767 60.482865-166.29163 19.820956s-82.489816-142.826682-63.542859-153.902658 55.526876 4.954989 90.2138 24.192947c56.109875 31.33493 167.748626 4.954989 139.619689 110.179754z"/><path d="M632.377732 837.013416a10.055978 10.055978 0 0 0 10.055978-10.055977v-94.43979a377.908159 377.908159 0 1 0-158.712647 22.29795 32.208928 32.208928 0 0 0-1.748996 9.909978v200.977553H352.553355a29.147935 29.147935 0 1 0 0 58.29687h303.143325a29.147935 29.147935 0 0 0 0-58.29687h-114.989744V764.725577a29.147935 29.147935 0 0 0-1.894996-9.909978 377.32516 377.32516 0 0 0 83.654814-15.594965v87.444805a10.055978 10.055978 0 0 0 9.909978 10.347977z m-120.819731-102.019773a357.212205 357.212205 0 1 1 357.212205-356.629205 357.212205 357.212205 0 0 1-357.212205 357.213204z"/></svg>
        <div class="device-status">Fan</div>
      </div>
      <div class="device" id="humidifier-device">
        <svg id="humidifier-svg" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path d="M483.209 847.694a34.133 34.133 0 1 0 68.267 0 34.133 34.133 0 1 0-68.267 0z m364.633-720.51a137.572 137.572 0 0 0-18.105-67.822c0 26.268-142.321 47.639-317.885 47.639S194.115 85.185 194.115 59.362a137.572 137.572 0 0 0-18.106 68.267l-37.398 625.53c0 149 126.739 270.841 281.971 270.841h182.836c154.936 0 281.971-121.841 281.971-270.84z m-330.5 804.508a84.146 84.146 0 1 1 83.998-83.998 84.146 84.146 0 0 1-83.997 83.998z m-4.155-839.977c169.331 0 306.607-20.48 306.607-45.858S682.518 0 513.187 0 206.581 20.48 206.581 45.857s137.275 45.858 306.606 45.858z m183.43-68.86c44.522 0 80.287 7.568 80.287 17.066s-35.914 17.215-80.287 17.215-80.288-7.717-80.288-17.215 36.063-17.067 80.288-17.067z"/></svg>
        <div class="device-status">Humidifier</div>
      </div>
    </div>

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

    <!-- Controls panel -->
    <details class="controls-panel">
      <summary>⚙ Controls</summary>
      <div class="controls-body">

        <!-- Thresholds -->
        <div>
          <div class="controls-section-heading">Thresholds</div>
          <form id="range-form">
            <div class="threshold-row">
              <span class="threshold-metric-label">CO₂</span>
              <span class="threshold-sublabel">On</span>
              <input type="number" id="co2-on" step="100">
              <span class="threshold-sublabel">Off</span>
              <input type="number" id="co2-off" step="100">
              <span class="threshold-unit">ppm</span>
            </div>
            <div class="threshold-row">
              <span class="threshold-metric-label">Temp</span>
              <span class="threshold-sublabel">On</span>
              <input type="number" id="temp-on" step="0.5">
              <span class="threshold-sublabel">Off</span>
              <input type="number" id="temp-off" step="0.5">
              <span class="threshold-unit" id="temp-threshold-unit">°C</span>
            </div>
            <div class="threshold-row">
              <span class="threshold-metric-label">Humidity</span>
              <span class="threshold-sublabel">On</span>
              <input type="number" id="rh-on" step="5">
              <span class="threshold-sublabel">Off</span>
              <input type="number" id="rh-off" step="5">
              <span class="threshold-unit">%</span>
            </div>
            <button type="submit" class="btn btn-primary">Save Thresholds</button>
          </form>
        </div>

        <hr class="controls-divider">

        <!-- Device Modes -->
        <div>
          <div class="controls-section-heading">Device Modes</div>
          <div class="mode-row">
            <span class="mode-label">Heater</span>
            <div class="toggle-group" data-device="heater">
              <button class="toggle-btn" data-mode="on">ON</button>
              <button class="toggle-btn" data-mode="auto">AUTO</button>
              <button class="toggle-btn" data-mode="off">OFF</button>
            </div>
          </div>
          <div class="mode-row">
            <span class="mode-label">Fan</span>
            <div class="toggle-group" data-device="fan">
              <button class="toggle-btn" data-mode="on">ON</button>
              <button class="toggle-btn" data-mode="auto">AUTO</button>
              <button class="toggle-btn" data-mode="off">OFF</button>
            </div>
          </div>
          <div class="mode-row">
            <span class="mode-label">Humidifier</span>
            <div class="toggle-group" data-device="humidifier">
              <button class="toggle-btn" data-mode="on">ON</button>
              <button class="toggle-btn" data-mode="auto">AUTO</button>
              <button class="toggle-btn" data-mode="off">OFF</button>
            </div>
          </div>
        </div>

        <hr class="controls-divider">

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

  </div><!-- /page -->

  <script>
  const USE_FAHRENHEIT = JSON.parse("{{USE_FAHRENHEIT}}".toLowerCase());

  function cToF(c) { return c === null || c === undefined ? c : (c * 9/5) + 32; }
  function fToC(f) { return (f - 32) * 5 / 9; }

  async function fetchMetrics() {
    const r = await fetch('/api/metrics'); return await r.json();
  }
  async function fetchRanges() {
    const r = await fetch('/api/ranges'); return await r.json();
  }
  async function updateRanges(ranges) {
    const r = await fetch('/api/ranges', { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(ranges) });
    return await r.json();
  }
  async function fetchModes() {
    const r = await fetch('/api/modes'); return await r.json();
  }
  async function updateMode(device, mode) {
    const r = await fetch('/api/modes', { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({[device]: mode}) });
    return await r.json();
  }
  async function fetchFanSchedule() {
    const r = await fetch('/api/fan-schedule'); return await r.json();
  }
  async function updateFanSchedule(schedule) {
    const r = await fetch('/api/fan-schedule', { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(schedule) });
    return await r.json();
  }

  // getBarColor: metric is 'co2', 'temp', 'rh', or null
  function getBarColor(val, onVal, offVal, metric) {
    if (!onVal || !offVal) return '#27ae60';
    if (metric === 'co2') {
      const v = Number(val), on = Number(onVal), off = Number(offVal);
      const margin = Math.abs(off - on) * 0.2;
      if (v > off + margin) return '#e74c3c';
      if (v >= on) return '#f1c40f';
      return '#27ae60';
    }
    const isCountingUp = Number(offVal) > Number(onVal);
    const lower = isCountingUp ? Number(onVal) : Number(offVal);
    const upper = isCountingUp ? Number(offVal) : Number(onVal);
    const v = Number(val);
    const margin = Math.abs(upper - lower) * 0.2;
    if (isCountingUp) {
      if (v < lower - margin) return '#3498db';
      if (v <= upper) return '#27ae60';
      if (v <= upper + margin) return '#f1c40f';
      return '#e74c3c';
    } else {
      if (v > upper + margin) return '#3498db';
      if (v >= lower) return '#27ae60';
      if (v >= lower - margin) return '#f1c40f';
      return '#e74c3c';
    }
  }

  function getStatusText(val, onVal, offVal, metric) {
    if (val === null || val === undefined) return '';
    const color = getBarColor(val, onVal, offVal, metric);
    if (color === '#27ae60') return 'in range';
    if (color === '#f1c40f') return 'near threshold';
    if (color === '#e74c3c') return 'out of range';
    if (color === '#3498db') return 'well below';
    return '';
  }

  function updateBar(val, min, max, barId, valueId, onVal, offVal, metric) {
    const bar = document.getElementById(barId);
    const valueEl = document.getElementById(valueId);
    if (val === null || val === undefined) {
      if (valueEl) valueEl.firstChild.textContent = '--';
      if (bar) bar.style.width = '0%';
      return;
    }
    let pct = ((val - min) / (max - min)) * 100;
    pct = Math.min(100, Math.max(0, pct));
    if (bar) {
      bar.style.width = pct + '%';
      bar.style.background = metric ? getBarColor(val, onVal, offVal, metric) : '#6b5f3a';
    }
    if (valueEl) valueEl.firstChild.textContent = Number(val).toFixed(1);

    if (onVal !== undefined && offVal !== undefined) {
      const onInd  = document.getElementById(barId.replace('-bar', '-on-indicator'));
      const offInd = document.getElementById(barId.replace('-bar', '-off-indicator'));
      if (onInd && offInd) {
        onInd.style.left  = ((Number(onVal)  - min) / (max - min) * 100) + '%';
        offInd.style.left = ((Number(offVal) - min) / (max - min) * 100) + '%';
      }
    }

    const statusEl = document.getElementById(barId.replace('-bar', '-status'));
    if (statusEl && metric) {
      statusEl.textContent = getStatusText(val, onVal, offVal, metric);
    }
  }

  // Input focus tracking (prevents overwriting while editing)
  const inputIds = ['co2-on','co2-off','temp-on','temp-off','rh-on','rh-off'];
  const inputState = {};
  for (const id of inputIds) {
    inputState[id] = { focused: false, lastValue: null, editing: false };
    const input = document.getElementById(id);
    input.addEventListener('focus',  () => { inputState[id].focused = true; inputState[id].lastValue = input.value; });
    input.addEventListener('blur',   () => { inputState[id].focused = false; inputState[id].editing = false; });
    input.addEventListener('input',  () => { inputState[id].editing = true; inputState[id].lastValue = input.value; });
  }

  function setThresholdInputs(ranges) {
    const vals = {
      'co2-on': ranges.co2.on, 'co2-off': ranges.co2.off,
      'temp-on':  USE_FAHRENHEIT ? cToF(ranges.temp.on)  : ranges.temp.on,
      'temp-off': USE_FAHRENHEIT ? cToF(ranges.temp.off) : ranges.temp.off,
      'rh-on': ranges.rh.on, 'rh-off': ranges.rh.off,
    };
    for (const id of inputIds) {
      const input = document.getElementById(id);
      const state = inputState[id];
      if (!state.focused && !state.editing && vals[id] !== state.lastValue) {
        input.value = vals[id];
        state.lastValue = vals[id];
      }
    }
    // Update threshold labels under bars
    document.getElementById('co2-on-label').textContent  = ranges.co2.on;
    document.getElementById('co2-off-label').textContent = ranges.co2.off;
    const tempOn  = USE_FAHRENHEIT ? cToF(ranges.temp.on)  : ranges.temp.on;
    const tempOff = USE_FAHRENHEIT ? cToF(ranges.temp.off) : ranges.temp.off;
    document.getElementById('temp-on-label').textContent  = Number(tempOn).toFixed(1);
    document.getElementById('temp-off-label').textContent = Number(tempOff).toFixed(1);
    document.getElementById('rh-on-label').textContent  = ranges.rh.on;
    document.getElementById('rh-off-label').textContent = ranges.rh.off;
  }

  async function loadThresholdInputs() {
    const ranges = await fetchRanges();
    setThresholdInputs(ranges);
  }

  function setFanScheduleInputs(schedule) {
    const enabled = Boolean(schedule.enabled);
    document.getElementById('fan-schedule-enabled').checked = enabled;
    if (schedule.duration_minutes != null) document.getElementById('fan-schedule-duration').value = Number(schedule.duration_minutes);
    if (schedule.interval_minutes != null) document.getElementById('fan-schedule-interval').value = Number(schedule.interval_minutes);
    document.getElementById('fan-schedule-duration').disabled = !enabled;
    document.getElementById('fan-schedule-interval').disabled = !enabled;
    document.getElementById('fan-schedule-row').style.opacity = enabled ? '1' : '0.5';
  }

  async function loadFanScheduleForm() {
    const schedule = await fetchFanSchedule();
    setFanScheduleInputs(schedule);
  }

  async function loadModes() {
    const modes = await fetchModes();
    document.querySelectorAll('.toggle-group').forEach(group => {
      const device = group.dataset.device;
      group.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === modes[device]);
      });
    });
  }

  async function refresh() {
    const [metrics, ranges] = await Promise.all([fetchMetrics(), fetchRanges()]);

    const unit = USE_FAHRENHEIT ? '°F' : '°C';
    const tempMin = USE_FAHRENHEIT ? cToF(15) : 15;
    const tempMax = USE_FAHRENHEIT ? cToF(30) : 30;
    const tempOn  = USE_FAHRENHEIT ? cToF(ranges.temp.on)  : ranges.temp.on;
    const tempOff = USE_FAHRENHEIT ? cToF(ranges.temp.off) : ranges.temp.off;
    const mainTemp = USE_FAHRENHEIT ? cToF(metrics.temperature) : metrics.temperature;
    const t1 = USE_FAHRENHEIT ? cToF(metrics.temperature_1) : metrics.temperature_1;
    const t2 = USE_FAHRENHEIT ? cToF(metrics.temperature_2) : metrics.temperature_2;
    const t3 = USE_FAHRENHEIT ? cToF(metrics.temperature_3) : metrics.temperature_3;

    // Update temperature unit labels
    document.getElementById('temp-label').textContent = 'Temperature (' + unit + ')';
    document.getElementById('temp-unit').textContent = unit;
    document.getElementById('temp-threshold-unit').textContent = unit;

    updateBar(metrics.co2, 400, 2000, 'co2-bar', 'co2-value', ranges.co2.on, ranges.co2.off, 'co2');
    updateBar(mainTemp, tempMin, tempMax, 'temp-bar', 'temp-value', tempOn, tempOff, 'temp');
    updateBar(metrics.relative_humidity, 0, 100, 'rh-bar', 'rh-value', ranges.rh.on, ranges.rh.off, 'rh');

    updateBar(t1, tempMin, tempMax, 'temp1-bar', 'temp1-value', null, null, null);
    updateBar(t2, tempMin, tempMax, 'temp2-bar', 'temp2-value', null, null, null);
    updateBar(t3, tempMin, tempMax, 'temp3-bar', 'temp3-value', null, null, null);

    // Device status
    const deviceMap = [
      { id: 'heater-device',    svgId: 'heater-svg',    on: metrics.heater_on },
      { id: 'fan-device',       svgId: 'fan-svg',       on: metrics.fan_on },
      { id: 'humidifier-device',svgId: 'humidifier-svg',on: metrics.humidifier_on },
    ];
    deviceMap.forEach(({ id, on }) => {
      const card = document.getElementById(id);
      if (!card) return;
      card.classList.toggle('active', on);
      const statusDiv = card.querySelector('.device-status');
      if (statusDiv) statusDiv.textContent = on ? 'ON' : 'OFF';
    });

    document.getElementById('timestamp').textContent = 'Last update: ' + new Date().toLocaleString();
    setThresholdInputs(ranges);
  }

  // Form handlers
  document.getElementById('range-form').addEventListener('submit', async e => {
    e.preventDefault();
    let tempOn  = parseFloat(document.getElementById('temp-on').value);
    let tempOff = parseFloat(document.getElementById('temp-off').value);
    if (USE_FAHRENHEIT) { tempOn = fToC(tempOn); tempOff = fToC(tempOff); }
    await updateRanges({
      co2:  { on: parseFloat(document.getElementById('co2-on').value),  off: parseFloat(document.getElementById('co2-off').value) },
      temp: { on: tempOn, off: tempOff },
      rh:   { on: parseFloat(document.getElementById('rh-on').value),   off: parseFloat(document.getElementById('rh-off').value) },
    });
    await loadThresholdInputs();
  });

  document.getElementById('fan-schedule-enabled').addEventListener('change', e => {
    const enabled = e.target.checked;
    document.getElementById('fan-schedule-duration').disabled = !enabled;
    document.getElementById('fan-schedule-interval').disabled = !enabled;
    document.getElementById('fan-schedule-row').style.opacity = enabled ? '1' : '0.5';
  });

  document.getElementById('fan-schedule-form').addEventListener('submit', async e => {
    e.preventDefault();
    const enabled  = document.getElementById('fan-schedule-enabled').checked;
    const duration = parseFloat(document.getElementById('fan-schedule-duration').value);
    const interval = parseFloat(document.getElementById('fan-schedule-interval').value);
    const payload  = { enabled };
    if (!Number.isNaN(duration)) payload.duration_minutes = duration;
    if (!Number.isNaN(interval)) payload.interval_minutes = interval;
    await updateFanSchedule(payload);
    await loadFanScheduleForm();
  });

  function setupModeToggles() {
    document.querySelectorAll('.toggle-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const device = btn.parentElement.dataset.device;
        const mode   = btn.dataset.mode;
        await updateMode(device, mode);
        await loadModes();
      });
    });
  }

  setInterval(refresh, 5000);
  loadThresholdInputs();
  refresh();
  setupModeToggles();
  loadModes();
  loadFanScheduleForm();
  </script>

</body>
</html>
```

- [ ] **Step 2: Run all tests (no HTML unit tests — verify existing suite still passes)**

```bash
uv run pytest -v
```

Expected: all tests PASS.

- [ ] **Step 3: Manual smoke check**

Flash to device with `make flash` (or serve locally if you have a test setup) and verify:
- Page loads with earthy theme
- Metrics update every 5 seconds
- Controls panel collapses/expands
- Threshold save works
- Mode toggles work
- Fan schedule save works
- Temperature unit toggles correctly if `USE_FAHRENHEIT=true`

- [ ] **Step 4: Commit**

```bash
git add src/static/index.html
git commit -m "feat: rewrite index.html with earthy theme and controls panel"
```

---

## Chunk 3: logs.html and memory.html Rewrites

### Task 4: Rewrite `src/static/logs.html`

**Files:**
- Rewrite: `src/static/logs.html`

- [ ] **Step 1: Rewrite `src/static/logs.html`**

Replace the entire file with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MushBoom Log Files</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="stylesheet" href="/style.css">
</head>
<body>

  <nav class="navbar">
    <a class="navbar-brand" href="/">🍄 MushBoom</a>
    <div class="navbar-links">
      <a href="/logs.html">Logs</a>
      <a href="/memory.html">Memory</a>
    </div>
  </nav>

  <div class="page-wide">
    <div class="page-heading">Log Files</div>

    <div class="refresh-bar">
      <button class="btn btn-refresh" onclick="refreshLogs()">Refresh Now</button>
    </div>

    <div class="log-section">
      <h2>Application Log</h2>
      <pre id="app-log">Loading...</pre>
    </div>

    <div class="log-section">
      <h2>Error Log</h2>
      <pre id="error-log">Loading...</pre>
    </div>
  </div>

  <script>
    async function fetchLogs() {
      try {
        const appRes = await fetch('/api/logs/app');
        if (appRes.ok) {
          const data = await appRes.text();
          document.getElementById('app-log').textContent =
            data ? data.split('\n').reverse().join('\n') : 'No log entries';
        } else {
          document.getElementById('app-log').textContent = 'Failed to load log';
        }
        const errRes = await fetch('/api/logs/error');
        if (errRes.ok) {
          const data = await errRes.text();
          document.getElementById('error-log').textContent =
            data ? data.split('\n').reverse().join('\n') : 'No log entries';
        } else {
          document.getElementById('error-log').textContent = 'Failed to load log';
        }
      } catch (e) {
        console.error('Error fetching logs:', e);
      }
    }

    function refreshLogs() {
      document.getElementById('app-log').textContent = 'Loading...';
      document.getElementById('error-log').textContent = 'Loading...';
      fetchLogs();
    }

    fetchLogs();
  </script>
</body>
</html>
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest -v
```

Expected: all PASS.

- [ ] **Step 3: Commit**

```bash
git add src/static/logs.html
git commit -m "feat: rewrite logs.html with earthy theme"
```

---

### Task 5: Rewrite `src/static/memory.html`

**Files:**
- Rewrite: `src/static/memory.html`

- [ ] **Step 1: Rewrite `src/static/memory.html`**

> **Note — intentional bug fix in `fetchData()`:** The current source has two unreachable branches: `current.percent > 25` is checked before `> 30` (so `danger` is never reached), and `change > 5` is checked before `> 10` (same issue). The rewrite corrects the check order (`> 30` → danger, `> 25` → warning; `> 10` → danger, `> 5` → warning). This is a deliberate fix bundled with the visual rewrite — the spec's "logic preserved unchanged" applies to behavior that actually fires, and these branches were dead code.

Replace the entire file with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MushBoom Memory Monitor</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="stylesheet" href="/style.css">
</head>
<body>

  <nav class="navbar">
    <a class="navbar-brand" href="/">🍄 MushBoom</a>
    <div class="navbar-links">
      <a href="/logs.html">Logs</a>
      <a href="/memory.html">Memory</a>
    </div>
  </nav>

  <div class="page-wide">
    <div class="page-heading">Memory Usage Monitor</div>

    <div class="stats-grid">
      <div class="card">
        <div class="stat-title">Current Usage</div>
        <div class="stat-value" id="current-percent">--.-%</div>
        <div class="stat-details">
          <span id="current-used">-- KB</span> used /
          <span id="current-total">-- KB</span> total
        </div>
      </div>
      <div class="card">
        <div class="stat-title">Maximum Usage</div>
        <div class="stat-value" id="max-percent">--.-%</div>
        <div class="stat-details" id="max-time">--</div>
      </div>
      <div class="card">
        <div class="stat-title">Since Startup</div>
        <div class="stat-value" id="change-since-startup">--.-</div>
        <div class="stat-details">Started at <span id="startup-percent">--.-%</span></div>
      </div>
      <div class="card">
        <div class="stat-title">Trend</div>
        <div class="stat-value" id="trend">--</div>
        <div class="stat-details" id="trend-details">--</div>
      </div>
    </div>

    <div class="refresh-bar">
      <button class="btn btn-refresh" onclick="fetchData()">Refresh Data</button>
    </div>

    <div class="last-updated">Last updated: <span id="last-update">--</span></div>
  </div>

  <script>
    function formatBytes(bytes) { return (bytes / 1024).toFixed(1) + ' KB'; }
    function formatTime(ts) {
      if (!ts) return '--';
      return new Date(ts * 1000).toLocaleString();
    }

    function fetchData() {
      fetch('/api/memory')
        .then(r => r.json())
        .then(data => {
          const pct = data.current.percent;
          const currentEl = document.getElementById('current-percent');
          currentEl.textContent = pct.toFixed(1) + '%';
          currentEl.className = 'stat-value' + (pct > 30 ? ' danger' : pct > 25 ? ' warning' : ' good');

          document.getElementById('current-used').textContent  = formatBytes(data.current.used);
          document.getElementById('current-total').textContent = formatBytes(data.current.total);
          document.getElementById('max-percent').textContent   = data.history.max.percent.toFixed(1) + '%';
          document.getElementById('max-time').textContent      = 'at ' + formatTime(data.history.max.time);

          const change = data.current.percent - data.history.startup.percent;
          const changeEl = document.getElementById('change-since-startup');
          changeEl.textContent = (change >= 0 ? '+' : '') + change.toFixed(1) + '%';
          changeEl.className = 'stat-value' + (change > 10 ? ' danger' : change > 5 ? ' warning' : ' good');

          document.getElementById('startup-percent').textContent = data.history.startup.percent.toFixed(1) + '%';

          const trendEl = document.getElementById('trend');
          if (data.history.trend_increasing) {
            trendEl.textContent = '↑ Increasing';
            trendEl.className = 'stat-value warning';
            document.getElementById('trend-details').textContent = 'Memory usage is trending upward';
          } else {
            trendEl.textContent = '→ Stable';
            trendEl.className = 'stat-value good';
            document.getElementById('trend-details').textContent = 'Memory usage is stable';
          }

          document.getElementById('last-update').textContent = new Date().toLocaleString();
        })
        .catch(e => console.error('Error fetching memory data:', e));
    }

    document.addEventListener('DOMContentLoaded', fetchData);
    setInterval(fetchData, 60000);
  </script>
</body>
</html>
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest -v
```

Expected: all PASS.

- [ ] **Step 3: Commit**

```bash
git add src/static/memory.html
git commit -m "feat: rewrite memory.html with earthy theme"
```

---

### Task 6: Final verification

- [ ] **Step 1: Run the full test suite one final time**

```bash
uv run pytest -v
```

Expected: all tests PASS including `test_api_static.py`.

- [ ] **Step 2: Lint check**

```bash
make lint
```

Expected: no errors in `src/api.py`.

- [ ] **Step 3: Flash and end-to-end smoke test on device**

```bash
make flash
```

Open the device IP in a mobile browser. Verify all 3 pages load with the earthy theme, all controls work, and the nav links between pages correctly.
