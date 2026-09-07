from typing import List, Set, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from models import ScrapedRecord
from polite_client import PoliteHTTPClient, DEFAULT_USER_AGENT
from robots_checker import RobotsChecker
from cleaner_extractor import HTMLCleanerExtractor
from storage import CorpusStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PoliteScraperPipeline:
    """Orchestrates web crawling, politeness compliance, content extraction, and RAG storage."""

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        default_delay: float = 1.0,
        jsonl_path: str = "corpus.jsonl",
        sqlite_path: str = "corpus.db"
    ):
        self.user_agent = user_agent
        self.default_delay = default_delay
        self.client = PoliteHTTPClient(user_agent=user_agent, default_delay=default_delay)
        self.robots_checker = RobotsChecker(client=self.client.client)
        self.extractor = HTMLCleanerExtractor()
        self.storage = CorpusStorage(jsonl_path=jsonl_path, sqlite_path=sqlite_path)
        self.visited_urls: Set[str] = set()

    def _extract_links(self, html_content: str, base_url: str) -> List[str]:
        soup = BeautifulSoup(html_content, "lxml" if "lxml" in sys.modules else "html.parser")
        base_domain = urlparse(base_url).netloc
        discovered = []

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            # Restrict crawling to same domain
            if parsed.netloc == base_domain and parsed.scheme in ("http", "https"):
                discovered.append(full_url)

        return list(dict.fromkeys(discovered))

    def run(self, seed_url: str, max_pages: int = 5) -> List[ScrapedRecord]:
        queue = [seed_url]
        scraped_records: List[ScrapedRecord] = []

        logger.info(f"Starting polite crawler from seed: {seed_url} (Max pages: {max_pages})")

        while queue and len(scraped_records) < max_pages:
            current_url = queue.pop(0)

            if current_url in self.visited_urls:
                continue
            self.visited_urls.add(current_url)

            # 1. Check robots.txt compliance
            if not self.robots_checker.can_fetch(current_url, self.user_agent):
                logger.warning(f"Skipping {current_url}: Disallowed by robots.txt")
                continue

            # 2. Extract Crawl-delay from robots.txt if present
            robots_delay = self.robots_checker.get_crawl_delay(current_url, self.user_agent)
            delay = robots_delay if robots_delay is not None else self.default_delay

            # 3. Fetch HTML politely
            response = self.client.get(current_url, delay=delay)
            if not response or response.status_code != 200:
                logger.warning(f"Failed to retrieve {current_url}")
                continue

            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                logger.info(f"Skipping non-HTML page {current_url} ({content_type})")
                continue

            # 4. Clean HTML & extract structured fields
            record = self.extractor.extract(response.text, current_url)

            # Only save records with meaningful content
            if record.word_count > 10:
                self.storage.save(record)
                scraped_records.append(record)
                logger.info(f"Scraped page [{len(scraped_records)}/{max_pages}]: {record.title} ({record.word_count} words)")

            # 5. Discover new links for crawling
            new_links = self._extract_links(response.text, current_url)
            for link in new_links:
                if link not in self.visited_urls and link not in queue:
                    queue.append(link)

        self.client.close()
        logger.info(f"Crawl completed. Total records saved: {len(scraped_records)}")
        return scraped_records
