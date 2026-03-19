# Hardware Abstraction & Debug Mode Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce a hardware abstraction layer so MushBoom can run in `DEBUG_MODE` without real sensors or relays attached, with mock sensor values injectable via HTTP.

**Architecture:** A new `src/hardware.py` provides duck-typed `RealSensorDriver`/`StubSensorDriver` and `RealRelayDriver`/`StubRelayDriver` classes returned by factory functions. `sensor_loop.py` and `relay_loop.py` accept their driver as a parameter; `main.py` instantiates drivers using the factories. A new `src/api_debug.py` registers `PUT/DELETE /api/debug/state` endpoints when `DEBUG_MODE=True`.

**Tech Stack:** MicroPython (ESP32-S3), Microdot, `mpremote`, `uasyncio`, pytest (host-side tests only)

**Spec:** `docs/superpowers/specs/2026-03-17-hardware-abstraction-debug-mode-design.md`

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `src/config.py` | Modify | Add `DEBUG_MODE = False` default |
| `src/config_local.example.py` | Modify | Document `DEBUG_MODE` and `DEVICE_IP` |
| `src/hardware.py` | **Create** | Stub + real sensor/relay drivers + factories |
| `src/tasks/sensor_loop.py` | Modify | Accept `sensor_driver` param; remove hardware imports |
| `src/tasks/relay_loop.py` | Modify | Replace `RelayController` singleton with free function |
| `src/main.py` | Modify | Instantiate drivers; pass to loops; register debug routes |
| `src/api_debug.py` | **Create** | `PUT/DELETE /api/debug/state` (DEBUG_MODE only) |
| `tools/tail_log.py` | **Create** | Log tail script for `mpremote run` |
| `Makefile` | Modify | Add `repl`, `logs`, `restart`; add `logs/` mkdir in `flash` |
| `CLAUDE.md` | Modify | Add Hardware Testing section |
| `tests/test_hardware.py` | **Create** | Tests for stub drivers |
| `tests/test_sensor_loop.py` | **Create** | Tests for refactored sensor loop |
| `tests/test_relay_loop.py` | **Create** | Tests for refactored relay loop |
| `tests/test_api_debug.py` | **Create** | Tests for debug API validation logic |

---

## Task 1: Add `DEBUG_MODE` default to `config.py`

**Files:**
- Modify: `src/config.py`

- [ ] **Step 1: Add `DEBUG_MODE = False`** at the end of the main config block in `src/config.py` (before the `config_local` import block):

```python
# Debug mode — set to True in config_local.py when testing without real hardware
DEBUG_MODE = False
```

- [ ] **Step 2: Run existing tests to confirm nothing breaks**

```bash
make test
```

Expected: all existing tests pass.

- [ ] **Step 3: Commit**

```bash
git add src/config.py
git commit -m "feat: add DEBUG_MODE = False default to config"
```

---

## Task 2: Stub drivers — test first, then implement

**Files:**
- Create: `src/hardware.py` (stubs only for now)
- Create: `tests/test_hardware.py`

### Stub drivers test

- [ ] **Step 1: Create `tests/test_hardware.py` with failing tests**

```python
import sys
import os
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock MicroPython-only modules so hardware.py can be imported on host
mock_machine = types.ModuleType('machine')
class _MockPin:
    OUT = 1
    def __init__(self, pin, mode=None): pass
    def value(self, v=None): pass
mock_machine.Pin = _MockPin
mock_machine.I2C = lambda *a, **kw: object()
sys.modules['machine'] = mock_machine

mock_scd4x = types.ModuleType('vendor.scd4x')
mock_scd4x.SCD4X = lambda i2c: object()
sys.modules['vendor'] = types.ModuleType('vendor')
sys.modules['vendor.scd4x'] = mock_scd4x

mock_pct = types.ModuleType('vendor.pct2075')
mock_pct.PCT2075 = lambda i2c, address=0: object()
sys.modules['vendor.pct2075'] = mock_pct

mock_logger = types.SimpleNamespace(
    debug=lambda *a, **k: None,
    info=lambda *a, **k: None,
    warning=lambda *a, **k: None,
    error=lambda *a, **k: None,
)
sys.modules['lib'] = types.ModuleType('lib')
sys.modules['lib.logger'] = types.SimpleNamespace(get_logger=lambda name: mock_logger)

# Mock config — DEBUG_MODE=False for these tests (stubs tested directly, not via factory)
mock_config = types.ModuleType('config')
mock_config.DEBUG_MODE = False
mock_config.QT_POWER_PIN = -1
mock_config.SCD4X_I2C_BUS = 1
mock_config.SCD4X_I2C_SDA_PIN = 3
mock_config.SCD4X_I2C_SCL_PIN = 4
mock_config.SCD4X_I2C_FREQ = 100000
mock_config.PCT2075_I2C_BUS_0 = 1
mock_config.PCT2075_I2C_SDA_PIN_0 = -1
mock_config.PCT2075_I2C_SCL_PIN_0 = -1
mock_config.PCT2075_I2C_ADDR_0 = 0x37
mock_config.PCT2075_I2C_BUS_1 = 1
mock_config.PCT2075_I2C_SDA_PIN_1 = -1
mock_config.PCT2075_I2C_SCL_PIN_1 = -1
mock_config.PCT2075_I2C_ADDR_1 = 0x76
mock_config.PCT2075_I2C_BUS_2 = 1
mock_config.PCT2075_I2C_SDA_PIN_2 = -1
mock_config.PCT2075_I2C_SCL_PIN_2 = -1
mock_config.PCT2075_I2C_ADDR_2 = 0x77
sys.modules['config'] = mock_config

import importlib
hardware = importlib.import_module('src.hardware')


class TestStubSensorDriver:
    def setup_method(self):
        self.driver = hardware.StubSensorDriver()

    def test_starts_empty(self):
        assert self.driver.values == {}

    def test_read_returns_empty_dict_when_no_values_injected(self):
        result = self.driver.read()
        assert result == {}

    def test_read_returns_injected_values(self):
        self.driver.values = {"temperature": 25.0, "co2": 800}
        result = self.driver.read()
        assert result["temperature"] == 25.0
        assert result["co2"] == 800

    def test_read_returns_same_dict_reference(self):
        self.driver.values["temperature"] = 22.0
        assert self.driver.read()["temperature"] == 22.0

    def test_clear_empties_values(self):
        self.driver.values = {"temperature": 25.0}
        self.driver.values.clear()
        assert self.driver.read() == {}


class TestStubRelayDriver:
    def setup_method(self):
        self.driver = hardware.StubRelayDriver()

    def test_set_heater_does_not_raise(self):
        self.driver.set_heater(True)
        self.driver.set_heater(False)

    def test_set_fan_does_not_raise(self):
        self.driver.set_fan(True)
        self.driver.set_fan(False)

    def test_set_humidifier_does_not_raise(self):
        self.driver.set_humidifier(True)
        self.driver.set_humidifier(False)


class TestFactories:
    def test_get_sensor_driver_returns_stub_when_debug(self):
        mock_config.DEBUG_MODE = True
        driver = hardware.get_sensor_driver()
        assert isinstance(driver, hardware.StubSensorDriver)
        mock_config.DEBUG_MODE = False

    def test_get_relay_driver_returns_stub_when_debug(self):
        mock_config.DEBUG_MODE = True
        driver = hardware.get_relay_driver()
        assert isinstance(driver, hardware.StubRelayDriver)
        mock_config.DEBUG_MODE = False
```

- [ ] **Step 2: Run tests — expect ImportError (hardware.py doesn't exist yet)**

```bash
uv run pytest tests/test_hardware.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.hardware'`

- [ ] **Step 3: Create `src/hardware.py` — stub drivers only**

```python
from lib.logger import get_logger

logger = get_logger("hardware")


class StubSensorDriver:
    def __init__(self):
        self.values = {}

    def read(self):
        return self.values


class StubRelayDriver:
    def __init__(self):
        self._logger = get_logger("hardware.relay.stub")

    def set_heater(self, on):
        self._logger.debug("StubRelayDriver: set_heater(%s)", on)

    def set_fan(self, on):
        self._logger.debug("StubRelayDriver: set_fan(%s)", on)

    def set_humidifier(self, on):
        self._logger.debug("StubRelayDriver: set_humidifier(%s)", on)


class RealSensorDriver:
    pass  # implemented in Task 3


class RealRelayDriver:
    pass  # implemented in Task 3


def get_sensor_driver():
    from config import DEBUG_MODE
    return StubSensorDriver() if DEBUG_MODE else RealSensorDriver()


def get_relay_driver():
    from config import DEBUG_MODE
    return StubRelayDriver() if DEBUG_MODE else RealRelayDriver()
```

- [ ] **Step 4: Run tests — expect pass**

```bash
uv run pytest tests/test_hardware.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Run full test suite**

```bash
make test
```

Expected: all existing tests still pass.

- [ ] **Step 6: Commit**

```bash
git add src/hardware.py tests/test_hardware.py
git commit -m "feat: add stub sensor and relay drivers with factory functions"
```

---

## Task 3: Real drivers — move hardware init into `hardware.py`

**Files:**
- Modify: `src/hardware.py` (fill in `RealSensorDriver` and `RealRelayDriver`)

The real drivers move init code from `sensor_loop.py` and `relay_loop.py` verbatim. No new unit tests — these require physical hardware. The test suite already passes with stubs.

- [ ] **Step 1: Fill in `RealSensorDriver` in `src/hardware.py`**

Replace the `class RealSensorDriver: pass` stub with:

```python
class RealSensorDriver:
    def __init__(self):
        from machine import I2C, Pin
        from vendor.scd4x import SCD4X
        from vendor.pct2075 import PCT2075
        from config import (
            QT_POWER_PIN,
            SCD4X_I2C_BUS, SCD4X_I2C_SDA_PIN, SCD4X_I2C_SCL_PIN, SCD4X_I2C_FREQ,
            PCT2075_I2C_BUS_0, PCT2075_I2C_SDA_PIN_0, PCT2075_I2C_SCL_PIN_0, PCT2075_I2C_ADDR_0,
            PCT2075_I2C_BUS_1, PCT2075_I2C_SDA_PIN_1, PCT2075_I2C_SCL_PIN_1, PCT2075_I2C_ADDR_1,
            PCT2075_I2C_BUS_2, PCT2075_I2C_SDA_PIN_2, PCT2075_I2C_SCL_PIN_2, PCT2075_I2C_ADDR_2,
        )

        if QT_POWER_PIN > -1:
            qtpwr = Pin(QT_POWER_PIN, Pin.OUT)
            qtpwr.value(1)
            logger.info("QT port power enabled on pin %d", QT_POWER_PIN)

        i2c_scd4x = I2C(
            SCD4X_I2C_BUS,
            sda=Pin(SCD4X_I2C_SDA_PIN),
            scl=Pin(SCD4X_I2C_SCL_PIN),
            freq=SCD4X_I2C_FREQ,
        )
        logger.info("Initializing SCD4X on I2C bus %d (SDA %d, SCL %d)",
                    SCD4X_I2C_BUS, SCD4X_I2C_SDA_PIN, SCD4X_I2C_SCL_PIN)
        logger.info("I2C devices found: %s", i2c_scd4x.scan())
        self._scd4x = SCD4X(i2c_scd4x)
        self._scd4x.start_periodic_measurement()
        logger.info("SCD4X initialized")

        pct_configs = [
            (PCT2075_I2C_BUS_0, PCT2075_I2C_SDA_PIN_0, PCT2075_I2C_SCL_PIN_0, PCT2075_I2C_ADDR_0),
            (PCT2075_I2C_BUS_1, PCT2075_I2C_SDA_PIN_1, PCT2075_I2C_SCL_PIN_1, PCT2075_I2C_ADDR_1),
            (PCT2075_I2C_BUS_2, PCT2075_I2C_SDA_PIN_2, PCT2075_I2C_SCL_PIN_2, PCT2075_I2C_ADDR_2),
        ]
        self._pct_sensors = []
        for i, (bus, sda, scl, addr) in enumerate(pct_configs):
            if sda > -1 or scl > -1:
                try:
                    i2c = I2C(bus, sda=Pin(sda), scl=Pin(scl), freq=100000)
                    sensor = PCT2075(i2c, address=addr)
                    self._pct_sensors.append(sensor)
                    logger.info("PCT2075 sensor %d initialized on I2C bus %d", i + 1, bus)
                except Exception as e:
                    logger.error("PCT2075 sensor %d init failed: %s", i + 1, e)
                    self._pct_sensors.append(None)
            else:
                self._pct_sensors.append(None)

    def read(self):
        result = {}
        try:
            if self._scd4x.data_ready:
                result["co2"] = self._scd4x.co2
                result["temperature"] = self._scd4x.temperature
                result["relative_humidity"] = self._scd4x.relative_humidity
                logger.debug("SCD4X: CO2=%s T=%s RH=%s",
                             result["co2"], result["temperature"], result["relative_humidity"])
        except Exception as e:
            logger.error("SCD4X read error: %s", e)

        for i, sensor in enumerate(self._pct_sensors):
            if sensor:
                try:
                    key = f"temperature_{i + 1}"
                    result[key] = sensor.temperature
                    logger.debug("PCT2075 sensor %d: %s°C", i + 1, result[key])
                except Exception as e:
                    logger.error("PCT2075 sensor %d read error: %s", i + 1, e)

        return result
```

- [ ] **Step 2: Fill in `RealRelayDriver` in `src/hardware.py`**

Replace `class RealRelayDriver: pass` with:

```python
class RealRelayDriver:
    def __init__(self):
        from machine import Pin
        from config import HEATER_RELAY_PIN, FAN_RELAY_PIN, HUMIDIFIER_RELAY_PIN
        self._heater_pin = Pin(HEATER_RELAY_PIN, Pin.OUT)
        self._fan_pin = Pin(FAN_RELAY_PIN, Pin.OUT)
        self._humidifier_pin = Pin(HUMIDIFIER_RELAY_PIN, Pin.OUT)
        # Initialize to OFF (active-LOW: 1 = OFF)
        self._heater_pin.value(1)
        self._fan_pin.value(1)
        self._humidifier_pin.value(1)
        logger.info("RealRelayDriver: GPIO pins initialized")

    def set_heater(self, on):
        self._heater_pin.value(0 if on else 1)

    def set_fan(self, on):
        self._fan_pin.value(0 if on else 1)

    def set_humidifier(self, on):
        self._humidifier_pin.value(0 if on else 1)
```

- [ ] **Step 3: Run tests — confirm stubs still pass**

```bash
make test
```

Expected: all tests pass (real drivers are not instantiated in tests).

- [ ] **Step 4: Commit**

```bash
git add src/hardware.py
git commit -m "feat: implement RealSensorDriver and RealRelayDriver in hardware.py"
```

---

## Task 4: Refactor `sensor_loop.py` — test first

**Files:**
- Create: `tests/test_sensor_loop.py`
- Modify: `src/tasks/sensor_loop.py`

- [ ] **Step 1: Create `tests/test_sensor_loop.py` with failing tests**

```python
import sys
import os
import types
import asyncio as stdlib_asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock uasyncio — sleep raises StopIteration after first call to break the loop
class _StopAfterOne(Exception):
    pass

_sleep_call_count = 0

class _MockAsyncio:
    async def sleep(self, s):
        global _sleep_call_count
        _sleep_call_count += 1
        if _sleep_call_count >= 1:
            raise _StopAfterOne()

sys.modules['uasyncio'] = _MockAsyncio()

mock_logger = types.SimpleNamespace(
    debug=lambda *a, **k: None,
    info=lambda *a, **k: None,
    warning=lambda *a, **k: None,
    error=lambda *a, **k: None,
)
sys.modules['lib'] = types.ModuleType('lib')
sys.modules['lib.logger'] = types.SimpleNamespace(get_logger=lambda name: mock_logger)

mock_state = types.SimpleNamespace(
    temperature=None,
    co2=None,
    relative_humidity=None,
    temperature_1=None,
    temperature_2=None,
    temperature_3=None,
)
sys.modules['shared_state'] = types.SimpleNamespace(state=mock_state)

mock_config = types.ModuleType('config')
mock_config.POLL_INTERVAL_SECONDS = 30
sys.modules['config'] = mock_config

import importlib
sensor_loop = importlib.import_module('src.tasks.sensor_loop')


def _run_one_iteration(driver):
    """Run poll_sensor_loop for exactly one iteration then stop."""
    global _sleep_call_count
    _sleep_call_count = 0
    mock_state.temperature = None
    mock_state.co2 = None
    mock_state.relative_humidity = None
    mock_state.temperature_1 = None
    mock_state.temperature_2 = None
    mock_state.temperature_3 = None
    try:
        stdlib_asyncio.run(sensor_loop.poll_sensor_loop(driver))
    except _StopAfterOne:
        pass


class FakeDriver:
    def __init__(self, values):
        self._values = values
    def read(self):
        return self._values


class TestPollSensorLoop:
    def test_writes_temperature_to_state(self):
        _run_one_iteration(FakeDriver({"temperature": 25.0}))
        assert mock_state.temperature == 25.0

    def test_writes_co2_to_state(self):
        _run_one_iteration(FakeDriver({"co2": 800.0}))
        assert mock_state.co2 == 800.0

    def test_writes_relative_humidity_to_state(self):
        _run_one_iteration(FakeDriver({"relative_humidity": 85.0}))
        assert mock_state.relative_humidity == 85.0

    def test_writes_pct_temperatures_to_state(self):
        _run_one_iteration(FakeDriver({
            "temperature_1": 21.0, "temperature_2": 22.0, "temperature_3": 23.0
        }))
        assert mock_state.temperature_1 == 21.0
        assert mock_state.temperature_2 == 22.0
        assert mock_state.temperature_3 == 23.0

    def test_absent_keys_write_none(self):
        mock_state.temperature = 99.0
        _run_one_iteration(FakeDriver({}))
        assert mock_state.temperature is None

    def test_partial_readings_write_none_for_absent(self):
        _run_one_iteration(FakeDriver({"temperature": 20.0}))
        assert mock_state.temperature == 20.0
        assert mock_state.co2 is None
        assert mock_state.relative_humidity is None
```

- [ ] **Step 2: Run — expect failure**

```bash
uv run pytest tests/test_sensor_loop.py -v
```

Expected: `TypeError` or `AttributeError` — `poll_sensor_loop` doesn't accept a driver argument yet.

- [ ] **Step 3: Rewrite `src/tasks/sensor_loop.py`**

Remove all module-level hardware imports (`machine`, `vendor.scd4x`, `vendor.pct2075`) and all sensor init code. Replace the body:

```python
import uasyncio as asyncio

from shared_state import state
from lib.logger import get_logger
from config import POLL_INTERVAL_SECONDS

logger = get_logger("sensor")


async def poll_sensor_loop(sensor_driver):
    """Periodically read sensors via the provided driver and write to SystemState."""
    while True:
        try:
            readings = sensor_driver.read()
            state.temperature = readings.get("temperature")
            state.co2 = readings.get("co2")
            state.relative_humidity = readings.get("relative_humidity")
            state.temperature_1 = readings.get("temperature_1")
            state.temperature_2 = readings.get("temperature_2")
            state.temperature_3 = readings.get("temperature_3")
        except Exception as e:
            logger.error("Sensor read error: %s", e)

        await asyncio.sleep(POLL_INTERVAL_SECONDS)
```

- [ ] **Step 4: Run sensor_loop tests — expect pass**

```bash
uv run pytest tests/test_sensor_loop.py -v
```

Expected: all 6 tests pass.

- [ ] **Step 5: Run full suite**

```bash
make test
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/tasks/sensor_loop.py tests/test_sensor_loop.py
git commit -m "feat: refactor sensor_loop to accept driver parameter, remove hardware imports"
```

---

## Task 5: Refactor `relay_loop.py` — test first

**Files:**
- Create: `tests/test_relay_loop.py`
- Modify: `src/tasks/relay_loop.py`

- [ ] **Step 1: Create `tests/test_relay_loop.py` with failing tests**

```python
import sys
import os
import types
import asyncio as stdlib_asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

_sleep_call_count = 0

class _StopAfterOne(Exception):
    pass

class _MockAsyncio:
    async def sleep(self, s):
        global _sleep_call_count
        _sleep_call_count += 1
        if _sleep_call_count >= 1:
            raise _StopAfterOne()

sys.modules['uasyncio'] = _MockAsyncio()

mock_logger = types.SimpleNamespace(
    debug=lambda *a, **k: None,
    info=lambda *a, **k: None,
    warning=lambda *a, **k: None,
    error=lambda *a, **k: None,
)
sys.modules['lib'] = types.ModuleType('lib')
sys.modules['lib.logger'] = types.SimpleNamespace(get_logger=lambda name: mock_logger)

mock_state = types.SimpleNamespace(
    heater_on=False,
    fan_on=False,
    humidifier_on=False,
)
sys.modules['shared_state'] = types.SimpleNamespace(state=mock_state)

import importlib
relay_loop = importlib.import_module('src.tasks.relay_loop')


class RecordingRelayDriver:
    def __init__(self):
        self.calls = []
    def set_heater(self, on): self.calls.append(("heater", on))
    def set_fan(self, on): self.calls.append(("fan", on))
    def set_humidifier(self, on): self.calls.append(("humidifier", on))


def _run_one_iteration(driver):
    global _sleep_call_count
    _sleep_call_count = 0
    try:
        stdlib_asyncio.run(relay_loop.poll_relay_loop(driver))
    except _StopAfterOne:
        pass


class TestPollRelayLoop:
    def setup_method(self):
        mock_state.heater_on = False
        mock_state.fan_on = False
        mock_state.humidifier_on = False

    def test_calls_set_heater_when_state_changes_to_on(self):
        mock_state.heater_on = True
        driver = RecordingRelayDriver()
        _run_one_iteration(driver)
        assert ("heater", True) in driver.calls

    def test_calls_set_fan_when_state_changes_to_on(self):
        mock_state.fan_on = True
        driver = RecordingRelayDriver()
        _run_one_iteration(driver)
        assert ("fan", True) in driver.calls

    def test_calls_set_humidifier_when_state_changes_to_on(self):
        mock_state.humidifier_on = True
        driver = RecordingRelayDriver()
        _run_one_iteration(driver)
        assert ("humidifier", True) in driver.calls

    def test_no_call_when_state_unchanged(self):
        """All state False (default) — loop starts with last_* = False, no change, no calls."""
        driver = RecordingRelayDriver()
        _run_one_iteration(driver)
        assert driver.calls == []

    def test_does_not_duplicate_call_when_state_unchanged_after_first_change(self):
        """After set_heater(True) fires, a second iteration with no change should not re-fire."""
        mock_state.heater_on = True
        driver = RecordingRelayDriver()

        # Run two iterations by allowing sleep to fire twice before stopping
        global _sleep_call_count
        _sleep_call_count = -1  # stop on 2nd sleep (count 0 and 1)

        class _StopAfterTwo(Exception):
            pass

        original_sleep = relay_loop.asyncio.sleep

        async def two_shot_sleep(s):
            global _sleep_call_count
            _sleep_call_count += 1
            if _sleep_call_count >= 1:
                raise _StopAfterTwo()

        relay_loop.asyncio.sleep = two_shot_sleep
        try:
            stdlib_asyncio.run(relay_loop.poll_relay_loop(driver))
        except _StopAfterTwo:
            pass
        finally:
            relay_loop.asyncio.sleep = original_sleep
            _sleep_call_count = 0

        # set_heater(True) fires exactly once (on first iteration); second iteration sees no change
        heater_calls = [c for c in driver.calls if c[0] == "heater"]
        assert heater_calls == [("heater", True)]
```

- [ ] **Step 2: Run — expect failure**

```bash
uv run pytest tests/test_relay_loop.py -v
```

Expected: `ImportError` or `AttributeError` — `relay_loop.py` has no `poll_relay_loop`.

- [ ] **Step 3: Rewrite `src/tasks/relay_loop.py`**

Replace the entire file:

```python
import uasyncio as asyncio

from shared_state import state
from lib.logger import get_logger

logger = get_logger("relay")


async def poll_relay_loop(relay_driver):
    """Monitor SystemState and toggle relays via the provided driver on state changes."""
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

- [ ] **Step 4: Run relay_loop tests — expect pass**

```bash
uv run pytest tests/test_relay_loop.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Run full suite**

```bash
make test
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/tasks/relay_loop.py tests/test_relay_loop.py
git commit -m "feat: replace RelayController singleton with poll_relay_loop free function"
```

---

## Task 6: Create `api_debug.py` — test first

**Files:**
- Create: `tests/test_api_debug.py`
- Create: `src/api_debug.py`

- [ ] **Step 1: Create `tests/test_api_debug.py` with failing tests**

```python
import sys
import os
import types
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ujson is MicroPython-only — alias CPython's json for host-side tests
sys.modules['ujson'] = json

mock_logger = types.SimpleNamespace(
    debug=lambda *a, **k: None,
    info=lambda *a, **k: None,
    warning=lambda *a, **k: None,
    error=lambda *a, **k: None,
)
sys.modules['lib'] = types.ModuleType('lib')
sys.modules['lib.logger'] = types.SimpleNamespace(get_logger=lambda name: mock_logger)

# Minimal Microdot mock — just enough to capture registered routes
class MockResponse:
    def __init__(self, body, status_code=200, headers=None):
        self.body = body
        self.status_code = status_code
        self.headers = headers or {}

sys.modules['vendor'] = types.ModuleType('vendor')
mock_microdot = types.ModuleType('vendor.microdot')
mock_microdot.Response = MockResponse
sys.modules['vendor.microdot'] = mock_microdot

import importlib
api_debug = importlib.import_module('src.api_debug')


class MockRequest:
    def __init__(self, body_dict):
        self.json = body_dict


class MockApp:
    def __init__(self):
        self._put = {}
        self._delete = {}
    def put(self, path):
        def decorator(fn):
            self._put[path] = fn
            return fn
        return decorator
    def delete(self, path):
        def decorator(fn):
            self._delete[path] = fn
            return fn
        return decorator


import asyncio as stdlib_asyncio


class TestApiDebugValidation:
    def setup_method(self):
        self.app = MockApp()
        self.driver = type('Driver', (), {'values': {}})()
        api_debug.register_debug_routes(self.app, self.driver)
        self.put_handler = self.app._put["/api/debug/state"]
        self.delete_handler = self.app._delete["/api/debug/state"]

    def test_valid_keys_update_driver_values(self):
        req = MockRequest({"temperature": 25.0, "co2": 800})
        resp = stdlib_asyncio.run(self.put_handler(req))
        assert self.driver.values["temperature"] == 25.0
        assert self.driver.values["co2"] == 800

    def test_unknown_key_returns_400(self):
        req = MockRequest({"temperture": 25.0})  # typo
        resp = stdlib_asyncio.run(self.put_handler(req))
        assert resp.status_code == 400
        data = json.loads(resp.body)
        assert data["ok"] is False
        assert "temperture" in data["error"]

    def test_unknown_key_does_not_update_driver(self):
        self.driver.values.clear()
        req = MockRequest({"bad_key": 1.0})
        stdlib_asyncio.run(self.put_handler(req))
        assert self.driver.values == {}

    def test_empty_body_is_valid(self):
        req = MockRequest({})
        resp = stdlib_asyncio.run(self.put_handler(req))
        assert resp.status_code == 200

    def test_delete_clears_driver_values(self):
        self.driver.values["temperature"] = 25.0
        req = MockRequest(None)
        resp = stdlib_asyncio.run(self.delete_handler(req))
        assert self.driver.values == {}

    def test_delete_returns_ok(self):
        req = MockRequest(None)
        resp = stdlib_asyncio.run(self.delete_handler(req))
        data = json.loads(resp.body)
        assert data["ok"] is True

    def test_valid_keys_set_is_complete(self):
        expected = {
            "temperature", "co2", "relative_humidity",
            "temperature_1", "temperature_2", "temperature_3"
        }
        assert api_debug.VALID_KEYS == expected
```

- [ ] **Step 2: Run — expect ImportError**

```bash
uv run pytest tests/test_api_debug.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.api_debug'`

- [ ] **Step 3: Create `src/api_debug.py`**

```python
import ujson as json

from vendor.microdot import Response
from lib.logger import get_logger

logger = get_logger("api_debug")

VALID_KEYS = {
    "temperature", "co2", "relative_humidity",
    "temperature_1", "temperature_2", "temperature_3",
}


def register_debug_routes(app, sensor_driver):
    @app.put("/api/debug/state")
    async def set_debug_state(request):
        data = request.json or {}
        unknown = set(data.keys()) - VALID_KEYS
        if unknown:
            return Response(
                body=json.dumps({"ok": False, "error": f"Unknown keys: {sorted(unknown)}"}),
                status_code=400,
                headers={"Content-Type": "application/json"},
            )
        sensor_driver.values.update(data)
        return Response(
            body=json.dumps({"ok": True}),
            headers={"Content-Type": "application/json"},
        )

    @app.delete("/api/debug/state")
    async def clear_debug_state(request):
        sensor_driver.values.clear()
        return Response(
            body=json.dumps({"ok": True}),
            headers={"Content-Type": "application/json"},
        )
```

- [ ] **Step 4: Run api_debug tests — expect pass**

```bash
uv run pytest tests/test_api_debug.py -v
```

Expected: all 7 tests pass.

- [ ] **Step 5: Run full suite**

```bash
make test
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/api_debug.py tests/test_api_debug.py
git commit -m "feat: add api_debug.py with PUT/DELETE /api/debug/state endpoints"
```

---

## Task 7: Update `main.py` to wire drivers and debug routes

**Files:**
- Modify: `src/main.py`

No new tests — this is wiring code verified by running on device in debug mode.

- [ ] **Step 1: Update `src/main.py`**

Make these changes (shown as before/after for each section):

**Remove** the old imports (lines 13 and 15 — both are replaced):
```python
from tasks.sensor_loop import poll_sensor_loop  # REMOVE — replaced below
from tasks.relay_loop import relay_controller   # REMOVE — replaced below
```

**Add** after the existing imports block, before `WEB_SERVER_PORT = ...`:
```python
from hardware import get_sensor_driver, get_relay_driver
from tasks.sensor_loop import poll_sensor_loop
from tasks.relay_loop import poll_relay_loop
from config import DEBUG_MODE
```

**Inside `async def main():`**, add driver instantiation at the top of the function body (before the `logger.info("Initializing system tasks...")` line) so that `safe_task` can catch and recover from hardware init failures:
```python
sensor_driver = get_sensor_driver()
relay_driver = get_relay_driver()

if DEBUG_MODE:
    from api_debug import register_debug_routes
    register_debug_routes(app, sensor_driver)
```

> **Why inside `main()`:** `RealSensorDriver.__init__()` calls I2C hardware. If it raises, placing instantiation inside `main()` allows the exception to propagate to `asyncio.run(main())` which triggers `machine.reset()` — same recovery path as today. Module-level placement would crash before `safe_task` or the event loop is active.

**Still inside `main():`**, replace the old Sensor and Relay task lines:
```python
# REMOVE:
asyncio.create_task(safe_task("Sensor", poll_sensor_loop))
asyncio.create_task(safe_task("Relay", relay_controller.relay_loop))

# REPLACE WITH:
asyncio.create_task(safe_task("Sensor", lambda: poll_sensor_loop(sensor_driver)))
asyncio.create_task(safe_task("Relay", lambda: poll_relay_loop(relay_driver)))
```

- [ ] **Step 2: Run full test suite**

```bash
make test
```

Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add src/main.py
git commit -m "feat: wire hardware drivers in main.py, register debug routes in DEBUG_MODE"
```

---

## Task 8: `tools/tail_log.py` and Makefile

**Files:**
- Create: `tools/tail_log.py`
- Modify: `Makefile`

- [ ] **Step 1: Create `tools/tail_log.py`**

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

- [ ] **Step 2: Update `Makefile`**

Add `logs/` to the `flash` target's mkdir block (after the last `mkdir` line):
```makefile
	$(MPREMOTE) connect $(DEVICE) fs mkdir $(BOARD_PATH)/logs || true
```

Add three new targets after the `clean` target:
```makefile
repl:
	$(MPREMOTE) connect $(DEVICE) repl

logs:
	$(MPREMOTE) connect $(DEVICE) run tools/tail_log.py

restart:
	$(MPREMOTE) connect $(DEVICE) exec "import machine; machine.soft_reset()"
```

Also add them to the `.PHONY` line:
```makefile
.PHONY: all sync lint format typecheck test flash flash-clean clean repl logs restart
```

- [ ] **Step 3: Run full suite**

```bash
make test
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add tools/tail_log.py Makefile
git commit -m "feat: add tail_log.py and repl/logs/restart Makefile targets"
```

---

## Task 9: Update `config_local.example.py` and `CLAUDE.md`

**Files:**
- Modify: `src/config_local.example.py`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update `src/config_local.example.py`**

Add after the existing ThingSpeak block:

```python
# Debug mode — set to True when testing without real hardware (no sensors or relays attached)
# DEBUG_MODE = True

# Device IP — used as a shell variable, not read by app code.
# After boot, find it via: mpremote exec "import network; w=network.WLAN(); print(w.ifconfig())"
# Then: export DEVICE_IP=192.168.x.x
# DEVICE_IP = "192.168.x.x"
```

- [ ] **Step 2: Update `CLAUDE.md` — add Hardware Testing section**

Add a new section after the existing "Development Notes" section:

```markdown
## Hardware Testing

The board communicates over **USB** (via `mpremote`) for file upload, REPL access, and log tailing, and over **WiFi/HTTP** for dashboard interaction, API calls, and mock data injection.

### Configuration

In `src/config_local.py`:
```python
DEBUG_MODE = True  # disables real sensor/relay hardware
```

In your shell (find IP after boot with `make repl` → `import network; print(network.WLAN().ifconfig())`):
```sh
export DEVICE_IP=192.168.x.x
```

### Commands

| Action | Command |
|--------|---------|
| Upload files | `make flash` |
| Soft-reset board | `make restart` |
| Open REPL | `make repl` |
| Tail logs (USB) | `make logs` (Ctrl-C to stop; stop before `make restart`) |
| Read state | `curl http://$DEVICE_IP/api/metrics` |
| Open dashboard | `open http://$DEVICE_IP/` |

### Injecting mock sensor values (DEBUG_MODE only)

```sh
# Inject values — control loop reacts within 5s
curl -X PUT http://$DEVICE_IP/api/debug/state \
  -H 'Content-Type: application/json' \
  -d '{"temperature": 17.0, "co2": 1200, "relative_humidity": 85}'

# Read relay decisions
curl http://$DEVICE_IP/api/metrics
# → {"heater_on": true, "fan_on": true, "humidifier_on": true, ...}

# Clear mocks — heater turns OFF (safety fallback) until re-injected
curl -X DELETE http://$DEVICE_IP/api/debug/state
```

### Setting config via API

```sh
# Set thresholds
curl -X PUT http://$DEVICE_IP/api/ranges \
  -H 'Content-Type: application/json' \
  -d '{"temp": {"on": 18, "off": 22}, "co2": {"on": 900, "off": 700}}'

# Set device modes (auto | on | off)
curl -X PUT http://$DEVICE_IP/api/modes \
  -H 'Content-Type: application/json' \
  -d '{"fan": "on"}'
```

### Full deploy cycle

```sh
make flash && make restart
# Wait ~5s for boot, then:
make logs   # in a separate terminal
```

> **Note:** `make logs` and `make restart` both open the USB serial port. Stop `make logs` (Ctrl-C) before running `make restart`.
```

- [ ] **Step 3: Run full suite**

```bash
make test
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add src/config_local.example.py CLAUDE.md
git commit -m "docs: add DEBUG_MODE docs to config_local.example.py and hardware testing guide to CLAUDE.md"
```

---

## Final Verification

- [ ] **Run full test suite one last time**

```bash
make test
```

Expected: all tests pass with no warnings.

- [ ] **Lint check**

```bash
make lint
```

Fix any issues before marking complete.

- [ ] **Final commit summary**

Review `git log --oneline` — should show 9 commits since branch start, each self-contained.
