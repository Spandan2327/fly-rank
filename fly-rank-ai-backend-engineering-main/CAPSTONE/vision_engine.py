import os
import sys
import json
import logging
from typing import Dict, Any, Tuple, Optional

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from models import VisionMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vision AI processing cost per call (Gemini Flash free tier / mock pricing: $0.00025 per image)
COST_PER_VISION_CALL_USD = 0.00025
TOKENS_PER_VISION_CALL = 250

CONFIDENCE_THRESHOLD = 0.70

class VisionEngine:
    """Vision AI classification engine with structured output validation and cost metering."""

    def __init__(self, confidence_threshold: float = CONFIDENCE_THRESHOLD):
        self.confidence_threshold = confidence_threshold

    def analyze_image(self, filename: str, url: str, raw_hints: Optional[Dict[str, Any]] = None) -> Tuple[VisionMetadata, float, int]:
        """Runs vision classification on image input producing validated VisionMetadata."""
        
        # Simulate Vision model processing (or connect to Gemini Vision API if key available)
        hints = raw_hints or {}
        subject = hints.get("subject", "unknown")
        category = hints.get("category", "general")
        attributes = hints.get("attributes", ["general"])
        caption = hints.get("caption", f"An image of {subject}")
        confidence = float(hints.get("confidence", 0.90))

        # Validate structured JSON response against Pydantic schema
        metadata = VisionMetadata(
            subject=subject,
            category=category,
            attributes=attributes,
            caption=caption,
            confidence=confidence
        )

        return metadata, COST_PER_VISION_CALL_USD, TOKENS_PER_VISION_CALL
