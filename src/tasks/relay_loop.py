from machine import Pin
import uasyncio as asyncio

from config import FAN_RELAY_PIN, HEATER_RELAY_PIN, HUMIDIFIER_RELAY_PIN
from shared_state import state


class RelayController:
    """
    Class to manage GPIO pins for relays based on system state changes.
    Listens to state changes and toggles pins accordingly.
    """

    def __init__(self):
        # Initialize GPIO pins for relay control
        self.heater_pin = Pin(HEATER_RELAY_PIN, Pin.OUT)
        self.fan_pin = Pin(FAN_RELAY_PIN, Pin.OUT)
        self.humidifier_pin = Pin(HUMIDIFIER_RELAY_PIN, Pin.OUT)

        # Initialize pins to OFF state (relays are typically active LOW)
        self.heater_pin.value(1)  # 1 = OFF for active LOW relay
        self.fan_pin.value(1)  # 1 = OFF for active LOW relay
        self.humidifier_pin.value(1)  # 1 = OFF for active LOW relay

        # Keep track of last states to detect changes
        self.last_heater_state = False
        self.last_fan_state = False
        self.last_humidifier_state = False

    async def relay_loop(self):
        """Continuously monitor state changes and toggle relays accordingly."""
        while True:
            # Check for heater state change
            if state.heater_on != self.last_heater_state:
                self.toggle_heater(state.heater_on)
                self.last_heater_state = state.heater_on

            # Check for fan state change
            if state.fan_on != self.last_fan_state:
                self.toggle_fan(state.fan_on)
                self.last_fan_state = state.fan_on

            # Check for humidifier state change
            if state.humidifier_on != self.last_humidifier_state:
                self.toggle_humidifier(state.humidifier_on)
                self.last_humidifier_state = state.humidifier_on

            # Longer delay to prevent excessive CPU usage
            await asyncio.sleep(5)

    def toggle_heater(self, on):
        """Toggle heater relay."""
        self.heater_pin.value(0 if on else 1)

    def toggle_fan(self, on):
        """Toggle fan relay."""
        self.fan_pin.value(0 if on else 1)

    def toggle_humidifier(self, on):
        """Toggle humidifier relay."""
        self.humidifier_pin.value(0 if on else 1)


# Create a singleton instance for use in main
relay_controller = RelayController()
