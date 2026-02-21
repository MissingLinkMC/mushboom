"""
Centralized logging system for MushBoom
Handles log rotation and different log levels
"""

import time
import os
import sys

# Log levels
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50

# Log level names for output
LEVEL_NAMES = {
    DEBUG: "DEBUG",
    INFO: "INFO",
    WARNING: "WARNING",
    ERROR: "ERROR",
    CRITICAL: "CRITICAL",
}

# Configuration
LOG_FOLDER = "logs"
LOG_FILE = "mushboom.log"
ERROR_LOG_FILE = "error.log"
MAX_LOG_SIZE = 500 * 1024  # 500KB
MAX_LOG_ENTRIES = 2000
LOG_LEVEL = INFO  # Default log level

# Ensure log directory exists
try:
    os.mkdir(LOG_FOLDER)
except OSError:
    # Directory already exists
    pass


class Logger:
    def __init__(self, name=None):
        self.name = name or "main"

    def log(self, level, message, *args):
        """Log a message at the specified level if it meets the threshold"""
        if level < LOG_LEVEL:
            return  # Skip if below threshold

        # Format the message with args if provided
        if args:
            try:
                message = message % args
            except Exception as e:
                message = f"{message} - (Error formatting: {e})"

        # Get timestamp
        timestamp = time.localtime()
        time_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            timestamp[0],
            timestamp[1],
            timestamp[2],  # Year, month, day
            timestamp[3],
            timestamp[4],
            timestamp[5],  # Hour, minute, second
        )

        # Format log entry
        log_entry = f"{time_str} | {LEVEL_NAMES.get(level, 'UNKNOWN')} | {self.name} | {message}"

        # Print to stdout for REPL/debugging
        print(log_entry)

        # Write to file
        try:
            path = f"{LOG_FOLDER}/{LOG_FILE}"
            self._write_log(path, log_entry)

            # Also write errors and criticals to error log
            if level >= ERROR:
                error_path = f"{LOG_FOLDER}/{ERROR_LOG_FILE}"
                self._write_log(error_path, log_entry)

        except Exception as e:
            print(f"Error writing to log file: {e}")

    def _write_log(self, file_path, entry):
        """Write a log entry to file with rotation if needed"""
        try:
            try:
                # First, check if file exists and needs rotation
                need_rotation = False
                try:
                    stat = os.stat(file_path)
                    # Check entry count by counting newlines (approximation)
                    if stat[6] > MAX_LOG_SIZE:  # stat[6] is file size
                        need_rotation = True
                except OSError:
                    # File doesn't exist yet
                    pass

                if need_rotation:
                    # This is more memory efficient than loading all entries
                    try:
                        # Rename existing file as backup during rotation
                        os.rename(file_path, file_path + ".bak")
                    except OSError:
                        pass

                    # Create new log with just this entry
                    with open(file_path, "w") as f:
                        f.write(entry + "\n")
                else:
                    # Just append to the file
                    with open(file_path, "a") as f:
                        f.write(entry + "\n")

            except OSError:
                # If anything fails, attempt a direct write
                with open(file_path, "w") as f:
                    f.write(entry + "\n")

        except Exception as e:
            print(f"Error in log rotation: {e}")

    # Convenience methods for different log levels
    def debug(self, message, *args):
        self.log(DEBUG, message, *args)

    def info(self, message, *args):
        self.log(INFO, message, *args)

    def warning(self, message, *args):
        self.log(WARNING, message, *args)

    def error(self, message, *args):
        self.log(ERROR, message, *args)

    def critical(self, message, *args):
        self.log(CRITICAL, message, *args)

    # Exception handler for uncaught exceptions
    def exception(self, e, context="unhandled"):
        """Log an exception with traceback if available"""
        error_msg = f"Exception in {context}: {type(e).__name__}: {e}"

        # Try to get traceback info if possible
        try:
            sys.print_exception(e)
            self.critical(error_msg)
        except Exception:
            self.critical(error_msg + " (traceback unavailable)")


def get_logger(name):
    """Get a logger with the specified name"""
    return Logger(name)
