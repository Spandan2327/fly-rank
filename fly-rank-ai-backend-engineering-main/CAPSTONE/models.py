from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class VisionMetadata(BaseModel):
    subject: str = Field(description="Detected primary subject, e.g., 'red fox'")
    category: str = Field(description="Broad category, e.g., 'animal', 'landscape', 'vehicle'")
    attributes: List[str] = Field(default_factory=list, description="Visual attributes, e.g., ['orange fur', 'wild', 'forest']")
    caption: str = Field(description="Human-readable descriptive caption")
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence score between 0.0 and 1.0")

    @field_validator("subject", "category", "caption")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip().lower()

class ImageRecord(BaseModel):
    id: str
    filename: str
    url: str
    subject: Optional[str] = None
    category: Optional[str] = None
    attributes: List[str] = Field(default_factory=list)
    caption: Optional[str] = None
    confidence: float = 0.0
    status: str = Field(default="PENDING", description="PENDING, PROCESSED, FLAGGED_LOW_CONFIDENCE")
    cost_usd: float = 0.0
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

class BlogPost(BaseModel):
    id: str
    title: str
    category: str
    topic: str
    content: str

class MismatchGuardResult(BaseModel):
    passed: bool
    status: str = Field(description="ACCEPTED, REJECTED, NO_CONFIDENT_MATCH")
    similarity_score: float
    reason: Optional[str] = None

class MatchSuggestion(BaseModel):
    id: str
    post_id: str
    post_title: str
    image_id: Optional[str] = None
    image_url: Optional[str] = None
    image_caption: Optional[str] = None
    similarity_score: float
    status: str = Field(description="SUGGESTED, APPROVED, REJECTED, NO_MATCH")
    guard_result: MismatchGuardResult

class CostLogEntry(BaseModel):
    job_id: str
    operation: str = Field(description="VISION_CLASSIFICATION or EMBEDDING_GENERATION")
    items_processed: int
    tokens_used: int
    cost_usd: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
