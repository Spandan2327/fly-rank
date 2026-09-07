import urllib.robotparser
from urllib.parse import urlparse
import httpx
import re
import logging
from typing import Optional, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobotsChecker:
    """Parses robots.txt files, enforcing Disallow rules and extracting Crawl-delay."""

    def __init__(self, client: Optional[httpx.Client] = None):
        self.parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self.raw_robots: Dict[str, str] = {}
        self.client = client or httpx.Client(timeout=10.0, follow_redirects=True)

    def _get_robots_url(self, target_url: str) -> str:
        parsed = urlparse(target_url)
        return f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    def fetch_robots(self, target_url: str) -> urllib.robotparser.RobotFileParser:
        domain = urlparse(target_url).netloc
        if domain in self.parsers:
            return self.parsers[domain]

        robots_url = self._get_robots_url(target_url)
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(robots_url)

        try:
            response = self.client.get(robots_url)
            if response.status_code == 200:
                self.raw_robots[domain] = response.text
                parser.parse(response.text.splitlines())
                logger.info(f"Successfully fetched and parsed {robots_url}")
            else:
                self.raw_robots[domain] = ""
                logger.info(f"robots.txt not found at {robots_url} (status {response.status_code}). Allowing all paths by default.")
                parser.parse([])
        except Exception as e:
            self.raw_robots[domain] = ""
            logger.warning(f"Failed to fetch {robots_url}: {e}. Allowing paths by default.")
            parser.parse([])

        self.parsers[domain] = parser
        return parser

    def can_fetch(self, url: str, user_agent: str) -> bool:
        """Check if user agent is allowed to scrape target URL."""
        parser = self.fetch_robots(url)
        allowed = parser.can_fetch(user_agent, url)
        if not allowed:
            logger.warning(f"Scraping BLOCKED by robots.txt: {url} (User-Agent: {user_agent})")
        return allowed

    def get_crawl_delay(self, url: str, user_agent: str) -> Optional[float]:
        """Extract Crawl-delay for user agent if specified."""
        domain = urlparse(url).netloc
        parser = self.fetch_robots(url)
        
        # 1. Try standard robotparser crawl_delay
        try:
            delay = parser.crawl_delay(user_agent)
            if delay is not None:
                return float(delay)
        except Exception:
            pass

        # 2. Fallback regex search on raw robots.txt
        raw = self.raw_robots.get(domain, "")
        if raw:
            match = re.search(r"(?i)crawl-delay:\s*([\d\.]+)", raw)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass

        return None
