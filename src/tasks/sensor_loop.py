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
