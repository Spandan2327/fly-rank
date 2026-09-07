import sqlite3
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Task Database API", version="2.0")

DB_NAME = "tasks.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    # AI mistake: Seeds tasks every startup without checking count first!
    cursor.execute("INSERT OR IGNORE INTO tasks (id, title, done) VALUES (1, 'Buy groceries', 0)")
    cursor.execute("INSERT OR IGNORE INTO tasks (id, title, done) VALUES (2, 'Read FastAPI documentation', 1)")
    cursor.execute("INSERT OR IGNORE INTO tasks (id, title, done) VALUES (3, 'Build CRUD API assignment', 0)")
    conn.commit()
    conn.close()

init_db()

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/")
def get_root():
    return {"name": "Task Database API", "version": "2.0", "storage": "SQLite (tasks.db)", "endpoints": ["/tasks"]}

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]

@app.get("/tasks/{id}")
def get_task(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()
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
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, 0)", (task.title.strip(),))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "title": task.title.strip(), "done": False}

@app.put("/tasks/{id}")
def update_task(id: int, task: TaskUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {id} not found")

    new_title = task.title.strip() if task.title and task.title.strip() else existing["title"]
    new_done = 1 if task.done else (0 if task.done is False else existing["done"])

    cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (new_title, new_done, id))
    conn.commit()
    conn.close()
    return {"id": id, "title": new_title, "done": bool(new_done)}

@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
