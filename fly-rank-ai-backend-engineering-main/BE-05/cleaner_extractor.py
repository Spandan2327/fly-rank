from bs4 import BeautifulSoup
import hashlib
import re
from typing import Optional, List, Dict
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from models import ScrapedRecord

NOISE_TAGS = [
    "script", "style", "nav", "footer", "header", "aside", 
    "form", "iframe", "svg", "noscript", "input", "button", 
    "select", "textarea", "menu"
]

class HTMLCleanerExtractor:
    """Cleans HTML boilerplate and extracts structured fields for RAG corpus."""

    @staticmethod
    def _generate_id(url: str) -> str:
        return hashlib.md5(url.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str:
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()
            
        h1 = soup.find("h1")
        if h1 and h1.get_text(strip=True):
            return h1.get_text(strip=True)
            
        if soup.title and soup.title.get_text(strip=True):
            return soup.title.get_text(strip=True)
            
        return "Untitled Document"

    @staticmethod
    def _extract_author(soup: BeautifulSoup, domain: str) -> str:
        meta_author = soup.find("meta", attrs={"name": re.compile(r"author", re.I)})
        if meta_author and meta_author.get("content"):
            return meta_author["content"].strip()
            
        author_tag = soup.find(class_=re.compile(r"author|byline", re.I))
        if author_tag and author_tag.get_text(strip=True):
            return author_tag.get_text(strip=True)
            
        return domain

    @staticmethod
    def _extract_published_date(soup: BeautifulSoup) -> Optional[str]:
        meta_date = soup.find("meta", property=re.compile(r"published_time|date", re.I))
        if meta_date and meta_date.get("content"):
            return meta_date["content"].strip()
            
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            return time_tag["datetime"].strip()
        if time_tag and time_tag.get_text(strip=True):
            return time_tag.get_text(strip=True)
            
        return None

    @staticmethod
    def _extract_tags(soup: BeautifulSoup) -> List[str]:
        keywords = []
        meta_keywords = soup.find("meta", attrs={"name": re.compile(r"keywords", re.I)})
        if meta_keywords and meta_keywords.get("content"):
            raw = meta_keywords["content"]
            keywords = [k.strip() for k in raw.split(",") if k.strip()]
            
        for tag_el in soup.find_all(class_=re.compile(r"tag|category", re.I)):
            text = tag_el.get_text(strip=True)
            if text and len(text) < 30 and text not in keywords:
                keywords.append(text)
                
        return keywords[:10]

    def extract(self, html_content: str, url: str) -> ScrapedRecord:
        soup = BeautifulSoup(html_content, "lxml" if "lxml" in sys.modules else "html.parser")

        # 1. Remove noise elements
        for tag in soup.find_all(NOISE_TAGS):
            tag.decompose()

        # 2. Extract metadata
        from urllib.parse import urlparse
        domain = urlparse(url).netloc or "Unknown"
        title = self._extract_title(soup)
        author = self._extract_author(soup, domain)
        published_date = self._extract_published_date(soup)
        tags = self._extract_tags(soup)

        # 3. Target main content body
        main_container = (
            soup.find("article") or 
            soup.find("main") or 
            soup.find(id=re.compile(r"content|main|article", re.I)) or 
            soup.find(class_=re.compile(r"post-body|article-body|entry-content|content", re.I)) or 
            soup.body or 
            soup
        )

        # 4. Clean text extraction
        lines = []
        for element in main_container.find_all(["p", "h1", "h2", "h3", "h4", "li", "blockquote"]):
            text = element.get_text(separator=" ", strip=True)
            if text and len(text) > 10:
                lines.append(text)

        if not lines:
            raw_text = main_container.get_text(separator="\n", strip=True)
            lines = [line.strip() for line in raw_text.split("\n") if len(line.strip()) > 10]

        cleaned_content = "\n\n".join(lines)
        words = cleaned_content.split()
        word_count = len(words)
        summary = " ".join(words[:40]) + ("..." if len(words) > 40 else "") if words else ""

        return ScrapedRecord(
            id=self._generate_id(url),
            url=url,
            title=title,
            author=author,
            published_date=published_date,
            content=cleaned_content,
            summary=summary,
            tags=tags,
            word_count=word_count
        )
