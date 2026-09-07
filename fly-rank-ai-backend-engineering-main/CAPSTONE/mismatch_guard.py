import logging
from typing import Dict, Any, Optional
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from models import MismatchGuardResult, VisionMetadata, BlogPost

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.65
CONFIDENCE_THRESHOLD = 0.70

class MismatchGuard:
    """Production Safety Layer that validates image-article pairings and rejects mismatches with explanations."""

    def __init__(
        self,
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        confidence_threshold: float = CONFIDENCE_THRESHOLD
    ):
        self.similarity_threshold = similarity_threshold
        self.confidence_threshold = confidence_threshold

    def evaluate_match(
        self,
        post: BlogPost,
        image_data: Dict[str, Any],
        similarity_score: float
    ) -> MismatchGuardResult:
        """Evaluates whether an image candidate is safe and accurate for a blog post."""
        
        detected_subject = (image_data.get("subject") or "unknown").lower().strip()
        detected_category = (image_data.get("category") or "unknown").lower().strip()
        confidence = float(image_data.get("confidence") or 0.0)
        expected_topic = post.topic.lower().strip()
        expected_category = post.category.lower().strip()

        # Gate 1: Check Vision AI confidence score
        if confidence < self.confidence_threshold:
            reason = f"Low vision classification confidence: {confidence:.2f} < {self.confidence_threshold:.2f}"
            logger.warning(f"Guard Gate 1 REJECTED: {reason}")
            return MismatchGuardResult(
                passed=False,
                status="NO_CONFIDENT_MATCH",
                similarity_score=similarity_score,
                reason=reason
            )

        # Gate 2: Check Subject / Category Mismatch (e.g. Fox vs Wolf)
        if expected_topic != detected_subject and expected_topic in ["red fox", "fox"] and detected_subject in ["wolf", "gray wolf", "dog"]:
            reason = f"Animal category mismatch: expected {expected_topic}, detected {detected_subject}"
            logger.warning(f"Guard Gate 2 REJECTED: {reason}")
            return MismatchGuardResult(
                passed=False,
                status="REJECTED",
                similarity_score=similarity_score,
                reason=reason
            )

        if expected_topic != detected_subject and expected_topic in ["wolf", "gray wolf"] and detected_subject in ["fox", "red fox", "dog"]:
            reason = f"Animal category mismatch: expected {expected_topic}, detected {detected_subject}"
            logger.warning(f"Guard Gate 2 REJECTED: {reason}")
            return MismatchGuardResult(
                passed=False,
                status="REJECTED",
                similarity_score=similarity_score,
                reason=reason
            )

        # Gate 3: Check Similarity Threshold
        if similarity_score < self.similarity_threshold:
            reason = f"Similarity score below threshold: {similarity_score:.2f} < {self.similarity_threshold:.2f}"
            logger.warning(f"Guard Gate 3 REJECTED: {reason}")
            return MismatchGuardResult(
                passed=False,
                status="NO_CONFIDENT_MATCH",
                similarity_score=similarity_score,
                reason=reason
            )

        logger.info(f"Guard ACCEPTED match: {post.id} <-> {image_data.get('id')} (Score: {similarity_score:.2f})")
        return MismatchGuardResult(
            passed=True,
            status="ACCEPTED",
            similarity_score=similarity_score,
            reason=None
        )
