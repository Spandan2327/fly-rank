# Stage 7: The AI Rematch (AI vs Me Comparison)

This directory contains the Stage 7 Bonus AI Rematch exercise for Assignment BE-01.

---

## 🤖 1. Initial Prompt (`prompt.txt`)

```text
Build a To-Do List CRUD REST API in Python using FastAPI with in-memory storage.

Requirements:
1. Framework: FastAPI with Uvicorn server running on port 8000.
2. In-memory data: Pre-fill with 3 tasks (id: int, title: str, done: bool).
3. Endpoints:
   - GET /: Returns JSON { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }
   - GET /health: Returns JSON { "status": "ok" }
   - GET /tasks: Returns all tasks
   - GET /tasks/{id}: Returns single task or 404 error { "error": "Task {id} not found" }
   - POST /tasks: Accepts { "title": "..." }, generates next ID, sets done to false, returns 201 Created + new task. If title is missing or empty string, return 400 Bad Request { "error": "..." }
   - PUT /tasks/{id}: Updates title and/or done status. Returns updated task. Unknown id -> 404, empty title/body -> 400.
   - DELETE /tasks/{id}: Deletes task, returns 204 No Content with empty body. Unknown id -> 404.
4. Documentation: Built-in Swagger UI accessible at /docs.
```

---

## 🔍 2. AI vs Me Analysis

### Question 1: What did the AI do better?
- **Conciseness in basic endpoints**: The AI wrote fewer lines of boilerplate code for basic route definitions and auto-increment logic (`max([t['id'] for t in tasks_db], default=0) + 1`).
- **Default string stripping**: The AI immediately added `.strip()` directly inside the route handlers without needing complex custom validator decorators.

### Question 2: What did it get wrong or quietly ignore from your prompt?
- **Default FastAPI 422 vs required 400 status code**: When sending an empty JSON body `{}` to `POST /tasks`, FastAPI defaulted to status `422 Unprocessable Entity` because the `title` field was missing from Pydantic schema validation. The AI failed to implement a custom `RequestValidationError` handler, causing 2 checkpoint test failures.
- **Default `detail` key instead of required `error` key**: `HTTPException(status_code=404, detail="...")` outputs `{"detail": "..."}` instead of the requested spec `{"error": "..."}`.
- **Ignored query parameters & stretch features**: The AI did not include `search`, `done` filtering, pagination (`limit`/`offset`), `GET /stats`, or `POST /reset`.

### Question 3: What did your prompt forget to specify — and what did the AI silently decide for you?
- **Forgot to specify validation error handling for missing JSON fields**: The prompt did not specify how FastAPI should handle Pydantic schema validation failures. The AI silently accepted FastAPI's default `422` status code instead of mapping schema errors to `400 Bad Request`.
- **Forgot to specify OpenAPI documentation annotations**: The prompt didn't specify summary text or field descriptions for Swagger UI, so the AI generated generic endpoint titles.

---

## 🔄 3. The Rematch & What Changed

### Improved Prompt (`improved_prompt.txt`)
Explicitly specified:
1. Intercepting `RequestValidationError` to map missing fields to `400 Bad Request` instead of default `422`.
2. Overriding FastAPI's `HTTPException` handler to output `{"error": "..."}` format instead of `{"detail": "..."}`.
3. Adding `GET /tasks` query filters (`done`, `search`, `limit`, `offset`), `GET /stats`, and `POST /reset`.

### One-Sentence Rematch Summary:
> *By explicitly specifying custom exception handlers for Pydantic schema validation and JSON error keys, the regenerated AI code passed 100% of the checkpoint tests on the first try without any status code mismatches.*
