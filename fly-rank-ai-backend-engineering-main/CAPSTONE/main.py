from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import sqlite3
import json
import uuid
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from database import get_db_connection, init_db
from models import BlogPost, MatchSuggestion, MismatchGuardResult, ImageRecord
from batch_processor import BatchProcessor
from embedding_engine import EmbeddingEngine
from mismatch_guard import MismatchGuard
from seed_data import seed_database, SEED_IMAGES, SEED_POSTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_database()
    logger.info("Capstone Engine running: database initialized and seeded")
    yield

app = FastAPI(
    title="AI Image Understanding & Content Matching Engine",
    description="FlyRank Backend Track Capstone API for AI Vision Classification, Vector Similarity Matching, and Mismatch Guard Safety",
    version="1.0.0",
    lifespan=lifespan
)

batch_processor = BatchProcessor()
embedding_engine = EmbeddingEngine()
mismatch_guard = MismatchGuard()

@app.get("/")
def get_root():
    return {
        "name": "AI Image Understanding & Content Matching Engine",
        "track": "FlyRank Backend AI Engineering Track (Capstone)",
        "version": "1.0.0",
        "endpoints": [
            "/batch/process-images",
            "/posts/{id}/images",
            "/suggestions/{id}/approve",
            "/suggestions/{id}/reject",
            "/stats/costs",
            "/eval"
        ]
    }

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.post("/batch/process-images", summary="Trigger Background Vision Processing Batch Job")
def run_batch_job():
    result = batch_processor.process_all_pending_images(image_hints=SEED_IMAGES)
    return {
        "message": "Batch image processing complete",
        "job": result
    }

@app.get("/posts/{post_id}/images", summary="Get Image Suggestions for Blog Post")
def get_image_suggestions_for_post(post_id: str, force_image_id: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM posts WHERE id = ?;", (post_id,))
    post_row = cursor.fetchone()
    if not post_row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    post = BlogPost(
        id=post_row["id"],
        title=post_row["title"],
        category=post_row["category"],
        topic=post_row["topic"],
        content=post_row["content"]
    )

    post_text = f"{post.title} {post.topic} {post.content}"
    post_vec = embedding_engine.store_embedding("post", post.id, post_text)

    cursor.execute("SELECT * FROM images WHERE status IN ('PROCESSED', 'FLAGGED_LOW_CONFIDENCE');")
    image_rows = cursor.fetchall()

    if not image_rows:
        batch_processor.process_all_pending_images(image_hints=SEED_IMAGES)
        cursor.execute("SELECT * FROM images WHERE status IN ('PROCESSED', 'FLAGGED_LOW_CONFIDENCE');")
        image_rows = cursor.fetchall()

    if force_image_id:
        image_rows = [r for r in image_rows if r["id"] == force_image_id]

    candidates = []
    for r in image_rows:
        attrs = json.loads(r["attributes"]) if r["attributes"] else []
        img_text = f"{r['subject']} {r['category']} {' '.join(attrs)} {r['caption']}"
        img_vec = embedding_engine.store_embedding("image", r["id"], img_text)
        
        sim_score = embedding_engine.cosine_similarity(post_vec, img_vec)
        img_data = {
            "id": r["id"],
            "filename": r["filename"],
            "url": r["url"],
            "subject": r["subject"],
            "category": r["category"],
            "attributes": attrs,
            "caption": r["caption"],
            "confidence": r["confidence"],
            "status": r["status"]
        }
        candidates.append((sim_score, img_data))

    candidates.sort(key=lambda x: x[0], reverse=True)

    if not candidates:
        conn.close()
        return {
            "post_id": post.id,
            "post_title": post.title,
            "suggestion": None,
            "status": "NO_MATCH",
            "message": "No candidates available for evaluation"
        }

    best_match_sug = None
    first_rejection_guard = None
    first_top_sim = None
    first_top_img = None

    for sim, img in candidates:
        guard_res = mismatch_guard.evaluate_match(post=post, image_data=img, similarity_score=sim)
        if first_rejection_guard is None:
            first_rejection_guard = guard_res
            first_top_sim = sim
            first_top_img = img

        if guard_res.passed:
            best_match_sug = (sim, img, guard_res)
            break

    if best_match_sug:
        top_sim, top_img, guard_res = best_match_sug
    else:
        top_sim, top_img, guard_res = first_top_sim, first_top_img, first_rejection_guard

    sug_id = f"sug-{uuid.uuid4().hex[:8]}"
    sug_status = "SUGGESTED" if guard_res.passed else guard_res.status

    cursor.execute("""
        INSERT INTO suggestions (id, post_id, image_id, similarity_score, status, rejection_reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (
        sug_id,
        post.id,
        top_img["id"] if guard_res.passed else None,
        top_sim,
        sug_status,
        guard_res.reason,
        json.dumps(guard_res.model_dump())
    ))
    conn.commit()
    conn.close()

    suggestion_out = MatchSuggestion(
        id=sug_id,
        post_id=post.id,
        post_title=post.title,
        image_id=top_img["id"] if guard_res.passed else None,
        image_url=top_img["url"] if guard_res.passed else None,
        image_caption=top_img["caption"] if guard_res.passed else None,
        similarity_score=top_sim,
        status=sug_status,
        guard_result=guard_res
    )

    return suggestion_out

@app.post("/suggestions/{suggestion_id}/approve", summary="Approve Match Suggestion")
def approve_suggestion(suggestion_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suggestions WHERE id = ?;", (suggestion_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Suggestion {suggestion_id} not found")

    cursor.execute("UPDATE suggestions SET status = 'APPROVED' WHERE id = ?;", (suggestion_id,))
    conn.commit()
    conn.close()

    return {"message": f"Suggestion {suggestion_id} approved", "status": "APPROVED"}

@app.post("/suggestions/{suggestion_id}/reject", summary="Reject Match Suggestion")
def reject_suggestion(suggestion_id: str, reason: Optional[str] = "Human reviewer rejected pairing"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suggestions WHERE id = ?;", (suggestion_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Suggestion {suggestion_id} not found")

    cursor.execute("UPDATE suggestions SET status = 'REJECTED', rejection_reason = ? WHERE id = ?;", (reason, suggestion_id))
    conn.commit()
    conn.close()

    return {"message": f"Suggestion {suggestion_id} rejected", "status": "REJECTED", "reason": reason}

@app.get("/stats/costs", summary="Get AI Processing Cost Logs")
def get_cost_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cost_logs ORDER BY timestamp DESC;")
    rows = cursor.fetchall()
    conn.close()

    logs = [dict(r) for r in rows]
    total_cost = sum(r["cost_usd"] for r in logs)
    total_tokens = sum(r["tokens_used"] for r in logs)

    return {
        "total_cost_usd": total_cost,
        "total_tokens_used": total_tokens,
        "job_logs": logs
    }

@app.get("/eval", summary="Run Evaluation Suite & Calculate Top-1 Precision")
def run_evaluation():
    conn = get_db_connection()
    cursor = conn.cursor()

    eval_dataset = [
        {"post_id": "post-001", "expected_image_id": "img-001"}, # Red fox
        {"post_id": "post-002", "expected_image_id": "img-003"}, # Gray wolf
        {"post_id": "post-003", "expected_image_id": "img-005"}, # Dog
        {"post_id": "post-004", "expected_image_id": "img-007"}, # Bear
        {"post_id": "post-005", "expected_image_id": "img-008"}  # Deer
    ]

    total_evals = len(eval_dataset)
    correct_matches = 0
    results = []

    for item in eval_dataset:
        sug = get_image_suggestions_for_post(post_id=item["post_id"])
        top_img_id = sug.image_id if isinstance(sug, MatchSuggestion) else sug.get("image_id")
        is_correct = (top_img_id == item["expected_image_id"])
        if is_correct:
            correct_matches += 1

        results.append({
            "post_id": item["post_id"],
            "expected_image_id": item["expected_image_id"],
            "suggested_image_id": top_img_id,
            "correct": is_correct
        })

    top_1_precision = (correct_matches / total_evals) * 100.0 if total_evals > 0 else 0.0
    conn.close()

    return {
        "eval_count": total_evals,
        "correct_matches": correct_matches,
        "top_1_precision_percentage": top_1_precision,
        "eval_results": results
    }
