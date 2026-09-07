# FlyRank AI Internship — BE-02: Connecting Your CRUD to SQLite Database

A production-grade **SQLite-backed To-Do List CRUD API** built using **Python 3.10+** and **FastAPI**, featuring automatic database table initialization, single-time idempotent seeding, parameterized SQL queries, interactive Swagger UI documentation, and 100% test coverage.

---

## 🚀 Quick Start (One Documented Command)

Run the SQLite API server with a single command from the repository root:

```bash
source BE-02/.venv/bin/activate && uvicorn BE-02.main:app --reload --port 8000
```

Once running, access:
- **API Base URL:** `http://localhost:8000`
- **Interactive Swagger UI Docs:** `http://localhost:8000/docs`

---

## 💡 Why SQLite?

In Assignment BE-01, tasks were stored in-memory in a Python list. Every time the server restarted, all data vanished. 

In Assignment BE-02, we swapped the storage layer for **SQLite**:
1. **Zero Configuration & Serverless:** SQLite stores data directly in a single local file (`tasks.db`), requiring no separate database server process (like PostgreSQL or MySQL).
2. **True Persistence:** Data outlives application restarts and server crashes.
3. **Identical API Contract:** The external HTTP endpoints, request shapes, and status codes remain 100% identical to BE-01. Storage is simply an implementation detail.

---

## 📂 Database Initialization & Auto-Creation

- **Database File:** [`BE-02/tasks.db`](tasks.db) (created automatically on startup if missing).
- **Git Ignored:** `tasks.db` is added to `.gitignore` so each clone starts fresh.
- **Idempotent Seeding:** On startup, the application checks `SELECT COUNT(*) FROM tasks`. If count is `0`, it seeds the 3 default example tasks inside a database transaction:
  1. `"Buy groceries"` (`done = 0`)
  2. `"Read FastAPI documentation"` (`done = 1`)
  3. `"Build CRUD API assignment"` (`done = 0`)

Restarting the server multiple times does **not** duplicate seed data.

---

## 📋 Endpoints Summary

| HTTP Method | Endpoint | Description | SQL Query | Status Codes |
|-------------|----------|-------------|-----------|--------------|
| `GET` | `/` | API Root Metadata | N/A | `200 OK` |
| `GET` | `/health` | Health Check | N/A | `200 OK` |
| `GET` | `/tasks` | List Tasks | `SELECT id, title, done FROM tasks` | `200 OK` |
| `GET` | `/tasks/{id}` | Get Task by ID | `SELECT * FROM tasks WHERE id = ?` | `200 OK`, `404` |
| `POST` | `/tasks` | Create Task | `INSERT INTO tasks (title, done) VALUES (?, ?)` | `201`, `400` |
| `PUT` | `/tasks/{id}` | Update Task | `UPDATE tasks SET title = ?, done = ? WHERE id = ?` | `200`, `400`, `404` |
| `DELETE` | `/tasks/{id}` | Delete Task | `DELETE FROM tasks WHERE id = ?` | `204`, `404` |
| `GET` | `/stats` | Task Statistics | `SELECT COUNT(*), SUM(...) FROM tasks` | `200 OK` |
| `POST` | `/reset` | Reset Seed Data | `DELETE FROM tasks` + re-seed | `200 OK` |

---

## 🔍 Stage 4: Hand-Run SQL Exploration

Using the `sqlite3` CLI / DB Browser for SQLite:

### Query 1: List all tasks
```sql
SELECT * FROM tasks;
```
*Output:*
```text
1|Buy groceries|0
2|Read FastAPI documentation|1
3|Build CRUD API assignment|0
```

### Query 2: Only completed tasks
```sql
SELECT * FROM tasks WHERE done = 1;
```
*Output:* `2|Read FastAPI documentation|1`

### Query 3: Count total tasks
```sql
SELECT COUNT(*) FROM tasks;
```
*Output:* `3`

---

## 🛡️ Parameterized Queries & Security

All database interactions use parameterized SQL placeholders (`?`):

```python
cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
```

**Why this matters:** Passing parameters separately from the SQL string prevents **SQL Injection** attacks, ensuring user input is safely treated as literal data rather than executable code.

---

## 🤖 Stage 6: AI vs Me (AI Rematch)

As part of the Stage 6 bonus challenge, we benchmarked hand-built code against an AI-generated solution kept in a quarantine folder ([`BE-02/ai-version/`](ai-version/)).

Key findings:
- **What AI did well:** Fast generation of single-file SQLite endpoint handlers.
- **Where AI failed:** Used `INSERT OR IGNORE` with hardcoded IDs instead of checking `SELECT COUNT(*) FROM tasks == 0`, causing deleted tasks to re-appear on restart. Also defaulted to `422` for empty payloads and `detail` key instead of custom `error` key.
- **Rematch takeaway:** Specifying explicit `COUNT(*)` row checks and custom exception handlers produced 100% test pass rate.

See full analysis in [BE-02/ai-version/README.md](ai-version/README.md).

---

## 🧪 Running Automated Tests

Run the test suite powered by `pytest` and `httpx`:

```bash
BE-02/.venv/bin/pytest BE-02/test_main.py -v
```
