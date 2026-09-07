# Stage 6: The AI Rematch (AI vs Me Comparison for Containerized Stack)

This directory contains the Stage 6 Bonus AI Rematch exercise for Assignment BE-04.

---

## 🤖 1. Initial Prompt (`prompt.txt`)

```text
Containerize our FastAPI To-Do List CRUD API using PostgreSQL in Docker Compose.

Requirements:
1. Database: PostgreSQL container in docker compose with POSTGRES_PASSWORD and POSTGRES_DB loaded from .env file.
2. Persistence: Use a named volume taskdata so database rows survive restarts.
3. Seeding: Insert 3 default example tasks ("Buy groceries", "Read FastAPI documentation", "Build CRUD API assignment") ONLY if the tasks table is empty.
4. Endpoints: Keep identical external HTTP API contract (GET /, GET /health, GET /tasks, GET /tasks/{id}, POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id}).
5. Security: Parameterized SQL queries (%s) with psycopg2 and no hardcoded credentials in source code.
6. One-Command Startup: Single docker compose up starts both api and db services.
```

---

## 🔍 2. AI vs Me Analysis

### Question 1: What did the AI do better?
- **Fast boilerplate generation**: Generated the `Dockerfile`, `compose.yaml`, and database connection code in seconds.
- **`RETURNING id, title, done` in SQL**: The AI used PostgreSQL's `RETURNING` clause correctly for `POST` and `PUT` queries.

### Question 2: What did it get wrong or quietly ignore from your prompt?
- **Database host mismatch (`localhost` vs `db`)**: The AI hardcoded `localhost:5432` in default fallback strings instead of using the Compose service hostname `db:5432`. Inside Docker network, `localhost` points to the `api` container itself, causing connection refused errors unless overridden.
- **Race Condition on Startup (`depends_on`)**: The AI specified basic `depends_on: [db]` without a `pg_isready` healthcheck. As a result, the `api` container launched before Postgres finished initializing, crashing the app on first boot.
- **Default FastAPI `detail` key instead of required `error` key**: Used standard `HTTPException(detail="...")` instead of custom JSON formatting `{"error": "..."}`.
- **Status code 422 vs 400 for empty payloads**: Missing Pydantic validation handlers returned 422 Unprocessable Entity instead of 400 Bad Request.

### Question 3: What did your prompt forget to specify — and what did the AI silently decide for you?
- **Forgot to specify container healthcheck conditions**: The prompt didn't mention `healthcheck` or `service_healthy`. The AI silently used basic `depends_on`, causing startup timing crashes.
- **Forgot to specify `.env.example` file**: The AI generated `.env` directly without creating a committed template `.env.example`.

---

## 🔄 3. The Rematch & What Changed

### Improved Prompt (`improved_prompt.txt`)
Explicitly specified:
1. Compose service name `db` for network routing (`postgresql://postgres:dev@db:5432/tasks`).
2. `healthcheck` with `pg_isready` and `depends_on: db: condition: service_healthy`.
3. Checking `SELECT COUNT(*) FROM tasks == 0` before seeding.
4. Exception handlers returning `{"error": "..."}` format for 400 Bad Request and 404 Not Found.
5. SQL query parameters (`done`, `search` with `ILIKE %...%`, `ORDER BY`, `LIMIT`/`OFFSET`).

### One-Sentence Rematch Summary:
> *Adding explicit Docker Compose service name routing and PostgreSQL `pg_isready` healthchecks prevented container startup crashes and allowed the multi-container stack to boot reliably on the first attempt.*
