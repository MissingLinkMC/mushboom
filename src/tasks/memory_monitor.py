"""
Helps track memory usage and identify potential memory leaks
"""

import gc
import uasyncio as asyncio
import time
import sys

from lib.logger import get_logger

logger = get_logger("memory")

# Track memory usage history
memory_history = {
    "startup": {"percent": 0, "free": 0, "used": 0, "time": 0},
    "current": {"percent": 0, "free": 0, "used": 0, "total": 0, "time": 0},
    "min": {"percent": 100, "free": 0, "used": sys.maxsize, "time": 0},
    "max": {"percent": 0, "free": 0, "used": 0, "time": 0},
    "last_hour": [],
    "trend_increasing": False,
    "consecutive_increases": 0,
}

INTERVAL_SECONDS = 300


async def monitor_memory():
    """
    Monitor memory usage periodically and log stats
    """

    # Initialize the memory history at startup
    gc.collect()
    mem_free = gc.mem_free()
    mem_alloc = gc.mem_alloc()
    total = mem_free + mem_alloc
    percent_used = 100 * mem_alloc / total if total > 0 else 0

    current_time = time.time()
    memory_history["startup"] = {
        "percent": percent_used,
        "free": mem_free,
        "used": mem_alloc,
        "time": current_time,
    }
    memory_history["min"]["percent"] = percent_used
    memory_history["min"]["free"] = mem_free
    memory_history["min"]["used"] = mem_alloc
    memory_history["min"]["time"] = current_time
    memory_history["max"]["percent"] = percent_used
    memory_history["max"]["free"] = mem_free
    memory_history["max"]["used"] = mem_alloc
    memory_history["max"]["time"] = current_time

    prev_used = mem_alloc
    hour_entries = int(3600 / INTERVAL_SECONDS)  # Number of entries in an hour

    while True:
        # Force garbage collection
        gc.collect()

        # Get memory statistics
        mem_free = gc.mem_free()
        mem_alloc = gc.mem_alloc()
        total = mem_free + mem_alloc
        percent_used = 100 * mem_alloc / total if total > 0 else 0
        current_time = time.time()

        memory_history["current"] = {
            "percent": percent_used,
            "free": mem_free,
            "used": mem_alloc,
            "total": total,
            "time": current_time,
        }

        # Update history
        if percent_used > memory_history["max"]["percent"]:
            memory_history["max"] = {
                "percent": percent_used,
                "free": mem_free,
                "used": mem_alloc,
                "time": current_time,
            }

        if percent_used < memory_history["min"]["percent"]:
            memory_history["min"] = {
                "percent": percent_used,
                "free": mem_free,
                "used": mem_alloc,
                "time": current_time,
            }

        # Add to hour history, keeping only the last hour
        memory_history["last_hour"].append(
            {
                "percent": percent_used,
                "free": mem_free,
                "used": mem_alloc,
                "time": current_time,
            }
        )

        # Maintain just the last hour's worth of entries
        if len(memory_history["last_hour"]) > hour_entries:
            memory_history["last_hour"].pop(0)

        # Check for memory growth trend
        if mem_alloc > prev_used:
            memory_history["consecutive_increases"] += 1
            if memory_history["consecutive_increases"] >= 3:
                memory_history["trend_increasing"] = True
        else:
            memory_history["consecutive_increases"] = 0
            memory_history["trend_increasing"] = False

        prev_used = mem_alloc

        # Determine log level based on usage
        if percent_used > 30:
            logger.warning(
                "HIGH Memory: %0.1f%% used (%d free, %d used)",
                percent_used,
                mem_free,
                mem_alloc,
            )
        elif percent_used > 25 and memory_history["trend_increasing"]:
            logger.warning(
                "Memory usage trending upward: %0.1f%% used (%d free, %d used)",
                percent_used,
                mem_free,
                mem_alloc,
            )
        else:
            logger.info(
                "Memory: %0.1f%% used (%d free, %d used)",
                percent_used,
                mem_free,
                mem_alloc,
            )

        # Additional period report (every hour)
        if int(current_time / 3600) != int((current_time - INTERVAL_SECONDS) / 3600):
            # It's the first check of a new hour, log a summary
            startup = memory_history["startup"]
            change = percent_used - startup["percent"]
            logger.info(
                "Memory summary - Current: %0.1f%%, Max: %0.1f%%, Min: %0.1f%%, Change since boot: %+0.1f%%",
                percent_used,
                memory_history["max"]["percent"],
                memory_history["min"]["percent"],
                change,
            )

        # Sleep until next check
        await asyncio.sleep(INTERVAL_SECONDS)
