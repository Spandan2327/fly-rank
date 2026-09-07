import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database import init_db, get_db_connection, reset_db
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    client.post("/reset")

def test_postgres_table_seeding():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks;")
    row = cursor.fetchone()
    count = row["count"]
    assert count == 3
    cursor.close()
    conn.close()

def test_read_all_tasks_postgres():
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3
    assert tasks[0]["id"] == 1
    assert tasks[0]["title"] == "Buy groceries"

def test_read_single_task_success():
    response = client.get("/tasks/1")
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == 1
    assert task["title"] == "Buy groceries"
    assert task["done"] is False

def test_read_single_task_not_found():
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"error": "Task 999 not found"}

def test_create_task_postgres_success():
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Buy milk"
    assert task["done"] is False
    assert task["id"] == 4

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, done FROM tasks WHERE id = 4;")
    row = cursor.fetchone()
    assert row["title"] == "Buy milk"
    assert row["done"] is False
    cursor.close()
    conn.close()

def test_create_task_validation_empty_body():
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert "error" in response.json()

def test_create_task_validation_empty_title():
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 400
    assert "error" in response.json()

def test_update_task_postgres_success():
    response = client.put("/tasks/1", json={"title": "Buy organic groceries", "done": True})
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == 1
    assert task["title"] == "Buy organic groceries"
    assert task["done"] is True

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, done FROM tasks WHERE id = 1;")
    row = cursor.fetchone()
    assert row["title"] == "Buy organic groceries"
    assert row["done"] is True
    cursor.close()
    conn.close()

def test_update_task_not_found():
    response = client.put("/tasks/999", json={"title": "Non-existent task"})
    assert response.status_code == 404
    assert response.json() == {"error": "Task 999 not found"}

def test_update_task_invalid_empty_body():
    response = client.put("/tasks/1", json={})
    assert response.status_code == 400
    assert "error" in response.json()

def test_delete_task_postgres_success():
    response = client.delete("/tasks/1")
    assert response.status_code == 204
    assert response.content == b""

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = 1;")
    assert cursor.fetchone() is None
    cursor.close()
    conn.close()

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

def test_query_search_ilike():
    resp = client.get("/tasks?search=fastapi")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == 2

def test_query_pagination():
    resp = client.get("/tasks?limit=2&offset=1")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    assert resp.json()[0]["id"] == 2
    assert resp.json()[1]["id"] == 3

def test_stats_endpoint_postgres():
    resp = client.get("/stats")
    assert resp.status_code == 200
    assert resp.json() == {"total": 3, "done": 1, "open": 2}
