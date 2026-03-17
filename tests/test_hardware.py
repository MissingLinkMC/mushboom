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

import importlib  # noqa: E402
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
