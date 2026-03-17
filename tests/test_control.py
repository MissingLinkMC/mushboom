import unittest
import sys
import types
import os
import importlib

# Add the parent directory to sys.path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock MicroPython modules
class AsyncioMock:
    async def sleep(self, seconds):
        pass

sys.modules['uasyncio'] = AsyncioMock()

# Mock lib.logger
mock_logger = types.SimpleNamespace(
    debug=lambda *a, **k: None,
    info=lambda *a, **k: None,
    warning=lambda *a, **k: None,
    error=lambda *a, **k: None,
)
sys.modules['lib'] = types.ModuleType('lib')
sys.modules['lib.logger'] = types.SimpleNamespace(get_logger=lambda name: mock_logger)

# Mock shared_state module
mock_state = types.SimpleNamespace(
    temperature=None,
    temperature_1=None,
    temperature_2=None,
    temperature_3=None,
    heater_on=False,
    co2=None,
    fan_on=False,
    relative_humidity=None,
    humidifier_on=False,
)
mock_config = types.SimpleNamespace(
    on_temp=18,
    off_temp=22,
    on_co2=1000,
    off_co2=800,
    on_humidity=60,
    off_humidity=80,
    heater_mode="auto",
    fan_mode="auto",
    humidifier_mode="auto",
    fan_schedule_enabled=False,
    fan_schedule_interval_minutes=60,
    fan_schedule_duration_minutes=5,
)

sys.modules["shared_state"] = types.SimpleNamespace(
    state=mock_state, config=mock_config
)

control = importlib.import_module("src.tasks.control_loop")


class TestControlLogic(unittest.TestCase):
    def setUp(self):
        mock_state.temperature = None
        mock_state.temperature_1 = None
        mock_state.temperature_2 = None
        mock_state.temperature_3 = None
        mock_state.heater_on = False
        mock_state.co2 = None
        mock_state.fan_on = False
        mock_state.relative_humidity = None
        mock_state.humidifier_on = False

    def test_heater_hysteresis(self):
        # Heater should turn on below on_temp
        mock_state.temperature = 17
        mock_state.heater_on = False
        control.control_heater()
        self.assertTrue(mock_state.heater_on)
        # Heater should stay on until above off_temp
        mock_state.temperature = 21
        control.control_heater()
        self.assertTrue(mock_state.heater_on)
        # Heater should turn off above off_temp
        mock_state.temperature = 23
        control.control_heater()
        self.assertFalse(mock_state.heater_on)

    def test_fan_hysteresis(self):
        # Fan should turn on above on_co2
        mock_state.co2 = 1200
        mock_state.fan_on = False
        control.control_fan()
        self.assertTrue(mock_state.fan_on)
        # Fan should stay on until below off_co2
        mock_state.co2 = 900
        control.control_fan()
        self.assertTrue(mock_state.fan_on)
        # Fan should turn off below off_co2
        mock_state.co2 = 700
        control.control_fan()
        self.assertFalse(mock_state.fan_on)

    def test_humidifier_hysteresis(self):
        # Humidifier should turn on below on_humidity
        mock_state.relative_humidity = 50
        mock_state.humidifier_on = False
        control.control_humidifier()
        self.assertTrue(mock_state.humidifier_on)
        # Humidifier should stay on until above off_humidity
        mock_state.relative_humidity = 70
        control.control_humidifier()
        self.assertTrue(mock_state.humidifier_on)
        # Humidifier should turn off above off_humidity
        mock_state.relative_humidity = 85
        control.control_humidifier()
        self.assertFalse(mock_state.humidifier_on)


if __name__ == "__main__":
    unittest.main()
