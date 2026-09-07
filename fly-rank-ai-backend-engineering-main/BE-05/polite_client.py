import httpx
import time
import logging
from typing import Optional, Dict
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = "FlyRankPoliteBot/1.0 (+https://github.com/0-second-shadow-0/fly-rank-ai-backend-engineering)"

class PoliteHTTPClient:
    """Polite HTTP Client with custom User-Agent, per-domain rate limiting, and exponential backoff."""
    
    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        default_delay: float = 1.0,
        timeout: float = 10.0,
        max_retries: int = 3
    ):
        self.user_agent = user_agent
        self.default_delay = default_delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.last_request_time: Dict[str, float] = {}
        
        self.client = httpx.Client(
            headers={"User-Agent": self.user_agent},
            timeout=self.timeout,
            follow_redirects=True
        )

    def _throttle(self, url: str, delay: Optional[float] = None):
        """Enforce per-domain crawl delay."""
        domain = urlparse(url).netloc
        req_delay = delay if delay is not None else self.default_delay
        
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < req_delay:
                sleep_time = req_delay - elapsed
                logger.info(f"Throttling request to {domain}: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
                
        self.last_request_time[domain] = time.time()

    def get(self, url: str, delay: Optional[float] = None) -> Optional[httpx.Response]:
        """Fetch URL politely with rate limiting and retries."""
        self._throttle(url, delay=delay)
        
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.get(url)
                if response.status_code == 200:
                    return response
                elif response.status_code in (429, 500, 502, 503, 504):
                    backoff = (2 ** attempt) * 0.5
                    logger.warning(f"HTTP {response.status_code} for {url}. Retrying in {backoff:.1f}s (Attempt {attempt}/{self.max_retries})")
                    time.sleep(backoff)
                else:
                    logger.error(f"HTTP {response.status_code} for {url}. Not retrying.")
                    return response
            except httpx.RequestError as e:
                backoff = (2 ** attempt) * 0.5
                logger.warning(f"Network error {e} for {url}. Retrying in {backoff:.1f}s (Attempt {attempt}/{self.max_retries})")
                time.sleep(backoff)
                
        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts.")
        return None

    def close(self):
        self.client.close()
