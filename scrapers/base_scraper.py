import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config

logger = logging.getLogger("ScraperPipeline")


class BaseScraper(ABC):
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Configures a resilient HTTP session with retries and exponential backoff."""
        session = requests.Session()
        retry_strategy = Retry(
            total=config.MAX_RETRIES,
            backoff_factor=config.BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({"User-Agent": config.USER_AGENT})
        return session

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetches page content with exception handling and rate limiting."""
        try:
            time.sleep(config.REQUEST_DELAY)
            response = self.session.get(url, timeout=config.DEFAULT_TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as e:
            logger.error(f"[{self.name}] HTTP error fetched {url}: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[{self.name}] Connection error for {url}: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"[{self.name}] Request timed out for {url}: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"[{self.name}] Request failed for {url}: {e}")
        return None

    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping loop to be implemented by child classes."""
        pass