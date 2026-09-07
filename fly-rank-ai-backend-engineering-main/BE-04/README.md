# FlyRank AI Internship — BE-04: Containerize Your Stack (PostgreSQL + Docker Compose)

A production-grade **Containerized To-Do List CRUD API** built using **Python 3.10+**, **FastAPI**, **PostgreSQL**, and **Docker Compose**. 

Swapping the storage layer from memory (A1) and SQLite (A2) to a containerized PostgreSQL engine (A3) ensures the exact same API contract, response shapes, and status codes run identically on any machine or deployment environment.

---

## 🚀 Quick Start (One Command for the Whole Stack)

Clone the repository, copy environment variables, and launch the multi-container stack with a single command:

```bash
cp BE-04/.env.example BE-04/.env && docker compose -f BE-04/compose.yaml up --build -d
```

Once running:
- **API Base URL:** `http://localhost:8000`
- **Interactive Swagger UI Docs:** `http://localhost:8000/docs`
- **Health Check Endpoint:** `http://localhost:8000/health`

To stop the stack and keep persisted data:
```bash
docker compose -f BE-04/compose.yaml down
```

---

## 🔐 Environment Variables & Secrets (`.env`)

Secrets are managed cleanly via environment variables. `BE-04/.env` is ignored by git, while `BE-04/.env.example` is committed:

### `BE-04/.env.example`
```env
DATABASE_URL=postgresql://postgres:dev@localhost:5432/tasks
```

Inside the Docker Compose network, `api` connects to `db` using the service name `db`:
`DATABASE_URL=postgresql://postgres:dev@db:5432/tasks`

---

## 🐳 Docker Stack Architecture (`compose.yaml`)

| Service Name | Image | Role | Port Mapping |
|--------------|-------|------|--------------|
| **`api`** | Built from `Dockerfile` | FastAPI application server | `8000:8000` |
| **`db`** | `postgres:16-alpine` | Relational PostgreSQL database | `5432:5432` |

- **Named Volume (`taskdata`):** Database rows are stored on a persistent Docker volume (`taskdata:/var/lib/postgresql/data`), preserving data across `docker compose down` and `docker compose up`.
- **Healthcheck:** The `api` container waits for PostgreSQL to become healthy (`pg_isready`) before starting.

---

## 📋 Endpoints Summary

| HTTP Method | Endpoint | Description | PostgreSQL Query | Status Codes |
|-------------|----------|-------------|------------------|--------------|
| `GET` | `/` | API Root Metadata | N/A | `200 OK` |
| `GET` | `/health` | Health Check | N/A | `200 OK` |
| `GET` | `/tasks` | List Tasks | `SELECT id, title, done FROM tasks` | `200 OK` |
| `GET` | `/tasks/{id}` | Get Task by ID | `SELECT * FROM tasks WHERE id = %s` | `200 OK`, `404` |
| `POST` | `/tasks` | Create Task | `INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *` | `201`, `400` |
| `PUT` | `/tasks/{id}` | Update Task | `UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *` | `200`, `400`, `404` |
| `DELETE` | `/tasks/{id}` | Delete Task | `DELETE FROM tasks WHERE id = %s` | `204`, `404` |
| `GET` | `/stats` | Task Statistics | `SELECT COUNT(*), SUM(...) FROM tasks` | `200 OK` |
| `POST` | `/reset` | Reset Seed Data | `TRUNCATE tasks RESTART IDENTITY` + re-seed | `200 OK` |

---

## 🧪 Sample `curl -i` Outputs

### 1. List Tasks (`GET /tasks`)
```http
HTTP/1.1 200 OK
date: Fri, 07 Aug 2026 06:00:00 GMT
server: uvicorn
content-length: 163
content-type: application/json

[
  {"id":1,"title":"Buy groceries","done":false},
  {"id":2,"title":"Read FastAPI documentation","done":true},
  {"id":3,"title":"Build CRUD API assignment","done":false}
]
```

### 2. Create Task (`POST /tasks`)
```http
HTTP/1.1 201 Created
date: Fri, 07 Aug 2026 06:00:00 GMT
server: uvicorn
content-length: 52
content-type: application/json

{"id":4,"title":"Docker compose task","done":false}
```

---

## 🔍 Database Inspection inside Container (`psql`)

Inspect database tables and rows directly inside the PostgreSQL container:

```bash
docker exec -it be-04-db-1 psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```

*Output:*
```text
 id |           title            | done 
----+----------------------------+------
  1 | Buy groceries              | f
  2 | Read FastAPI documentation | t
  3 | Build CRUD API assignment  | f
  4 | Docker compose task        | f
(4 rows)
```

---

## 🤖 Stage 6: AI vs Me (AI Rematch)

As part of the Stage 6 bonus challenge, we benchmarked hand-built code against an AI-generated containerized solution in [`BE-04/ai-version/`](ai-version/).

Key findings:
- **What AI did well:** Quick generation of `Dockerfile` and `compose.yaml` boilerplate.
- **Where AI failed:** Hardcoded `localhost` inside default connection strings instead of service name `db`, causing connection refused errors inside container networks; omitted `pg_isready` healthcheck causing startup race conditions; and defaulted to status `422` for empty payloads.
- **Rematch takeaway:** Adding explicit Compose service name routing and PostgreSQL `pg_isready` healthchecks enabled reliable single-command stack startup.

See full analysis in [BE-04/ai-version/README.md](ai-version/README.md).

---

## 🧪 Running Automated Tests

Run the test suite powered by `pytest` and `httpx`:

```bash
BE-04/.venv/bin/pytest BE-04/test_main.py -v
```
