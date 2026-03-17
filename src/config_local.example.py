# Local configuration overrides — copy this file to config_local.py and fill in your values.
# config_local.py is gitignored and will never be committed.

# ThingSpeak configuration
THINGSPEAK_API_KEY = "your-write-api-key-here"
THINGSPEAK_ENABLED = True
THINGSPEAK_CHANNEL_ID = 0  # Your numeric channel ID

# Debug mode — set to True when testing without real hardware (no sensors or relays attached)
# DEBUG_MODE = True

# Device IP — used as a shell variable, not read by app code.
# After boot, find it via: mpremote exec "import network; w=network.WLAN(); print(w.ifconfig())"
# Then: export DEVICE_IP=192.168.x.x
# DEVICE_IP = "192.168.x.x"
