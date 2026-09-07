# Stage 6: The AI Rematch (AI vs Me Comparison for SQLite Migration)

This directory contains the Stage 6 Bonus AI Rematch exercise for Assignment BE-02.

---

## 🤖 1. Initial Prompt (`prompt.txt`)

```text
Migrate our existing FastAPI To-Do List CRUD API from in-memory storage to a SQLite database.

Requirements:
1. Database: SQLite database named tasks.db. Automatically create table tasks if it does not exist (columns: id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0).
2. Seeding: Insert 3 default example tasks ("Buy groceries", "Read FastAPI documentation", "Build CRUD API assignment") ONLY if the table is empty.
3. Endpoints: Keep identical external endpoint contract and response format:
   - GET /: Returns JSON { "name": "Task Database API", "version": "2.0", "storage": "SQLite (tasks.db)", "endpoints": ["/tasks"] }
   - GET /health: Returns JSON { "status": "ok" }
   - GET /tasks: Returns all tasks from SQLite.
   - GET /tasks/{id}: Returns single task or 404 error { "error": "Task {id} not found" }.
   - POST /tasks: Accepts { "title": "..." }, validates non-empty title, inserts into SQLite, returns 201 Created + task object. Invalid/missing title -> 400 Bad Request { "error": "..." }.
   - PUT /tasks/{id}: Updates title/done in SQLite. Unknown id -> 404, invalid body -> 400.
   - DELETE /tasks/{id}: Deletes task from SQLite, returns 204 No Content. Unknown id -> 404.
4. Security: Use parameterized SQL queries for all database operations to prevent SQL injection.
```

---

## 🔍 2. AI vs Me Analysis

### Question 1: What did the AI do better?
- **Immediate single-file inline execution**: The AI wrote all database setup and endpoint logic inside a single `ai_main.py` file, making it easy to run for one-off manual testing.
- **`INSERT OR IGNORE` idiom**: The AI knew the SQLite `INSERT OR IGNORE` clause syntax for primary key conflicts.

### Question 2: What did it get wrong or quietly ignore from your prompt?
- **Flawed Seeding Logic (`INSERT OR IGNORE`)**: Instead of checking `SELECT COUNT(*) FROM tasks` first as requested, the AI used `INSERT OR IGNORE INTO tasks (id, ...) VALUES (1, ...)` with hardcoded IDs. If tasks with IDs 1, 2, 3 were deleted during use, restarting the server restored those deleted tasks, violating the requirement that seeding occurs *only* when the table is completely empty.
- **Default FastAPI `detail` key instead of required `error` key**: `HTTPException(status_code=404, detail="...")` returned `{"detail": "..."}` instead of `{"error": "..."}`.
- **Missing Pydantic schema error interception**: An empty body `{}` sent to `POST /tasks` returned status `422 Unprocessable Entity` instead of `400 Bad Request`.
- **Ignored query parameters & stretch endpoints**: Did not include `search`, `done` SQL filters, pagination (`limit`/`offset`), `GET /stats`, or `POST /reset`.

### Question 3: What did your prompt forget to specify — and what did the AI silently decide for you?
- **Forgot to specify row count checking method**: The prompt said "ONLY if table is empty", but didn't specify checking `COUNT(*)`. The AI silently decided to use hardcoded `INSERT OR IGNORE` instead.
- **Forgot to specify database connection modularity**: The prompt did not specify creating a separate `database.py` module, so the AI put `sqlite3.connect()` calls directly inside every endpoint handler.

---

## 🔄 3. The Rematch & What Changed

### Improved Prompt (`improved_prompt.txt`)
Explicitly specified:
1. Modular `database.py` with `get_db_connection()`.
2. Checking `SELECT COUNT(*) FROM tasks == 0` before executing seed inserts in a single transaction.
3. Registering exception handlers for `RequestValidationError` and `HTTPException` to format error output as `{"error": "..."}` with status code `400`.
4. SQL query filters (`done`, `search` with `LIKE %...%`, `ORDER BY id ASC`, `LIMIT`/`OFFSET`).

### One-Sentence Rematch Summary:
> *Explicitly specifying `SELECT COUNT(*)` row checks and custom Pydantic exception handlers fixed both the seed-restoration bug and the status 422 mismatch, producing 100% test pass rate on first run.*
