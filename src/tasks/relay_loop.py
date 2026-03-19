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
