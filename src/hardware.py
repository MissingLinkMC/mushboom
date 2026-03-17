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
    pass  # implemented in Task 3


class RealRelayDriver:
    pass  # implemented in Task 3


def get_sensor_driver():
    from config import DEBUG_MODE
    return StubSensorDriver() if DEBUG_MODE else RealSensorDriver()


def get_relay_driver():
    from config import DEBUG_MODE
    return StubRelayDriver() if DEBUG_MODE else RealRelayDriver()
