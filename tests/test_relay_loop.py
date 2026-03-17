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
