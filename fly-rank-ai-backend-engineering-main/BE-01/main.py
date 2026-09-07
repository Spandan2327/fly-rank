from fastapi import FastAPI, HTTPException, status, Request, Response, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional

app = FastAPI(
    title="Task API",
    description="A simple To-Do List CRUD API for FlyRank AI Internship Backend Track",
    version="1.0"
)

class Task(BaseModel):
    id: int
    title: str
    done: bool = False

class TaskCreate(BaseModel):
    title: str
    done: bool = False

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Task title is required and cannot be empty")
        return v.strip()

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Task title cannot be empty")
        return v.strip() if v else v

INITIAL_TASKS = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read FastAPI documentation", "done": True},
    {"id": 3, "title": "Build CRUD API assignment", "done": False},
]

tasks_db: List[dict] = [task.copy() for task in INITIAL_TASKS]

def get_next_id() -> int:
    if not tasks_db:
        return 1
    return max(task["id"] for task in tasks_db) + 1

@app.get("/", summary="Root API Info")
def get_root():
    """Return basic information about the API and available endpoints."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/stats", "/health", "/docs"]
    }

@app.get("/health", summary="Health Check")
def get_health():
    """Health check endpoint returning server status."""
    return {"status": "ok"}

@app.get("/tasks", response_model=List[Task], summary="List & Filter Tasks")
def get_all_tasks(
    done: Optional[bool] = Query(None, description="Filter tasks by completion status"),
    search: Optional[str] = Query(None, description="Search tasks by title (case-insensitive)"),
    limit: Optional[int] = Query(None, ge=1, description="Limit the number of returned tasks (pagination)"),
    offset: Optional[int] = Query(0, ge=0, description="Offset starting point (pagination)")
):
    """List all tasks with optional filtering, search, and pagination."""
    results = tasks_db

    if done is not None:
        results = [t for t in results if t["done"] == done]

    if search:
        search_lower = search.lower()
        results = [t for t in results if search_lower in t["title"].lower()]

    if limit is not None:
        results = results[offset : offset + limit]
    elif offset > 0:
        results = results[offset:]

    return results

@app.get("/tasks/{task_id}", response_model=Task, summary="Get Task by ID")
def get_single_task(task_id: int):
    """Retrieve a single task by its unique ID."""
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, summary="Create Task")
def create_task(task_in: TaskCreate):
    """Create a new task with a title and optional initial completion status."""
    new_task = {
        "id": get_next_id(),
        "title": task_in.title,
        "done": task_in.done
    }
    tasks_db.append(new_task)
    return new_task

@app.put("/tasks/{task_id}", response_model=Task, summary="Update Task")
def update_task(task_id: int, task_update: TaskUpdate):
    """Update an existing task's title and/or done status by ID."""
    target_task = None
    for task in tasks_db:
        if task["id"] == task_id:
            target_task = task
            break

    if not target_task:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    if task_update.title is None and task_update.done is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field (title or done) must be provided for update"
        )

    if task_update.title is not None:
        target_task["title"] = task_update.title
    if task_update.done is not None:
        target_task["done"] = task_update.done

    return target_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task")
def delete_task(task_id: int):
    """Delete a task by its unique ID."""
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:
            tasks_db.pop(i)
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )

@app.get("/stats", summary="Task Statistics")
def get_stats():
    """Return task counts: total, done, and open."""
    total = len(tasks_db)
    done_count = sum(1 for t in tasks_db if t["done"])
    open_count = total - done_count
    return {
        "total": total,
        "done": done_count,
        "open": open_count
    }

@app.post("/reset", summary="Reset Seed Data")
def reset_seed():
    """Reset the task database back to the initial 3 example tasks."""
    global tasks_db
    tasks_db.clear()
    tasks_db.extend([task.copy() for task in INITIAL_TASKS])
    return {"message": "Database reset to initial seed data", "count": len(tasks_db)}

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = "Invalid request payload"
    if errors:
        first_err = errors[0]
        if first_err.get("type") == "value_error":
            msg = first_err.get("msg", msg).replace("Value error, ", "")
        else:
            loc = first_err.get("loc", [])
            field_name = loc[-1] if loc else "field"
            msg = f"Task {field_name} is required and cannot be empty"
    return JSONResponse(
        status_code=400,
        content={"error": msg}
    )
