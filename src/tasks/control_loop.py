import uasyncio as asyncio
import time
from shared_state import state, config
from lib.logger import get_logger

logger = get_logger("control")

_fan_schedule_state = {
    "next_start": None,
    "active_until": None,
    "last_config": (None, None, None),
}


def _reset_fan_schedule_state():
    _fan_schedule_state["next_start"] = None
    _fan_schedule_state["active_until"] = None


def _fan_schedule_config_tuple():
    return (
        config.fan_schedule_enabled,
        max(1.0, float(config.fan_schedule_interval_minutes)),
        max(0.0, float(config.fan_schedule_duration_minutes)),
    )


def _fan_schedule_active():
    """Evaluate whether the fan should currently run because of the schedule."""
    enabled, interval_minutes, duration_minutes = _fan_schedule_config_tuple()

    if not enabled or duration_minutes <= 0:
        _reset_fan_schedule_state()
        _fan_schedule_state["last_config"] = (enabled, interval_minutes, duration_minutes)
        return False

    # Ensure duration cannot exceed interval
    duration_minutes = min(duration_minutes, interval_minutes)

    cfg_tuple = (True, interval_minutes, duration_minutes)
    if _fan_schedule_state["last_config"] != cfg_tuple:
        _reset_fan_schedule_state()
        _fan_schedule_state["last_config"] = cfg_tuple

    now = time.time()

    # Check if we are currently within an active run window
    active_until = _fan_schedule_state["active_until"]
    if active_until and now < active_until:
        return True
    elif active_until and now >= active_until:
        _fan_schedule_state["active_until"] = None

    # Initialize next_start if needed
    if _fan_schedule_state["next_start"] is None:
        _fan_schedule_state["next_start"] = now

    # Start a new run window if we've reached the next start time
    if now >= _fan_schedule_state["next_start"]:
        start_time = now
        _fan_schedule_state["active_until"] = start_time + (duration_minutes * 60)
        _fan_schedule_state["next_start"] = start_time + (interval_minutes * 60)
        logger.info(
            "Fan schedule - running for %.1f minutes (interval %.1f minutes)",
            duration_minutes,
            interval_minutes,
        )
        return True

    return False


async def control_loop():
    while True:
        control_heater()
        control_fan()
        control_humidifier()

        await asyncio.sleep(5)


def control_heater():
    """Control the heater based on temperature range or manual override.
    Uses all available temperature sensors to create a vertical temperature profile:
    - Turns on if ANY sensor reads below minimum temperature
    - Turns off if ALL sensors read above maximum temperature
    This ensures even heating throughout the growing space."""
    if config.heater_mode == "on":
        if not state.heater_on:
            logger.info("Heater turned ON (manual override)")
        state.heater_on = True
        return
    elif config.heater_mode == "off":
        if state.heater_on:
            logger.info("Heater turned OFF (manual override)")
        state.heater_on = False
        return

    # Collect all available temperature readings
    temps = []
    temp_sources = []
    if state.temperature is not None:  # SCD40 temperature
        temps.append(state.temperature)
        temp_sources.append("SCD40")
    if state.temperature_1 is not None:  # Top PCT2075
        temps.append(state.temperature_1)
        temp_sources.append("PCT2075 #1")
    if state.temperature_2 is not None:  # Middle PCT2075
        temps.append(state.temperature_2)
        temp_sources.append("PCT2075 #2")
    if state.temperature_3 is not None:  # Bottom PCT2075
        temps.append(state.temperature_3)
        temp_sources.append("PCT2075 #3")

    if not temps:  # No temperature readings available
        if state.heater_on:  # Only log if we're turning off due to no readings
            logger.warning("No temperature readings available - turning heater OFF")
            state.heater_on = False
        return

    min_temp = min(temps)  # Coldest spot
    max_temp = max(temps)  # Warmest spot
    min_idx = temps.index(min_temp)
    max_idx = temps.index(max_temp)

    if state.heater_on:
        # Heater is currently on, turn off only if the coldest spot is above off_temp
        if min_temp > config.off_temp:
            state.heater_on = False
            logger.info("Heater turned OFF - %s reports %.1f°C (above max %.1f°C). Range: %.1f°C to %.1f°C",
                       temp_sources[min_idx], min_temp, config.off_temp, min_temp, max_temp)
    else:
        # Heater is currently off, turn on if the warmest spot is below on_temp
        if max_temp < config.on_temp:
            state.heater_on = True
            logger.info("Heater turned ON - %s reports %.1f°C (below min %.1f°C). Range: %.1f°C to %.1f°C",
                       temp_sources[max_idx], max_temp, config.on_temp, min_temp, max_temp)


def control_fan():
    """Control the fan based on CO2 levels or manual override."""
    if config.fan_mode == "on":
        state.fan_on = True
        return
    elif config.fan_mode == "off":
        state.fan_on = False
        return

    schedule_active = _fan_schedule_active()
    if schedule_active:
        if not state.fan_on:
            logger.info("Fan turned ON (schedule)")
        state.fan_on = True
        return

    if state.co2 is not None:
        if state.fan_on:
            # Fan is currently on, turn off only if CO2 drops below off_co2 (min)
            if state.co2 < config.off_co2:
                state.fan_on = False
        else:
            # Fan is currently off, turn on if CO2 rises above on_co2 (max)
            if state.co2 > config.on_co2:
                state.fan_on = True


def control_humidifier():
    """Control the humidifier based on humidity range or manual override."""
    if config.humidifier_mode == "on":
        state.humidifier_on = True
        return
    elif config.humidifier_mode == "off":
        state.humidifier_on = False
        return

    if state.relative_humidity is not None:
        if state.humidifier_on:
            # Humidifier is currently on, turn off only if above off_humidity (max)
            if state.relative_humidity > config.off_humidity:
                state.humidifier_on = False
        else:
            # Humidifier is currently off, turn on if below on_humidity (min)
            if state.relative_humidity < config.on_humidity:
                state.humidifier_on = True
