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


def get_sensor_driver():
    from config import DEBUG_MODE
    return StubSensorDriver() if DEBUG_MODE else RealSensorDriver()


def get_relay_driver():
    from config import DEBUG_MODE
    return StubRelayDriver() if DEBUG_MODE else RealRelayDriver()
