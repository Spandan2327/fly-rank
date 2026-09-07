import json
import sqlite3
import os
import sys
import logging
from typing import List, Optional

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from models import ScrapedRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CorpusStorage:
    """Manages persistent storage of scraped records in JSONL and SQLite formats for RAG."""

    def __init__(self, jsonl_path: str = "corpus.jsonl", sqlite_path: str = "corpus.db"):
        self.jsonl_path = jsonl_path
        self.sqlite_path = sqlite_path
        self._init_sqlite()

    def _init_sqlite(self):
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS corpus (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT,
                published_date TEXT,
                content TEXT NOT NULL,
                summary TEXT,
                tags TEXT,
                word_count INTEGER,
                scraped_at TEXT NOT NULL
            );
        """)
        conn.commit()
        conn.close()

    def save_to_jsonl(self, record: ScrapedRecord) -> str:
        """Append a ScrapedRecord as a single-line JSON string to corpus.jsonl."""
        json_str = record.model_dump_json()
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json_str + "\n")
        logger.info(f"Appended record {record.id} ({record.title}) to {self.jsonl_path}")
        return self.jsonl_path

    def save_to_sqlite(self, record: ScrapedRecord) -> str:
        """Insert or replace a ScrapedRecord into the SQLite database corpus table."""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        tags_str = ",".join(record.tags) if record.tags else ""
        cursor.execute("""
            INSERT OR REPLACE INTO corpus (
                id, url, title, author, published_date, content, summary, tags, word_count, scraped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            record.id,
            record.url,
            record.title,
            record.author,
            record.published_date,
            record.content,
            record.summary,
            tags_str,
            record.word_count,
            record.scraped_at
        ))
        conn.commit()
        conn.close()
        logger.info(f"Saved record {record.id} to SQLite {self.sqlite_path}")
        return self.sqlite_path

    def save(self, record: ScrapedRecord):
        """Save record to both JSONL and SQLite storage."""
        self.save_to_jsonl(record)
        self.save_to_sqlite(record)

    def load_jsonl() -> List[ScrapedRecord]:
        records = []
        if not os.path.exists(self.jsonl_path):
            return records
        with open(self.jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(ScrapedRecord.model_validate_json(line))
        return records

    def get_sqlite_count(self) -> int:
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM corpus;")
        count = cursor.fetchone()[0]
        conn.close()
        return count
