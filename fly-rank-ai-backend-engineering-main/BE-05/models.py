from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class ScrapedRecord(BaseModel):
    id: str = Field(description="Unique hash or URL slug identifier for record deduplication")
    url: str = Field(description="Canonical URL of the scraped page")
    title: str = Field(description="Extracted document or article title")
    author: Optional[str] = Field(default="Unknown", description="Author or domain source")
    published_date: Optional[str] = Field(default=None, description="ISO 8601 publication date")
    content: str = Field(description="Cleaned, plain-text main body content")
    summary: Optional[str] = Field(default=None, description="Short text preview or first paragraph")
    tags: List[str] = Field(default_factory=list, description="Extracted keywords, categories, or tags")
    word_count: int = Field(default=0, description="Total word count of cleaned main body text")
    scraped_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z", description="UTC timestamp when page was scraped")
