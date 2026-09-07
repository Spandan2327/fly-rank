import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Containerized Task API", version="3.0")

# AI Mistake 1: Hardcoded connection string instead of reading DATABASE_URL from environment / .env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dev@localhost:5432/tasks")

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)
    # AI Mistake 2: Did not wrap seeding in SELECT COUNT(*) == 0 check
    cursor.execute("INSERT INTO tasks (title, done) VALUES ('Buy groceries', false) ON CONFLICT DO NOTHING;")
    cursor.execute("INSERT INTO tasks (title, done) VALUES ('Read FastAPI documentation', true) ON CONFLICT DO NOTHING;")
    cursor.execute("INSERT INTO tasks (title, done) VALUES ('Build CRUD API assignment', false) ON CONFLICT DO NOTHING;")
    conn.commit()
    cursor.close()
    conn.close()

init_db()

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/")
def get_root():
    return {"name": "Containerized Task API", "version": "3.0", "storage": "PostgreSQL"}

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks ORDER BY id ASC;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]

@app.get("/tasks/{id}")
def get_task(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, false) RETURNING id, title, done;", (task.title.strip(),))
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

@app.put("/tasks/{id}")
def update_task(id: int, task: TaskUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (id,))
    existing = cursor.fetchone()
    if not existing:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {id} not found")

    new_title = task.title.strip() if task.title and task.title.strip() else existing["title"]
    new_done = task.done if task.done is not None else existing["done"]

    cursor.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done;", (new_title, new_done, id))
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s RETURNING id;", (id,))
    deleted = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
