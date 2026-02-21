# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MushBoom is a MicroPython application for ESP32 that controls environmental conditions for mushroom cultivation. It monitors temperature, humidity, and CO2 via I2C sensors and controls GPIO relays for a heater, fan, and humidifier. A Microdot web server exposes a REST API and dashboard.

## Commands

```bash
make sync          # Install dependencies via UV
make lint          # Run ruff linter
make format        # Auto-format code with black
make typecheck     # Type-check with pyright
make test          # Run pytest unit tests
make flash         # Deploy to connected ESP32
make flash-clean   # Wipe device and deploy fresh
make clean         # Remove __pycache__ directories
```

Run a single test file: `uv run pytest tests/test_control.py`

## Architecture

The system is built around `uasyncio` coroutines. `main.py` initializes WiFi, starts the Microdot web server, and schedules all background tasks. Each task runs in a `safe_task()` wrapper (`tasks/task_helpers.py`) that automatically restarts it on crash.

**Data flow:** `sensor_loop.py` reads I2C sensors every 30s and writes to `SystemState`. `control_loop.py` reads `SystemState` and `AppConfig` to compute desired relay states, writing decisions back to `SystemState`. `relay_loop.py` polls `SystemState` every 5s and toggles GPIO pins (active-LOW: `0` = ON).

**Shared state** (`shared_state.py`): Two dataclasses — `SystemState` (live readings + relay states) and `AppConfig` (user-configured thresholds, modes, fan schedule). `AppConfig` is persisted to `config.json` on the device filesystem.

**Web API** (`api.py`): REST endpoints for metrics (`/api/metrics`), thresholds (`/api/ranges`), device modes (`/api/modes`), fan schedule (`/api/fan-schedule`), logs (`/api/logs/*`), and memory (`/api/memory`). Static web UI lives in `src/static/`.

**Hardware config** (`config.py`): All GPIO pin assignments, I2C addresses, and sensor polling intervals are defined here. Relay logic is active-LOW.

**Logging** (`lib/logger.py`): Custom logger that writes to both `mushboom.log` (all levels) and `error.log` (errors only), with 500KB rotation and 2000-entry cap. Logs are viewable via the web UI.

**WiFi** (`lib/wifi.py`): Wraps the vendored `wifi_manager.py`. Falls back to AP mode if no known networks are found. Syncs NTP on connect.

**ThingSpeak** (`lib/thingspeak.py`, `tasks/thingspeak_loop.py`): Optional cloud reporting; configured in `config.py`.

## Key Files

| File | Purpose |
|------|---------|
| `src/main.py` | Entry point — WiFi, web server, task startup |
| `src/config.py` | Hardware pin/sensor configuration (edit this for new hardware) |
| `src/shared_state.py` | `SystemState` and `AppConfig` dataclasses |
| `src/api.py` | All HTTP routes |
| `src/tasks/control_loop.py` | Hysteresis control logic and fan scheduling |
| `src/tasks/sensor_loop.py` | Sensor polling |
| `src/tasks/relay_loop.py` | GPIO relay control |
| `src/lib/logger.py` | Custom logging |
| `tests/test_control.py` | Unit tests for control/hysteresis logic |

## Development Notes

- **Target runtime is MicroPython** on ESP32-S3. Pyright is configured with MicroPython stubs (`micropython-esp32-esp32_generic_s3-stubs`). Standard CPython APIs may not exist on-device.
- `networks.json` (gitignored) holds WiFi credentials; copy from `networks.example.json`.
- Vendor dependencies (`microdot.py`, `wifi_manager.py`, sensor drivers) live in `src/vendor/` and should not be edited.
- Control modes per device: `auto` (threshold-based), `on` (always on), `off` (always off).
