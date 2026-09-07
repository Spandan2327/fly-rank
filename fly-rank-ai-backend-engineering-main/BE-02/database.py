import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "tasks.db")

def get_db_path() -> str:
    return os.environ.get("TEST_DB", DB_PATH)

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Optional[str] = None):
    """Initialize SQLite database, create table if missing, and seed initial tasks only if empty."""
    target_path = db_path or get_db_path()
    conn = sqlite3.connect(target_path)
    cursor = conn.cursor()

    # Create tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()

    # Check row count
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    # Seed only if table is empty
    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Buy groceries", 0),
                ("Read FastAPI documentation", 1),
                ("Build CRUD API assignment", 0)
            ]
        )
        conn.commit()

    conn.close()

def get_all_tasks_db(
    done: Optional[bool] = None,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0
) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT id, title, done FROM tasks"
    conditions = []
    params = []

    if done is not None:
        conditions.append("done = ?")
        params.append(1 if done else 0)

    if search:
        conditions.append("title LIKE ?")
        params.append(f"%{search}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id ASC"

    if limit is not None:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset or 0])
    elif offset and offset > 0:
        query += " LIMIT -1 OFFSET ?"
        params.append(offset)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]

def get_task_by_id_db(task_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
    return None

def create_task_db(title: str, done: bool = False) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    done_int = 1 if done else 0
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, done_int))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "title": title, "done": done}

def update_task_db(task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    existing = get_task_by_id_db(task_id)
    if not existing:
        return None

    new_title = title if title is not None else existing["title"]
    new_done = done if done is not None else existing["done"]
    new_done_int = 1 if new_done else 0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (new_title, new_done_int, task_id))
    conn.commit()
    conn.close()
    return {"id": task_id, "title": new_title, "done": new_done}

def delete_task_db(task_id: int) -> bool:
    existing = get_task_by_id_db(task_id)
    if not existing:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return True

def get_stats_db() -> Dict[str, int]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) AS total,
            COALESCE(SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END), 0) AS done,
            COALESCE(SUM(CASE WHEN done = 0 THEN 1 ELSE 0 END), 0) AS open
        FROM tasks
    """)
    row = cursor.fetchone()
    conn.close()
    return {"total": row["total"], "done": row["done"], "open": row["open"]}

def reset_db() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
    cursor.executemany(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        [
            ("Buy groceries", 0),
            ("Read FastAPI documentation", 1),
            ("Build CRUD API assignment", 0)
        ]
    )
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    conn.close()
    return count
