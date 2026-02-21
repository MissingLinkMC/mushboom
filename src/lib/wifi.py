import machine
from vendor.wifi_manager import WifiManager

import config as app_config
from lib.logger import get_logger

WIFI_STATUS_LED_PIN = getattr(app_config, "WIFI_STATUS_LED_PIN", -1)

logger = get_logger("wifi")

class WiFi:
    def __init__(self):
        """Initialize WiFi class"""

        logger.info("Initializing WiFi manager")

        self.led = (
            machine.Pin(WIFI_STATUS_LED_PIN, machine.Pin.OUT)
            if WIFI_STATUS_LED_PIN >= 0
            else None
        )
        self._status = {
            "state": "disconnected",
            "ssid": None,
            "ip": None,
            "ap_name": None,
            "last_failures": None,
        }

        self.led_off()

    def led_off(self):
        if self.led:
            self.led.value(0)
            logger.info("WiFi status LED turned off")

    def led_on(self):
        if self.led:
            self.led.value(1)
            logger.info("WiFi status LED turned on")

    def connection_handler(self, event, **kwargs):
        """Handle WiFi connection state changes"""
        if event == "connected":
            self._status["state"] = "connected"
            self._status["ssid"] = kwargs.get("ssid")
            self._status["ip"] = kwargs.get("ip")
            logger.info(f"Connected to {self._status['ssid']} with IP {self._status['ip']}")

            self.led_on()  # Turn LED on to indicate connection

        elif event == "disconnected":
            self._status["state"] = "disconnected"
            self._status["ssid"] = None
            self._status["ip"] = None
            logger.warning("Lost WiFi connection")

            self.led_off()

        elif event == "ap_started":
            self._status["state"] = "ap_active"
            self._status["ap_name"] = kwargs.get("essid")
            logger.info(f"Started access point: {self._status['ap_name']}")

        elif event == "connection_failed":
            self._status["state"] = "connection_failed"
            self._status["last_failures"] = kwargs.get("attempted_networks", [])
            logger.error(f"Failed to connect to: {self._status['last_failures']}")

    def up(self):
        """Start WiFi management"""
        logger.info("Starting WiFi manager")
        WifiManager.on_connection_change(self.connection_handler)
        WifiManager.start_managing()

    def get_status(self):
        """Get current WiFi status and information

        Returns:
            dict: Status information with keys:
                - state: 'connected', 'disconnected', 'ap_active', 'connection_failed'
                - ssid: Connected network name (if connected)
                - ip: Assigned IP address (if connected)
                - ap_name: Access point name (if AP active)
                - last_failures: List of networks that failed connection attempts
        """

        # Return a copy to prevent external modification of internal state
        return dict(self._status)
