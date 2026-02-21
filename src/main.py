"""
MushBoom - Main application entry point
Controls the mushroom growing environment with temperature, humidity, and CO2 monitoring
"""

import uasyncio as asyncio
import ntptime
import machine

# Core functionality
from api import app
import config as app_config
from tasks.sensor_loop import poll_sensor_loop
from tasks.control_loop import control_loop
from tasks.relay_loop import relay_controller
from tasks.thingspeak_loop import thingspeak_loop
from lib.reset_reason import get_reset_reason


# System utilities
from lib.wifi import WiFi
from tasks.task_helpers import safe_task
from lib.logger import get_logger
from tasks.memory_monitor import monitor_memory
import time

time.sleep(2)  # Short delay to allow us to interrupt if needed

# Get configs
WEB_SERVER_PORT = getattr(app_config, "WEB_SERVER_PORT", 80)
WEB_SERVER_HOST = getattr(app_config, "WEB_SERVER_HOST", "0.0.0.0")

# Get logger for main module
logger = get_logger("main")

# Initialize system
logger.info("Starting MushBoom system (v1.0)")

# Log reset cause at startup
try:
    cause = machine.reset_cause()
    cause_str = get_reset_reason(cause)
    logger.info(f"System reset cause: {cause_str} ({cause})")
except Exception as e:
    logger.warning(f"Could not determine reset cause {cause}: {e}")

async def main():
    """Main application entrypoint"""
    logger.info("Initializing system tasks...")

    # Start core functionality tasks as soon as possible to protect our mushies
    asyncio.create_task(safe_task("Sensor", poll_sensor_loop))
    asyncio.create_task(safe_task("Control", control_loop))
    asyncio.create_task(safe_task("Relay", relay_controller.relay_loop))
    asyncio.create_task(safe_task("ThingSpeak", thingspeak_loop))

    # Add memory monitoring to track memory usage
    asyncio.create_task(safe_task("Memory Monitor", monitor_memory))

    # Connect to WiFi
    logger.info("Connecting to WiFi")
    wifi = WiFi()
    wifi.up()

    while not wifi.get_status().get("state") == "connected":
        logger.info("Waiting for WiFi connection...")
        await asyncio.sleep(1)

    logger.info("WiFi connected successfully")

    logger.info("Synchronizing system time via NTP")

    try:
        ntptime.settime()
        logger.info('Clock synchronized successfully.')
    except OSError:
        logger.warning('Failed to synchronize the clock.')

    logger.info("System time synchronized via NTP")

    logger.info("Starting web server on port 80")

    # Create web server task with recovery wrapper
    server_task = asyncio.create_task(
        safe_task(
            "WebServer",
            lambda: app.start_server(debug=True, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT),
        )
    )

    # Keep the main task running to coordinate everything
    await server_task


# Set up global exception handler for uncaught errors
def handle_exception(loop, context):
    exception = context.get("exception", None)
    if exception:
        error_message = str(exception)
        logger.critical("Unhandled exception in event loop: %s", error_message)
        logger.exception(exception, "event loop")
    else:
        logger.critical("Unhandled exception in event loop: %s", str(context))


# Get the event loop and set the exception handler
loop = asyncio.get_event_loop()
loop.set_exception_handler(handle_exception)

# Run the main coroutine
logger.info("Launching main application...")
try:
    asyncio.run(main())
except Exception as e:
    logger.critical("Fatal error in main task: %s", str(e))
    logger.exception(e, "main")

    try:
        logger.critical(f"Resetting due to fatal error: {e}")
        machine.reset()
    except Exception as reset_exc:
        logger.critical(f"Failed to reset device after fatal error: {reset_exc}")
