import uasyncio as asyncio
from shared_state import state
from lib.thingspeak import ThingSpeak
from lib.logger import get_logger
from config import THINGSPEAK_API_KEY, THINGSPEAK_ENABLED, POLL_INTERVAL_SECONDS

logger = get_logger("thingspeak")
thingspeak = ThingSpeak(THINGSPEAK_API_KEY) if THINGSPEAK_ENABLED else None

async def thingspeak_loop():
    """Periodically send sensor and device state data to ThingSpeak."""
    if not thingspeak:
        logger.info("ThingSpeak integration disabled")
        return

    while True:
        try:
            # Prepare data fields
            fields = {}

            # Add sensor readings if available
            if state.co2 is not None:
                fields["1"] = state.co2
            if state.temperature is not None:
                fields["2"] = state.temperature
            if state.relative_humidity is not None:
                fields["3"] = state.relative_humidity

            # Add device states
            fields["4"] = 1 if state.heater_on else 0
            fields["5"] = 1 if state.fan_on else 0
            fields["6"] = 1 if state.humidifier_on else 0

            # Add additional temperature sensors
            if state.temperature_1 is not None:
                fields["7"] = state.temperature_1
            if state.temperature_2 is not None:
                fields["8"] = state.temperature_2

            # Send update if we have any data
            if fields:
                thingspeak.send_update(**fields)

        except Exception as e:
            logger.error("ThingSpeak update error: %s", e)

        # Wait for next polling interval
        await asyncio.sleep(POLL_INTERVAL_SECONDS)