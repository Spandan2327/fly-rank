import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

DEFAULT_DB_URL = "postgresql://postgres:dev@localhost:5432/tasks"

def get_db_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DB_URL)

def get_db_connection(db_url: Optional[str] = None):
    url = db_url or get_db_url()
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

def init_db(db_url: Optional[str] = None):
    """Initialize PostgreSQL database table and seed initial 3 tasks if table is empty."""
    conn = get_db_connection(db_url)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        );
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM tasks;")
    row = cursor.fetchone()
    count = row["count"] if row else 0

    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (%s, %s);",
            [
                ("Buy groceries", False),
                ("Read FastAPI documentation", True),
                ("Build CRUD API assignment", False)
            ]
        )
        conn.commit()

    cursor.close()
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
        conditions.append("done = %s")
        params.append(done)

    if search:
        conditions.append("title ILIKE %s")
        params.append(f"%{search}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id ASC"

    if limit is not None:
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset or 0])
    elif offset and offset > 0:
        query += " OFFSET %s"
        params.append(offset)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]

def get_task_by_id_db(task_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (task_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
    return None

def create_task_db(title: str, done: bool = False) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done;",
        (title, done)
    )
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

def update_task_db(task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    existing = get_task_by_id_db(task_id)
    if not existing:
        return None

    new_title = title if title is not None else existing["title"]
    new_done = done if done is not None else existing["done"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done;",
        (new_title, new_done, task_id)
    )
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

def delete_task_db(task_id: int) -> bool:
    existing = get_task_by_id_db(task_id)
    if not existing:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def get_stats_db() -> Dict[str, int]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) AS total,
            COALESCE(SUM(CASE WHEN done THEN 1 ELSE 0 END), 0) AS done,
            COALESCE(SUM(CASE WHEN NOT done THEN 1 ELSE 0 END), 0) AS open
        FROM tasks;
    """)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return {"total": row["total"], "done": row["done"], "open": row["open"]}

def reset_db() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE tasks RESTART IDENTITY;")
    cursor.executemany(
        "INSERT INTO tasks (title, done) VALUES (%s, %s);",
        [
            ("Buy groceries", False),
            ("Read FastAPI documentation", True),
            ("Build CRUD API assignment", False)
        ]
    )
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM tasks;")
    row = cursor.fetchone()
    count = row["count"]
    cursor.close()
    conn.close()
    return count
