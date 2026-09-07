import sys
import os
import pytest
import time
import json
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models import ScrapedRecord
from polite_client import PoliteHTTPClient, DEFAULT_USER_AGENT
from robots_checker import RobotsChecker
from cleaner_extractor import HTMLCleanerExtractor
from storage import CorpusStorage
from scraper import PoliteScraperPipeline

def test_scraped_record_model():
    record = ScrapedRecord(
        id="test-123",
        url="https://example.com/test",
        title="Test Title",
        content="This is clean main body text.",
        word_count=6
    )
    assert record.id == "test-123"
    assert record.url == "https://example.com/test"
    assert record.title == "Test Title"
    assert record.word_count == 6
    assert record.scraped_at.endswith("Z")

def test_polite_client_user_agent():
    client = PoliteHTTPClient(user_agent="CustomBot/1.0", default_delay=0.1)
    assert client.user_agent == "CustomBot/1.0"
    assert client.client.headers["User-Agent"] == "CustomBot/1.0"
    client.close()

def test_polite_client_rate_limiting():
    client = PoliteHTTPClient(default_delay=0.2)
    start_time = time.time()
    client._throttle("https://example.com/page1", delay=0.2)
    client._throttle("https://example.com/page2", delay=0.2)
    elapsed = time.time() - start_time
    assert elapsed >= 0.18
    client.close()

def test_robots_checker_parsing():
    checker = RobotsChecker()
    checker.raw_robots["example.com"] = "User-agent: *\nDisallow: /private/\nDisallow: /admin/\nCrawl-delay: 2.5"
    import urllib.robotparser
    p = urllib.robotparser.RobotFileParser()
    p.parse(checker.raw_robots["example.com"].splitlines())
    checker.parsers["example.com"] = p

    assert checker.can_fetch("https://example.com/public/article", "FlyRankPoliteBot") is True
    assert checker.can_fetch("https://example.com/private/secret", "FlyRankPoliteBot") is False
    assert checker.can_fetch("https://example.com/admin/login", "FlyRankPoliteBot") is False
    assert checker.get_crawl_delay("https://example.com/public/article", "FlyRankPoliteBot") == 2.5

def test_html_cleaner_extractor():
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Polite Web Scraping Article</title>
        <meta name="author" content="Jane Doe" />
        <meta name="keywords" content="python, scraping, rag, ai" />
    </head>
    <body>
        <nav><a href="/">Home</a> <a href="/about">About Us</a></nav>
        <article>
            <h1>Polite Web Scraping Article</h1>
            <p>Web scraping is a foundational skill for building retrieval-augmented generation RAG AI pipelines.</p>
        </article>
    </body>
    </html>
    """
    extractor = HTMLCleanerExtractor()
    record = extractor.extract(sample_html, "https://example.com/polite-scraping")

    assert record.title == "Polite Web Scraping Article"
    assert record.author == "Jane Doe"
    assert "python" in record.tags
    assert record.word_count > 5

def test_corpus_storage(tmp_path):
    jsonl_file = str(tmp_path / "test_corpus.jsonl")
    sqlite_file = str(tmp_path / "test_corpus.db")
    storage = CorpusStorage(jsonl_path=jsonl_file, sqlite_path=sqlite_file)

    record = ScrapedRecord(
        id="rec-001",
        url="https://example.com/article1",
        title="Article 1",
        content="Clean content for RAG embedding.",
        tags=["ai", "rag"],
        word_count=5
    )

    storage.save(record)

    with open(jsonl_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["id"] == "rec-001"
        assert data["title"] == "Article 1"

    assert storage.get_sqlite_count() == 1

def test_link_discovery():
    sample_html = """
    <html>
    <body>
        <a href="/page1">Page 1</a>
        <a href="https://example.com/page2">Page 2</a>
        <a href="https://external.com/page3">External</a>
    </body>
    </html>
    """
    pipeline = PoliteScraperPipeline()
    links = pipeline._extract_links(sample_html, "https://example.com/start")

    assert "https://example.com/page1" in links
    assert "https://example.com/page2" in links
    assert "https://external.com/page3" not in links
    pipeline.client.close()
