import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db_before_each_test():
    client.post("/reset")

def test_swagger_ui_endpoint():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower() or "html" in response.text.lower()

def test_openapi_json():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    assert openapi["info"]["title"] == "Task API"
    assert "/tasks" in openapi["paths"]
    assert "/tasks/{task_id}" in openapi["paths"]

def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Task API"
    assert data["version"] == "1.0"
    assert "/tasks" in data["endpoints"]

def test_get_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_all_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3

def test_get_single_task_success():
    response = client.get("/tasks/1")
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == 1
    assert task["title"] == "Buy groceries"

def test_get_single_task_not_found():
    response = client.get("/tasks/99")
    assert response.status_code == 404
    assert response.json() == {"error": "Task 99 not found"}

def test_create_task_success():
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Buy milk"
    assert task["done"] is False
    assert task["id"] == 4

def test_create_task_validation_empty_body():
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert "error" in response.json()

def test_create_task_validation_empty_title():
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 400
    assert "error" in response.json()

def test_update_task_success():
    response = client.put("/tasks/1", json={"title": "Buy organic groceries", "done": True})
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == 1
    assert task["title"] == "Buy organic groceries"
    assert task["done"] is True

def test_update_task_not_found():
    response = client.put("/tasks/999", json={"title": "Non-existent task"})
    assert response.status_code == 404
    assert response.json() == {"error": "Task 999 not found"}

def test_update_task_invalid_empty_body():
    response = client.put("/tasks/1", json={})
    assert response.status_code == 400
    assert "error" in response.json()

def test_delete_task_success():
    response = client.delete("/tasks/1")
    assert response.status_code == 204
    assert response.content == b""
    verify_resp = client.get("/tasks/1")
    assert verify_resp.status_code == 404

def test_delete_task_not_found():
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"error": "Task 999 not found"}

def test_query_filter_done():
    resp_done = client.get("/tasks?done=true")
    assert resp_done.status_code == 200
    assert len(resp_done.json()) == 1
    assert resp_done.json()[0]["id"] == 2

    resp_open = client.get("/tasks?done=false")
    assert resp_open.status_code == 200
    assert len(resp_open.json()) == 2

def test_query_search():
    resp = client.get("/tasks?search=FastAPI")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == 2

def test_query_pagination():
    resp = client.get("/tasks?limit=2&offset=1")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    assert resp.json()[0]["id"] == 2
    assert resp.json()[1]["id"] == 3

def test_stats_endpoint():
    resp = client.get("/stats")
    assert resp.status_code == 200
    assert resp.json() == {"total": 3, "done": 1, "open": 2}
