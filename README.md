# MushBoom

MushBoom is a simple environmental control system for mushroom cultivation. It monitors and regulates key environmental factors (temperature, humidity, and CO2 levels) to create optimal growing conditions for mushrooms using MicroPython on ESP32 microcontrollers.

## Features

- **Environmental Monitoring**: Continuous monitoring of temperature, humidity, and CO2 levels using SCD4X sensors
- **Multi-Point Temperature Sensing**: Up to 3 additional PCT2075 temperature sensors for vertical temperature profiling, enabling more precise heating control throughout the growing space
- **Automated Control**: Smart regulation of:
  - Heating system to maintain optimal temperature range (uses all available temperature sensors for even heating)
  - Humidification system for proper moisture levels
  - Fan control for CO2 management and fresh air exchange
  - **Fan Schedule**: Configurable periodic fan operation to ensure regular fresh air exchange, even when CO2 levels are within acceptable ranges
- **Web Interface**: Built-in web server for remote monitoring and control
- **WiFi Connectivity**: Easy network integration and remote access
- **Time Synchronization**: NTP client for accurate timestamps
- **Logging**: Logging for troubleshooting

## Hardware Requirements

- ESP32 microcontroller (preferably S3)
- SCD4X CO2, temperature, and humidity sensor
- Up to 3 optional PCT2075 temperature sensors (for vertical temperature profiling)
- Relay module for controlling devices (tested with SunFounder Lab 4 Relay Module 5V):
  - Heating element
  - Humidifier
  - Ventilation fan
- Power supply components

## Third-Party Libraries

MushBoom integrates several third-party libraries to provide essential functionality:

- **[Microdot](https://github.com/miguelgrinberg/microdot)**: Lightweight web framework for MicroPython that powers the web interface. It provides routing, request handling, and response formatting capabilities.

- **[SCD4X Driver](https://github.com/adafruit/Adafruit_CircuitPython_SCD4X)**: Custom sensor driver for the Sensirion SCD4X CO2, temperature, and humidity sensor, adapted from Adafruit's CircuitPython implementation.

- **[WiFi Manager](https://github.com/mitchins/micropython-wifimanager)**: Handles WiFi connectivity with features for network scanning, connection management, and fallback to Access Point mode if no networks are available.

## Development Environment Prerequisites

Before getting started with MushBoom, ensure your development environment has the following tools installed:

- **Python**: Version 3.13 or later is required
- **Make**: Used to run development commands and flash the firmware
- **UV**: The [UV Python package manager](https://github.com/astral-sh/uv) for dependency management
- **MicroPython Tools**:
  - `mpremote` for communicating with the ESP32 device
  - MicroPython firmware must be pre-installed on your ESP32
- **Development Tools**:
  - `ruff` for linting
  - `black` for code formatting
  - `pyright` for type checking
  - `pytest` for running tests

These tools are automatically installed in the virtual environment when running `uv sync`, but the base tools (Python, Make, UV) need to be installed on your system.

### Operating System Support

- **macOS/Linux**: Fully supported with bash/zsh
- **Windows**: Supported via PowerShell or WSL (Windows Subsystem for Linux)

## Installation

1. **Setup Development Environment**:
   ```bash
   # Create and activate a Python virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   uv sync
   ```

2. **Install Typing Stubs**:
   ```bash
   make stubs
   ```

3. **Configure Local Secrets** *(optional — required for ThingSpeak)*:
   ```bash
   cp src/config_local.example.py src/config_local.py
   ```

   Then edit `src/config_local.py` with your ThingSpeak credentials:
   ```python
   THINGSPEAK_API_KEY = "your-write-api-key"
   THINGSPEAK_ENABLED = True
   THINGSPEAK_CHANNEL_ID = 123456
   ```

   `config_local.py` is gitignored and will never be committed. It overrides any matching
   variable in `config.py`, so you can also use it to override other settings (pin numbers,
   polling interval, etc.) without modifying the tracked file.

4. **Configure WiFi**:
   ```bash
   # Copy the example network configuration
   cp src/networks.example.json src/networks.json
   ```

   Then edit the `src/networks.json` file to include your WiFi details:
   ```json
   {
     "schema": 2,
     "known_networks": [
       {
         "ssid": "Your_WiFi_Name",
         "password": "Your_WiFi_Password",
         "enables_webrepl": true
       }
     ],
     "access_point": {
       "config": {
         "essid": "MushBoom-AP",
         "channel": 11,
         "hidden": false,
         "password": "mushroom"
       },
       "enables_webrepl": true,
       "start_policy": "fallback"
     }
   }
   ```

   * Replace `Your_WiFi_Name` and `Your_WiFi_Password` with your actual WiFi credentials
   * You can add multiple networks by adding more objects to the `known_networks` array
   * The system will connect to networks in the order listed (first has highest priority)
   * If no known networks are available, it will create its own access point using the settings in `access_point`

5. **Configure Hardware Pins**:

   Edit the `src/config.py` file to match your hardware setup:

   ```python
   # GPIO pins for relay control
   HEATER_RELAY_PIN = 15      # Change to your heater relay GPIO pin
   FAN_RELAY_PIN = 14         # Change to your fan relay GPIO pin
   HUMIDIFIER_RELAY_PIN = 13  # Change to your humidifier relay GPIO pin

   # WiFi status LED configuration
   WIFI_STATUS_LED_PIN = 13   # Use -1 to disable status LED

   # SCD4X Sensor Pin configuration
   SCD4X_I2C_BUS = 1          # I2C bus number for SCD4X sensor
   SCD4X_I2C_SDA_PIN = 3      # I2C data pin connected to SCD4X
   SCD4X_I2C_SCL_PIN = 4      # I2C clock pin connected to SCD4X
   SCD4X_I2C_FREQ = 100000    # I2C frequency (100kHz standard)

   # PCT2075 Temperature Sensors (up to 3 optional sensors, -1 to disable)
   # These sensors share the same I2C bus as the SCD4X and use different addresses
   PCT2075_I2C_BUS_0 = SCD4X_I2C_BUS  # I2C bus for first PCT2075 sensor
   PCT2075_I2C_SDA_PIN_0 = SCD4X_I2C_SDA_PIN  # SDA pin (shared with SCD4X)
   PCT2075_I2C_SCL_PIN_0 = SCD4X_I2C_SCL_PIN  # SCL pin (shared with SCD4X)
   PCT2075_I2C_ADDR_0 = 0x37  # I2C address for first sensor

   PCT2075_I2C_BUS_1 = SCD4X_I2C_BUS  # I2C bus for second PCT2075 sensor
   PCT2075_I2C_SDA_PIN_1 = SCD4X_I2C_SDA_PIN  # Set to -1 to disable
   PCT2075_I2C_SCL_PIN_1 = SCD4X_I2C_SCL_PIN
   PCT2075_I2C_ADDR_1 = 0x76  # I2C address for second sensor

   PCT2075_I2C_BUS_2 = SCD4X_I2C_BUS  # I2C bus for third PCT2075 sensor
   PCT2075_I2C_SDA_PIN_2 = SCD4X_I2C_SDA_PIN  # Set to -1 to disable
   PCT2075_I2C_SCL_PIN_2 = SCD4X_I2C_SCL_PIN
   PCT2075_I2C_ADDR_2 = 0x77  # I2C address for third sensor

   # Sensor polling interval
   POLL_INTERVAL_SECONDS = 30  # Time between sensor readings
   ```

   Adjust these values according to your specific hardware connections. The default pins are suitable for many ESP32 development boards, but you may need to change them based on your wiring.

6. **Flash to Device**:
   ```bash
   # Connect your ESP32 device via USB
   make flash
   ```

## Usage

After installation, the system will:
1. Start monitoring environmental conditions
2. Automatically control connected devices based on sensor readings
3. Provide a web interface accessible via the ESP32's IP address

### Control Modes

Each component (heater, fan, humidifier) can operate in three modes:
- **Auto**: Adjusts based on sensor readings and set thresholds
- **On**: Forces the component to stay on
- **Off**: Forces the component to stay off

### Fan Schedule

The fan schedule feature allows you to configure periodic fan operation to ensure regular fresh air exchange in your growing environment. This is particularly useful for maintaining air circulation even when CO2 levels are within acceptable ranges.

**How it works:**
- When enabled, the fan will run for a specified duration at regular intervals (e.g., run for 5 minutes every 60 minutes)
- The schedule operates independently of CO2-based automatic control - the fan will still run automatically if CO2 levels exceed your configured thresholds
- Schedule settings can be configured through the web interface or by editing the configuration file
- Default settings: Runs for 5 minutes every 60 minutes (disabled by default)

**Configuration:**
- **Enabled**: Toggle to enable/disable the schedule
- **Duration**: How long the fan should run each cycle (in minutes)
- **Interval**: How often the cycle repeats (in minutes)

**Example:** With duration set to 5 minutes and interval set to 60 minutes, the fan will run for 5 minutes, then wait 55 minutes, then run for 5 minutes again, repeating this cycle continuously.

**Note:** The schedule takes priority over CO2-based control when active, but CO2-based control will still activate the fan if levels exceed thresholds, even outside of scheduled run times.

### Development Commands

```bash
# Run linting
make lint

# Format code
make format

# Run type checking
make typecheck

# Run tests
make test

# Install typing stubs
make stubs

# Flash to device
make flash

# Clean device (remove all files)
make flash-clean
```

## Helpful Tips

### I can't access the REPL
If a bug is in your main.py and it keeps rebooting or otherwise is unreachable, here's the nuclear option:

✅ Full flash erase (nuclear, cleanest)

Boot into flash mode: hold the Boot button, press reset, wait a few seconds, then release boot.

This wipes everything — firmware + filesystem:

```
esptool.py --port /dev/cu.usbmodem14401 erase_flash
```

Then re-flash MicroPython:

```
esptool.py --port /dev/cu.usbmodem14401 write_flash 0 ESP32_GENERIC_S3-20250911-v1.26.1.bin
```

💡 After this, main.py will be gone — it’s a factory-clean board.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
