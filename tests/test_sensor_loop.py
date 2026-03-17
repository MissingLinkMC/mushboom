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

if 'config' in sys.modules:
    mock_config = sys.modules['config']
else:
    mock_config = types.ModuleType('config')
    sys.modules['config'] = mock_config
mock_config.POLL_INTERVAL_SECONDS = 30
mock_config.DEBUG_MODE = False

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
