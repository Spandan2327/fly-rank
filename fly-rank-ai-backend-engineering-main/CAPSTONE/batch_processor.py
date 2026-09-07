import sys
import os
import json
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from database import get_db_connection, init_db
from vision_engine import VisionEngine, CONFIDENCE_THRESHOLD
from models import ImageRecord, CostLogEntry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchProcessor:
    """Background job processor for bulk vision classification and cost tracking."""

    def __init__(self):
        init_db()
        self.vision_engine = VisionEngine()

    def process_all_pending_images(self, image_hints: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM images WHERE status = 'PENDING';")
        pending_rows = cursor.fetchall()

        if not pending_rows and image_hints:
            for idx, hint in enumerate(image_hints, 1):
                img_id = f"img-{idx:03d}"
                cursor.execute("""
                    INSERT OR IGNORE INTO images (id, filename, url, status, created_at)
                    VALUES (?, ?, ?, 'PENDING', ?);
                """, (img_id, hint["filename"], hint["url"], datetime.utcnow().isoformat() + "Z"))
            conn.commit()
            cursor.execute("SELECT * FROM images WHERE status = 'PENDING';")
            pending_rows = cursor.fetchall()

        job_id = f"job-{uuid.uuid4().hex[:8]}"
        processed_count = 0
        flagged_count = 0
        total_tokens = 0
        total_cost_usd = 0.0

        hints_dict = {h["filename"]: h for h in (image_hints or [])}

        for row in pending_rows:
            img_id = row["id"]
            filename = row["filename"]
            url = row["url"]
            raw_hint = hints_dict.get(filename, {})

            try:
                metadata, cost_usd, tokens = self.vision_engine.analyze_image(
                    filename=filename, url=url, raw_hints=raw_hint
                )

                status = "PROCESSED"
                if metadata.confidence < CONFIDENCE_THRESHOLD:
                    status = "FLAGGED_LOW_CONFIDENCE"
                    flagged_count += 1

                attrs_json = json.dumps(metadata.attributes)

                cursor.execute("""
                    UPDATE images
                    SET subject = ?, category = ?, attributes = ?, caption = ?, confidence = ?, status = ?, cost_usd = ?
                    WHERE id = ?;
                """, (
                    metadata.subject,
                    metadata.category,
                    attrs_json,
                    metadata.caption,
                    metadata.confidence,
                    status,
                    cost_usd,
                    img_id
                ))

                processed_count += 1
                total_tokens += tokens
                total_cost_usd += cost_usd

            except Exception as e:
                logger.error(f"Failed processing image {img_id}: {e}")

        if processed_count > 0:
            cursor.execute("""
                INSERT INTO cost_logs (job_id, operation, items_processed, tokens_used, cost_usd, timestamp)
                VALUES (?, 'VISION_CLASSIFICATION', ?, ?, ?, ?);
            """, (
                job_id,
                processed_count,
                total_tokens,
                total_cost_usd,
                datetime.utcnow().isoformat() + "Z"
            ))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Batch Job {job_id} complete: {processed_count} images processed ({flagged_count} flagged), Cost: ${total_cost_usd:.5f}")

        return {
            "job_id": job_id,
            "processed_count": processed_count,
            "flagged_count": flagged_count,
            "tokens_used": total_tokens,
            "cost_usd": total_cost_usd
        }
