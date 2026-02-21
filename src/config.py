# Controller configuration

# Units
USE_FAHRENHEIT = True  # Set to True for Fahrenheit, False for Celsius

WIFI_STATUS_LED_PIN = 13  # Use -1 to disable status led

# ThingSpeak configuration
THINGSPEAK_API_KEY = ""  # Set in config_local.py
THINGSPEAK_ENABLED = False  # Set to True to enable ThingSpeak integration
THINGSPEAK_CHANNEL_ID = 0  # Set in config_local.py

# GPIO pins for relay control
HEATER_RELAY_PIN = 5
FAN_RELAY_PIN = 6
HUMIDIFIER_RELAY_PIN = 9

# NTP configuration
NTP_SERVER = "time.google.com"  # Default NTP server

# Web server configuration
WEB_SERVER_PORT = 80  # Standard HTTP port for the web server
WEB_SERVER_HOST = "0.0.0.0"  # Using 0.0.0.0 to check on all interfaces

# SDC Sensor Pin configuration
SCD4X_I2C_BUS = 1  # I2C bus number for SCD4X sensor
SCD4X_I2C_SDA_PIN = 3 # Blue wire
SCD4X_I2C_SCL_PIN = 4 # Yellow wire
SCD4X_I2C_FREQ = 100000

# PCT2075 I2C configuration (up to 3 optional sensors, -1 to disable)
PCT2075_I2C_BUS_0 = SCD4X_I2C_BUS  # I2C bus number for first PCT2075 sensor
PCT2075_I2C_SDA_PIN_0 = SCD4X_I2C_SDA_PIN  # Blue wire
PCT2075_I2C_SCL_PIN_0 = SCD4X_I2C_SCL_PIN  # Yellow wire
PCT2075_I2C_ADDR_0 = 0x37  # Default I2C address

PCT2075_I2C_BUS_1 = SCD4X_I2C_BUS  # I2C bus number for second PCT2075 sensor
PCT2075_I2C_SDA_PIN_1 = SCD4X_I2C_SDA_PIN  # Disable second sensor
PCT2075_I2C_SCL_PIN_1 = SCD4X_I2C_SCL_PIN
PCT2075_I2C_ADDR_1 = 0x76

PCT2075_I2C_BUS_2 = SCD4X_I2C_BUS  # I2C bus number for third PCT2075 sensor
PCT2075_I2C_SDA_PIN_2 = SCD4X_I2C_SDA_PIN  # Disable third sensor
PCT2075_I2C_SCL_PIN_2 = SCD4X_I2C_SCL_PIN
PCT2075_I2C_ADDR_2 = 0x77

# Sensor polling interval in seconds
POLL_INTERVAL_SECONDS = 30

QT_POWER_PIN = 7  # Pin for QT port power, set to -1 to disable

# Local overrides (gitignored) — copy config_local.example.py to config_local.py
try:
    from config_local import *  # type: ignore # noqa: F401, F403
except ImportError:
    pass
