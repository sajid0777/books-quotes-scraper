"""Shared polite HTTP client for the practice-site scrapers."""
import logging
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BaseScraper:
    def __init__(self, delay: float = 0.5, timeout: float = 10.0):
        self.delay = delay
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "ScrapingAssignment/1.0 (learning project)"})
        retry = Retry(total=3, connect=3, read=3, status=3, backoff_factor=0.5,
                      status_forcelist=(429, 500, 502, 503, 504),
                      allowed_methods=frozenset({"GET"}), raise_on_status=False)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get(self, url: str) -> requests.Response:
        self.logger.info("Requesting %s", url)
        response = self.session.get(url, timeout=self.timeout)
        response.encoding = "utf-8"
        response.raise_for_status()
        time.sleep(self.delay)
        return response

