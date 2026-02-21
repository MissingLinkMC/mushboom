import ujson as json
import os

from lib.logger import get_logger


class SystemState:
    def __init__(self) -> None:
        self.temperature = None
        self.relative_humidity = None
        self.co2 = None
        self.temperature_1 = None  # PCT2075 sensor 1
        self.temperature_2 = None  # PCT2075 sensor 2
        self.temperature_3 = None  # PCT2075 sensor 3
        self.fan_on = False
        self.humidifier_on = False
        self.heater_on = False

    def as_dict(self) -> dict:
        return {
            "temperature": self.temperature,
            "relative_humidity": self.relative_humidity,
            "co2": self.co2,
            "temperature_1": self.temperature_1,
            "temperature_2": self.temperature_2,
            "temperature_3": self.temperature_3,
            "fan_on": self.fan_on,
            "humidifier_on": self.humidifier_on,
            "heater_on": self.heater_on,
        }

    def __repr__(self) -> str:
        return f"<SystemState T={self.temperature} RH={self.relative_humidity} CO2={self.co2} fan={self.fan_on} humid={self.humidifier_on} heat={self.heater_on}>"


class AppConfig:
    def __init__(self) -> None:
        self.on_temp = 24.0
        self.off_temp = 26.0
        self.on_humidity = 86.0
        self.off_humidity = 90.0
        self.on_co2 = 900.0
        self.off_co2 = 700.0

        # Default device modes for overriding
        self.heater_mode = "auto"
        self.fan_mode = "auto"
        self.humidifier_mode = "auto"

        # Fan schedule defaults
        self.fan_schedule_enabled = False
        self.fan_schedule_interval_minutes = 60.0  # Run every 60 minutes
        self.fan_schedule_duration_minutes = 5.0   # for 5 minutes

        self._config_path = "config.json"
        self.load()

    def as_dict(self) -> dict:
        return {
            "on_temp": self.on_temp,
            "off_temp": self.off_temp,
            "on_humidity": self.on_humidity,
            "off_humidity": self.off_humidity,
            "on_co2": self.on_co2,
            "off_co2": self.off_co2,
            "heater_mode": self.heater_mode,
            "fan_mode": self.fan_mode,
            "humidifier_mode": self.humidifier_mode,
            "fan_schedule_enabled": self.fan_schedule_enabled,
            "fan_schedule_interval_minutes": self.fan_schedule_interval_minutes,
            "fan_schedule_duration_minutes": self.fan_schedule_duration_minutes,
        }

    def save(self):
        data = self.as_dict()
        with open(self._config_path, "w") as f:
            json.dump(data, f)

    def load(self):
        logger = get_logger("AppConfig")
        try:
            try:
                os.stat(self._config_path)
            except OSError:
                return  # file does not exist
            with open(self._config_path, "r") as f:
                data = json.load(f)
            self.on_temp = float(data.get("on_temp", self.on_temp))
            self.off_temp = float(data.get("off_temp", self.off_temp))
            self.on_humidity = float(data.get("on_humidity", self.on_humidity))
            self.off_humidity = float(data.get("off_humidity", self.off_humidity))
            self.on_co2 = float(data.get("on_co2", self.on_co2))
            self.off_co2 = float(data.get("off_co2", self.off_co2))

            # Load device mode settings
            self.heater_mode = data.get("heater_mode", self.heater_mode)
            self.fan_mode = data.get("fan_mode", self.fan_mode)
            self.humidifier_mode = data.get("humidifier_mode", self.humidifier_mode)

            # Fan schedule settings
            self.fan_schedule_enabled = bool(
                data.get("fan_schedule_enabled", self.fan_schedule_enabled)
            )
            self.fan_schedule_interval_minutes = float(
                data.get(
                    "fan_schedule_interval_minutes",
                    self.fan_schedule_interval_minutes,
                )
            )
            self.fan_schedule_duration_minutes = float(
                data.get(
                    "fan_schedule_duration_minutes",
                    self.fan_schedule_duration_minutes,
                )
            )
        except Exception as e:
            logger.error("Failed to load config: %s", e)

    def __repr__(self) -> str:
        return (
            f"<AppConfig T={self.on_temp}-{self.off_temp} "
            f"RH={self.on_humidity}-{self.off_humidity} "
            f"CO2={self.on_co2}-{self.off_co2} "
            f"Modes: H={self.heater_mode} F={self.fan_mode} Hum={self.humidifier_mode} "
            f"FanSchedule: enabled={self.fan_schedule_enabled} every={self.fan_schedule_interval_minutes}m "
            f"for={self.fan_schedule_duration_minutes}m>"
        )


# global singletons
state = SystemState()
config = AppConfig()
