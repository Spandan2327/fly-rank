import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app
from models import VisionMetadata, ImageRecord, BlogPost, MismatchGuardResult
from vision_engine import VisionEngine
from batch_processor import BatchProcessor
from embedding_engine import EmbeddingEngine
from mismatch_guard import MismatchGuard
from seed_data import seed_database, SEED_IMAGES

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

def test_vision_metadata_schema_validation():
    data = {
        "subject": "red fox",
        "category": "animal",
        "attributes": ["orange fur", "wild", "forest"],
        "caption": "A red fox standing in a forest",
        "confidence": 0.94
    }
    meta = VisionMetadata(**data)
    assert meta.subject == "red fox"
    assert meta.category == "animal"
    assert meta.confidence == 0.94

def test_mismatch_guard_result():
    res = MismatchGuardResult(
        passed=False,
        status="REJECTED",
        similarity_score=0.45,
        reason="Animal category mismatch: expected fox, detected wolf"
    )
    assert res.passed is False
    assert res.status == "REJECTED"
    assert "detected wolf" in res.reason

def test_vision_engine_classification():
    engine = VisionEngine()
    meta, cost, tokens = engine.analyze_image(
        filename="fox_01.jpg",
        url="https://example.com/fox.jpg",
        raw_hints={"subject": "red fox", "category": "animal", "caption": "A red fox in meadow", "confidence": 0.95}
    )
    assert meta.subject == "red fox"
    assert meta.confidence == 0.95
    assert cost > 0.0
    assert tokens > 0

def test_batch_processor_and_low_confidence_flagging():
    processor = BatchProcessor()
    res = processor.process_all_pending_images(image_hints=SEED_IMAGES)
    assert res["processed_count"] > 0
    assert res["flagged_count"] >= 1
    assert res["cost_usd"] > 0.0

def test_embedding_engine_cosine_similarity():
    engine = EmbeddingEngine()
    vec_fox_post, _, _ = engine.get_embedding("Understanding red foxes in the forest")
    vec_fox_img, _, _ = engine.get_embedding("A bright orange red fox in a forest meadow")
    vec_wolf_img, _, _ = engine.get_embedding("A gray wolf standing on a rocky ledge")

    sim_fox = engine.cosine_similarity(vec_fox_post, vec_fox_img)
    sim_wolf = engine.cosine_similarity(vec_fox_post, vec_wolf_img)

    assert sim_fox > sim_wolf
    assert sim_fox >= 0.65

def test_mismatch_guard_wolf_rejection_for_fox_post():
    guard = MismatchGuard()
    post = BlogPost(
        id="post-fox",
        title="Behavior of Red Foxes",
        category="animal",
        topic="red fox",
        content="Article about red foxes"
    )

    wolf_image = {
        "id": "img-wolf",
        "subject": "wolf",
        "category": "animal",
        "caption": "A gray wolf in the forest",
        "confidence": 0.94
    }

    res = guard.evaluate_match(post=post, image_data=wolf_image, similarity_score=0.85)
    assert res.passed is False
    assert res.status == "REJECTED"
    assert "Animal category mismatch" in res.reason
    assert "expected red fox, detected wolf" in res.reason

def test_get_image_suggestions_red_fox_ranks_first():
    response = client.get("/posts/post-001/images")
    assert response.status_code == 200
    data = response.json()
    assert data["post_id"] == "post-001"
    assert data["status"] in ("SUGGESTED", "ACCEPTED")
    assert data["image_id"] in ("img-001", "img-002")

def test_forced_wolf_rejection_via_api():
    response = client.get("/posts/post-001/images?force_image_id=img-003")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REJECTED"
    assert data["guard_result"]["passed"] is False
    assert "expected red fox, detected wolf" in data["guard_result"]["reason"]

def test_human_review_workflow():
    sug_resp = client.get("/posts/post-001/images")
    sug_id = sug_resp.json()["id"]

    # Test approve workflow
    app_resp = client.post(f"/suggestions/{sug_id}/approve")
    assert app_resp.status_code == 200
    assert app_resp.json()["status"] == "APPROVED"

    # Test reject workflow
    rej_resp = client.post(f"/suggestions/{sug_id}/reject", json={"reason": "Incorrect lighting"})
    assert rej_resp.status_code == 200
    assert rej_resp.json()["status"] == "REJECTED"

def test_cost_tracking_endpoint():
    client.post("/batch/process-images")
    response = client.get("/stats/costs")
    assert response.status_code == 200
    data = response.json()
    assert "total_cost_usd" in data
    assert "total_tokens_used" in data
    assert len(data["job_logs"]) > 0

def test_evaluation_top_1_precision():
    response = client.get("/eval")
    assert response.status_code == 200
    data = response.json()
    assert data["eval_count"] == 5
    assert data["top_1_precision_percentage"] == 100.0
