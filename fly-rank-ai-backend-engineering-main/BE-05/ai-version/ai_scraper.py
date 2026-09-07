import httpx
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urlparse

# AI Flaw 1: Generic User-Agent string instead of identifying bot with project URL
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

class AIScraper:
    def __init__(self, delay=1.0):
        self.delay = delay
        self.headers = {"User-Agent": USER_AGENT}

    # AI Flaw 2: Dumb robots.txt check that only looks for "Disallow: /" string matching instead of parsing rules with urllib.robotparser
    def check_robots(self, url):
        try:
            domain = urlparse(url).netloc
            robots_url = f"https://{domain}/robots.txt"
            res = httpx.get(robots_url, timeout=5.0)
            if "Disallow: /" in res.text:
                return False
            return True
        except Exception:
            return True

    def scrape(self, url, jsonl_file="ai_corpus.jsonl"):
        if not self.check_robots(url):
            print(f"Blocked by robots.txt: {url}")
            return None

        # AI Flaw 3: No per-domain throttle delay tracking across consecutive requests
        time.sleep(self.delay)

        res = httpx.get(url, headers=self.headers)
        soup = BeautifulSoup(res.text, "html.parser")

        # AI Flaw 4: Only removed script and style, leaving nav, footer, header, and sidebar text in content
        for script in soup(["script", "style"]):
            script.decompose()

        title = soup.title.string if soup.title else ""
        # Gets raw text without targeting <article> or <main> container
        text = soup.get_text(separator=" ", strip=True)
        word_count = len(text.split())

        record = {
            "url": url,
            "title": title,
            "content": text,
            "word_count": word_count
        }

        with open(jsonl_file, "a") as f:
            f.write(json.dumps(record) + "\n")

        return record

if __name__ == "__main__":
    scraper = AIScraper()
    scraper.scrape("https://example.com")
