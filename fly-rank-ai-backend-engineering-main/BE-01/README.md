# FlyRank AI Internship — BE-01: Build Your First CRUD API

A clean, production-grade In-Memory To-Do List CRUD API built using **Python 3.10+** and **FastAPI**, featuring automatic Swagger UI documentation, input validation, custom error formatting, and comprehensive test coverage.

---

## 🚀 Quick Start (One Documented Command)

Run the API server with a single command from the project root:

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r BE-01/requirements.txt && uvicorn BE-01.main:app --reload --port 8000
```

Once running, access:
- **API Base URL:** `http://localhost:8000`
- **Interactive Swagger UI Docs:** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`

---

## 📋 Endpoints Summary

| HTTP Method | Endpoint | Description | Status Codes |
|-------------|----------|-------------|--------------|
| `GET` | `/` | API Root Metadata | `200 OK` |
| `GET` | `/health` | Health Check | `200 OK` |
| `GET` | `/tasks` | List Tasks (Supports `done`, `search`, `limit`, `offset`) | `200 OK` |
| `GET` | `/tasks/{id}` | Get Single Task by ID | `200 OK`, `404 Not Found` |
| `POST` | `/tasks` | Create New Task | `201 Created`, `400 Bad Request` |
| `PUT` | `/tasks/{id}` | Update Task Title / Done status | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/tasks/{id}` | Delete Task by ID | `204 No Content`, `404 Not Found` |
| `GET` | `/stats` | Task Aggregate Counts (Total, Open, Done) | `200 OK` |
| `POST` | `/reset` | Reset Task Store to Seed Data | `200 OK` |

---

## 🧪 Sample `curl -i` Outputs

### 1. Root Endpoint (`GET /`)
```http
HTTP/1.1 200 OK
date: Fri, 07 Aug 2026 10:30:00 GMT
server: uvicorn
content-length: 73
content-type: application/json

{"name":"Task API","version":"1.0","endpoints":["/tasks","/stats","/health","/docs"]}
```

### 2. List Tasks (`GET /tasks`)
```http
HTTP/1.1 200 OK
date: Fri, 07 Aug 2026 10:30:00 GMT
server: uvicorn
content-length: 198
content-type: application/json

[
  {"id":1,"title":"Buy groceries","done":false},
  {"id":2,"title":"Read FastAPI documentation","done":true},
  {"id":3,"title":"Build CRUD API assignment","done":false}
]
```

### 3. Get Single Task - 404 Error (`GET /tasks/99`)
```http
HTTP/1.1 404 Not Found
date: Fri, 07 Aug 2026 10:30:00 GMT
server: uvicorn
content-length: 30
content-type: application/json

{"error":"Task 99 not found"}
```

### 4. Create Task (`POST /tasks`)
```http
HTTP/1.1 201 Created
date: Fri, 07 Aug 2026 10:30:00 GMT
server: uvicorn
content-length: 44
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

### 5. Create Task Validation Error (`POST /tasks` with `{}`)
```http
HTTP/1.1 400 Bad Request
date: Fri, 07 Aug 2026 10:30:00 GMT
server: uvicorn
content-length: 53
content-type: application/json

{"error":"Task title is required and cannot be empty"}
```

### 6. Delete Task (`DELETE /tasks/1`)
```http
HTTP/1.1 204 No Content
date: Fri, 07 Aug 2026 10:30:00 GMT
server: uvicorn
```

---

## 🛠️ Interactive Swagger UI

FastAPI automatically generates interactive OpenAPI documentation powered by Swagger UI.
Visit `http://localhost:8000/docs` in any web browser to:
- Inspect request/response schemas for all endpoints.
- Click **"Try it out"** to execute live `GET`, `POST`, `PUT`, and `DELETE` requests directly from the UI.
- Verify status codes (`200`, `201`, `204`, `400`, `404`) in real time.

---

## 💀 The Mortality Experiment

> **Observation:** When tasks are created, updated, or deleted during runtime, all modifications persist only in the Python server's memory (`tasks_db`). If the server process is restarted or stopped, all newly created tasks vanish, and the list resets to the initial 3 seed tasks.

**Why this happens:** Backend applications without a persistent storage layer (such as PostgreSQL, MySQL, or SQLite) hold state strictly in RAM within process variables. RAM is volatile memory; restarting the application clears process memory. This observation demonstrates why real-world backend architectures require databases to preserve state across server restarts and deployments.

---

## 🤖 Stage 7: AI vs Me (AI Rematch)

As part of the bonus Stage 7 challenge, we benchmarked hand-built code against an AI-generated solution kept in a quarantine folder (`BE-01/ai-version/`).

Key findings:
- **What AI did well:** Fast generation of basic route definitions and auto-increment logic.
- **Where AI failed:** Defaulted to HTTP status `422` instead of requested `400 Bad Request` for empty payloads, and used `detail` key instead of custom `error` key.
- **Rematch takeaway:** Adding explicit instructions about Pydantic error interceptors enabled 100% test pass rate on the first try.

See full analysis in [BE-01/ai-version/README.md](ai-version/README.md).

---

## 🧪 Running Automated Tests

Run the test suite powered by `pytest` and `httpx`:

```bash
source .venv/bin/activate && pytest BE-01/test_main.py -v
```
