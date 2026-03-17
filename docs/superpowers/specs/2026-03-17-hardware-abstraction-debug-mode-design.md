# Hardware Abstraction & Debug Mode Design

**Date:** 2026-03-17
**Status:** Approved

## Goal

Enable Claude Code to test the MushBoom app on real hardware by:
- Uploading files to the board via USB
- Tailing logs via REPL
- Injecting mock sensor values in debug mode
- Reading system state and relay decisions via HTTP API
- Interacting with the dashboard

## Context

MushBoom runs on ESP32-S3 (MicroPython). The current codebase initializes I2C sensors and GPIO relays directly inside `sensor_loop.py` and `relay_loop.py`. There is no abstraction boundary between hardware and logic, making it impossible to run without real hardware attached.

## Approach: Hardware Abstraction Layer with Factory Functions

A single new file `src/hardware.py` provides duck-typed sensor and relay driver classes. A factory function returns the real or stub implementation based on a `DEBUG_MODE` flag in `config_local.py`. All hardware-dependent loops receive their driver at startup — no `if DEBUG_MODE` inside loop logic.

## Affected Files

| File | Change |
|------|--------|
| `src/hardware.py` | **New** — sensor and relay driver classes + factories |
| `src/api_debug.py` | **New** — debug API routes (registered only in DEBUG_MODE) |
| `src/tasks/sensor_loop.py` | Remove module-level hardware imports and init; accept `sensor_driver` param |
| `src/tasks/relay_loop.py` | Remove singleton instantiation and module-level hardware imports; accept `relay_driver` param |
| `src/main.py` | Call factory functions; pass drivers to loops via lambda; register debug routes |
| `src/config.py` | Add `DEBUG_MODE = False` default |
| `src/config_local.example.py` | Document `DEBUG_MODE = True` and `DEVICE_IP` |
| `Makefile` | Add `repl`, `logs`, `restart` targets; add `logs/` mkdir to `flash` |
| `CLAUDE.md` | Add Hardware Testing section |
| `tools/tail_log.py` | **New** — log tailing script run via `mpremote run` |

## Components

### 1. `src/hardware.py` — Hardware Abstraction Layer

Two driver pairs, each with a real and stub implementation. All hardware imports (`machine`, `vendor.scd4x`, `vendor.pct2075`) live exclusively in this file — they must not remain in `sensor_loop.py` or `relay_loop.py`.

**Sensor drivers:**
- `RealSensorDriver.__init__()` — initializes I2C bus, SCD4X, and PCT2075 sensors (logic moved from `sensor_loop.py`). Init failure raises (let `safe_task` restart the loop).
- `RealSensorDriver.read()` — polls hardware; returns dict with `temperature`, `co2`, `relative_humidity`, `temperature_1/2/3`. Wraps all I2C reads in try/except — on transient error, logs the error and returns `{}` (graceful degradation without restarting the task). The `data_ready` guard is handled here: if `scd4x.data_ready` is False, the SCD4X keys are omitted from the returned dict.
- `StubSensorDriver.__init__()` — sets `self.values = {}` (empty; no sensor readings until injected)
- `StubSensorDriver.read()` — returns `self.values` directly

**Relay drivers:**
- `RealRelayDriver.__init__()` — initializes GPIO pins (logic moved from `relay_loop.py`; active-LOW)
- `RealRelayDriver.set_heater(on)`, `set_fan(on)`, `set_humidifier(on)` — toggle real pins
- `StubRelayDriver.set_heater(on)`, `set_fan(on)`, `set_humidifier(on)` — log the call (e.g. `logger.debug("StubRelayDriver: set_fan(%s)", on)`) then no-op

**Factories:**
```python
def get_sensor_driver():
    from config import DEBUG_MODE
    return StubSensorDriver() if DEBUG_MODE else RealSensorDriver()

def get_relay_driver():
    from config import DEBUG_MODE
    return StubRelayDriver() if DEBUG_MODE else RealRelayDriver()
```

### 2. `src/tasks/sensor_loop.py` — Updated

Remove all module-level imports of `machine`, `vendor.scd4x`, `vendor.pct2075`, and all sensor init code. These imports currently crash at import time on any non-ESP32 host. The loop function signature changes to accept a `sensor_driver` parameter:

```python
async def poll_sensor_loop(sensor_driver):
    while True:
        readings = sensor_driver.read()
        # Unconditionally write all keys to SystemState using .get() (returns None for absent keys)
        state.temperature = readings.get("temperature")
        state.co2 = readings.get("co2")
        state.relative_humidity = readings.get("relative_humidity")
        state.temperature_1 = readings.get("temperature_1")
        state.temperature_2 = readings.get("temperature_2")
        state.temperature_3 = readings.get("temperature_3")
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
```

The `data_ready` guard (currently in `sensor_loop.py` line 92) moves inside `RealSensorDriver.read()`. When data is not ready, `RealSensorDriver.read()` returns an empty dict `{}`, so all `SystemState` fields are written as `None` — matching the existing control loop guard behavior (`if not temps`, `if state.co2 is not None`).

`StubSensorDriver.read()` returns `self.values` directly. Empty dict after DELETE → all fields `None` → control loop makes no decisions until values are re-injected. Note: when temperature becomes `None`, `control_loop.py` actively turns the heater **off** as a safety fallback (line 115-119: `if not temps: heater off, return`). DELETE is not state-preserving — it is a safety reset.

### 3. `src/tasks/relay_loop.py` — Updated

Remove the module-level `relay_controller = RelayController()` singleton (line 65) and all `machine`/`Pin` imports (line 1). These execute at import time — `main.py` imports `relay_controller` at line 15 before `DEBUG_MODE` is checked, crashing immediately on any host without GPIO.

The `RelayController` class is replaced with a free function. State change tracking (previously `last_*_state` on `RelayController`) moves into the function's local variables:

```python
async def poll_relay_loop(relay_driver):
    last_heater = last_fan = last_humidifier = False
    while True:
        if state.heater_on != last_heater:
            relay_driver.set_heater(state.heater_on)
            last_heater = state.heater_on
        if state.fan_on != last_fan:
            relay_driver.set_fan(state.fan_on)
            last_fan = state.fan_on
        if state.humidifier_on != last_humidifier:
            relay_driver.set_humidifier(state.humidifier_on)
            last_humidifier = state.humidifier_on
        await asyncio.sleep(5)
```

### 4. `src/main.py` — Updated

Calls factory functions at startup and passes drivers into loops via lambdas (MicroPython has no `functools.partial`). Uses the existing two-argument `safe_task(name, coro_func)` signature and `asyncio.create_task()` wrapper:

```python
from hardware import get_sensor_driver, get_relay_driver
from tasks.sensor_loop import poll_sensor_loop
from tasks.relay_loop import poll_relay_loop
from config import DEBUG_MODE

sensor_driver = get_sensor_driver()
relay_driver = get_relay_driver()

if DEBUG_MODE:
    from api_debug import register_debug_routes
    register_debug_routes(app, sensor_driver)

# In main():
asyncio.create_task(safe_task("Sensor", lambda: poll_sensor_loop(sensor_driver)))
asyncio.create_task(safe_task("Relay", lambda: poll_relay_loop(relay_driver)))
```

The existing `from tasks.relay_loop import relay_controller` import in `main.py` is removed and replaced with the above.

### 5. `src/api_debug.py` — Debug API Routes

Only registered when `DEBUG_MODE = True`. Validates keys against the known set before updating stub state.

```python
VALID_KEYS = {"temperature", "co2", "relative_humidity", "temperature_1", "temperature_2", "temperature_3"}

def register_debug_routes(app, sensor_driver):
    @app.put("/api/debug/state")
    async def set_debug_state(request):
        data = request.json or {}
        unknown = set(data.keys()) - VALID_KEYS
        if unknown:
            return Response(
                body=json.dumps({"ok": False, "error": f"Unknown keys: {list(unknown)}"}),
                status_code=400,
                headers={"Content-Type": "application/json"},
            )
        sensor_driver.values.update(data)
        return Response(body=json.dumps({"ok": True}), headers={"Content-Type": "application/json"})

    @app.delete("/api/debug/state")
    async def clear_debug_state(request):
        sensor_driver.values.clear()
        return Response(body=json.dumps({"ok": True}), headers={"Content-Type": "application/json"})
```

**Behavior after DELETE:** `sensor_driver.values` becomes `{}`. On the next sensor poll, `sensor_loop` writes `None` for all fields to `SystemState`. `control_loop` guards on `if state.temperature is not None`, so no relay decisions are made. This is expected — re-inject values to resume control.

### 6. `src/config.py` — Updated

Add default:
```python
DEBUG_MODE = False
```

### 7. `src/config_local.example.py` — Updated

Document debug config:
```python
# Set to True when testing without real hardware (sensors/relays not attached)
# DEBUG_MODE = True

# Device IP for HTTP testing (shell variable — not used by app code)
# DEVICE_IP = "192.168.1.x"  # find via 'mpremote exec "import network; ..."'
```

`DEVICE_IP` is a **shell environment variable** set by the developer — it is not read by the app. The example file documents it as a comment convention so developers know to look for it.

### 8. Makefile Additions

```makefile
repl:
	$(MPREMOTE) connect $(DEVICE) repl

logs:
	$(MPREMOTE) connect $(DEVICE) run tools/tail_log.py

restart:
	$(MPREMOTE) connect $(DEVICE) exec "import machine; machine.soft_reset()"
```

Also add `logs/` directory creation to the `flash` target (after the existing `mkdir` calls):
```makefile
$(MPREMOTE) connect $(DEVICE) fs mkdir $(BOARD_PATH)/logs || true
```

**`logs` target:** Uses `mpremote run` with a script rather than inline code (shell cannot pass multi-line Python via `exec` reliably). New file `tools/tail_log.py`:
```python
import time
f = open("logs/mushboom.log")
f.seek(0, 2)
while True:
    line = f.readline()
    if line:
        print(line, end="")
    else:
        time.sleep(0.5)
```

**`restart` target:** Uses `machine.soft_reset()` (not `mpremote reset`) to re-run `main.py` without power-cycling peripherals.

### 9. `CLAUDE.md` Hardware Testing Section

Documents the full developer workflow. Key points:
- `DEVICE_IP` is a shell variable (`export DEVICE_IP=192.168.1.x`) not an app config value
- After `DELETE /api/debug/state`, no relay decisions are made until values are re-injected
- `make restart` does a soft reset (re-runs `main.py`); use `make flash` then `make restart` for a full deploy cycle

## Debug Testing Workflow

```sh
# 1. Configure
#    Set DEBUG_MODE = True in config_local.py
#    export DEVICE_IP=192.168.1.x

# 2. Deploy
make flash && make restart

# 3. In a separate terminal, tail logs
make logs

# 4. Inject sensor values
curl -X PUT http://$DEVICE_IP/api/debug/state \
  -H 'Content-Type: application/json' \
  -d '{"temperature": 17.0, "co2": 1200, "relative_humidity": 85}'

# 5. Wait ≤5s for control loop tick, then read relay decisions
curl http://$DEVICE_IP/api/metrics
# → {"heater_on": true, "fan_on": true, "humidifier_on": true, ...}

# 6. Clear mocks (relay decisions stop until re-injected)
curl -X DELETE http://$DEVICE_IP/api/debug/state

# 7. Interact with dashboard
open http://$DEVICE_IP/

# 8. Set thresholds
curl -X PUT http://$DEVICE_IP/api/ranges \
  -H 'Content-Type: application/json' \
  -d '{"temp": {"on": 18, "off": 22}}'

# 9. Set device modes
curl -X PUT http://$DEVICE_IP/api/modes \
  -H 'Content-Type: application/json' \
  -d '{"fan": "on"}'
```

## What Is NOT Changed

- `control_loop.py` — reads `SystemState` and `AppConfig` as before; no hardware dependency
- `SystemState` / `AppConfig` — unchanged
- All existing REST API endpoints — unchanged
- Unit tests — unchanged (already mock at module level)

## Relay State Observability

`StubRelayDriver` methods log their calls then no-op — visible in `make logs`. `control_loop.py` still writes `state.fan_on`, `state.heater_on`, `state.humidifier_on` based on injected sensor readings. These are returned by `/api/metrics` and reflected in the dashboard — no separate relay injection needed.
