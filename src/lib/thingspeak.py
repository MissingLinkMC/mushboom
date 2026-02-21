import urequests
import time
from lib.logger import get_logger

logger = get_logger("thingspeak")

class ThingSpeak:
    def __init__(self, api_key, base_url="https://api.thingspeak.com",
                 max_retries=3, retry_delay=5, timeout=10):
        """
        Initialize ThingSpeak client.

        Args:
            api_key: ThingSpeak Write API Key
            base_url: ThingSpeak API base URL
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Seconds to wait between retries (default: 5)
            timeout: Request timeout in seconds (default: 10)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout

    def send_update(self, **fields):
        """
        Send an update to ThingSpeak with the given field values.
        fields should be a dictionary of field numbers to values.
        """
        if not self.api_key:
            return

        # Build query string from fields, explicitly converting both keys and values to strings
        query_params = [f"field{str(k)}={str(v)}" for k, v in fields.items()]
        query_string = "&".join(query_params)

        # Construct full URL
        url = f"{self.base_url}/update?api_key={self.api_key}&{query_string}"

        attempts = 0
        last_error = None

        while attempts < self.max_retries:
            try:
                response = urequests.get(url, timeout=self.timeout)
                try:
                    if response.status_code == 200:
                        logger.debug("ThingSpeak update successful")
                        return True
                    else:
                        last_error = f"HTTP {response.status_code}"
                        logger.warning("ThingSpeak update failed (attempt %d/%d): %s",
                                     attempts + 1, self.max_retries, last_error)
                finally:
                    response.close()  # Always close the response

            except OSError as e:
                last_error = str(e)
                logger.warning("ThingSpeak network error (attempt %d/%d): %s",
                             attempts + 1, self.max_retries, last_error)

            except Exception as e:
                last_error = str(e)
                logger.warning("ThingSpeak unexpected error (attempt %d/%d): %s",
                             attempts + 1, self.max_retries, last_error)

            attempts += 1
            if attempts < self.max_retries:
                time.sleep(self.retry_delay)

        logger.error("ThingSpeak update failed after %d attempts. Last error: %s",
                    self.max_retries, last_error)
        return False