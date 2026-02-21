import uasyncio as asyncio
from machine import I2C, Pin

from shared_state import state
from vendor.scd4x import SCD4X
from vendor.pct2075 import PCT2075
from lib.logger import get_logger
from config import (
    SCD4X_I2C_SCL_PIN,
    POLL_INTERVAL_SECONDS,
    SCD4X_I2C_FREQ,
    SCD4X_I2C_SDA_PIN,
    QT_POWER_PIN,
    SCD4X_I2C_BUS,
    PCT2075_I2C_BUS_0,
    PCT2075_I2C_BUS_1,
    PCT2075_I2C_BUS_2,
    PCT2075_I2C_SDA_PIN_0,
    PCT2075_I2C_SCL_PIN_0,
    PCT2075_I2C_ADDR_0,
    PCT2075_I2C_SDA_PIN_1,
    PCT2075_I2C_SCL_PIN_1,
    PCT2075_I2C_ADDR_1,
    PCT2075_I2C_SDA_PIN_2,
    PCT2075_I2C_SCL_PIN_2,
    PCT2075_I2C_ADDR_2,
)

logger = get_logger("sensor")


async def poll_sensor_loop():
    """Periodically read CO2, temperature, and humidity from the sensor."""

    # Initialize sensors
    scd4x = None
    pct2075_sensors = []

    try:
        # Initialize QT power pin if enabled (pin > -1)
        if QT_POWER_PIN > -1:
            qtpwr = Pin(QT_POWER_PIN, Pin.OUT)
            qtpwr.value(1)   # turn on QT port power
            logger.info("QT port power enabled on pin %d", QT_POWER_PIN)

        # Initialize SCD4X on its configured I2C bus
        i2c_scd4x = I2C(
            SCD4X_I2C_BUS,
            sda=Pin(SCD4X_I2C_SDA_PIN),
            scl=Pin(SCD4X_I2C_SCL_PIN),
            freq=SCD4X_I2C_FREQ,
        )
        logger.info("Initializing SCD4X on I2C bus %d (SDA pin %d, SCL pin %d)",
                   SCD4X_I2C_BUS, SCD4X_I2C_SDA_PIN, SCD4X_I2C_SCL_PIN)
        logger.info("I2C devices found on bus %d: %s", SCD4X_I2C_BUS, i2c_scd4x.scan())
        scd4x = SCD4X(i2c_scd4x)
        scd4x.start_periodic_measurement()
        logger.info("SCD4X sensor initialized successfully")

        # Initialize PCT2075 sensors if enabled
        pct2075_configs = [
            (PCT2075_I2C_BUS_0, PCT2075_I2C_SDA_PIN_0, PCT2075_I2C_SCL_PIN_0, PCT2075_I2C_ADDR_0),
            (PCT2075_I2C_BUS_1, PCT2075_I2C_SDA_PIN_1, PCT2075_I2C_SCL_PIN_1, PCT2075_I2C_ADDR_1),
            (PCT2075_I2C_BUS_2, PCT2075_I2C_SDA_PIN_2, PCT2075_I2C_SCL_PIN_2, PCT2075_I2C_ADDR_2),
        ]

        for i, (i2c_bus, sda_pin, scl_pin, addr) in enumerate(pct2075_configs):
            if sda_pin > -1 or scl_pin > -1:
                try:
                    i2c = I2C(i2c_bus,
                             sda=Pin(sda_pin),
                             scl=Pin(scl_pin),
                             freq=100000)
                    sensor = PCT2075(i2c, address=addr)
                    pct2075_sensors.append(sensor)
                    logger.info(f"PCT2075 sensor {i+1} initialized successfully on I2C bus {i2c_bus} (SDA pin {sda_pin}, SCL pin {scl_pin})")
                except Exception as e:
                    logger.error(f"PCT2075 sensor {i+1} init failed: {e}")
                    pct2075_sensors.append(None)
            else:
                pct2075_sensors.append(None)

    except Exception as e:
        logger.error("Main sensor init failed: %s", e)
        return

    while True:
        try:
            # Read SCD4X sensor
            if scd4x:
                # Only read sensor if it has data ready (more power efficient)
                if scd4x.data_ready:
                    state.co2 = scd4x.co2  # type: ignore
                    state.temperature = scd4x.temperature  # type: ignore
                    state.relative_humidity = scd4x.relative_humidity  # type: ignore
                    logger.debug(
                        "SCD4X data updated: CO2=%s, Temp=%s, RH=%s",
                        state.co2,
                        state.temperature,
                        state.relative_humidity,
                    )

            # Read PCT2075 temperature sensors
            for i, sensor in enumerate(pct2075_sensors):
                if sensor:
                    try:
                        temp = sensor.temperature
                        if i == 0:
                            state.temperature_1 = temp
                        elif i == 1:
                            state.temperature_2 = temp
                        elif i == 2:
                            state.temperature_3 = temp
                        logger.debug(f"PCT2075 sensor {i+1} temperature: {temp}°C")
                    except Exception as e:
                        logger.error(f"PCT2075 sensor {i+1} read error: {e}")

        except Exception as e:
            logger.error("Sensor error: %s", e)

        # Wait for next polling interval
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
