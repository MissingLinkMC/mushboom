import uasyncio as asyncio
import sys

from lib.logger import get_logger

# Get a logger for task helpers
logger = get_logger("tasks")


async def safe_task(name, coro):
    """
    Wraps a coroutine in a safety loop that catches and logs exceptions
    Makes sure to yield frequently to prevent blocking the event loop.

    Args:
        name: Name of the task for logging
        coro: Coroutine function to execute
    """
    task_logger = get_logger(name)
    task_logger.info("Starting task")

    # Track if this is the first run or a restart after crash
    is_restart = False

    while True:
        try:
            if is_restart:
                task_logger.warning(f"Restarting task '{name}' after previous failure")
                # Shorter delay on restart to prevent log spam but still allow recovery
                await asyncio.sleep(1)

            # Execute the coroutine
            await coro()

            # If we get here, the coroutine returned normally
            task_logger.warning(f"Task '{name}' completed unexpectedly")

        except asyncio.CancelledError:
            # This is a normal cancellation, just exit
            task_logger.info(f"Task '{name}' cancelled")
            raise

        except Exception as e:
            task_logger.error(f"Task '{name}' crashed: {str(e)}")
            # Try to get traceback if available
            try:
                sys.print_exception(e)
            except Exception:
                pass

            is_restart = True

        # Small sleep to prevent CPU hogging in case of rapid failures
        for _ in range(4):  # 4 x 0.5s = 2s total
            await asyncio.sleep(0.5)
