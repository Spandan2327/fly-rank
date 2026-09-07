from fastapi import FastAPI, HTTPException, Request, Response, Query, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional
from contextlib import asynccontextmanager
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from database import (
    init_db,
    get_all_tasks_db,
    get_task_by_id_db,
    create_task_db,
    update_task_db,
    delete_task_db,
    get_stats_db,
    reset_db
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Task Database API",
    description="A SQLite-backed To-Do List CRUD API for FlyRank AI Internship Backend Track",
    version="2.0",
    lifespan=lifespan
)

@app.get("/", summary="Root API Info")
def get_root():
    return {
        "name": "Task Database API",
        "version": "2.0",
        "storage": "SQLite (tasks.db)",
        "endpoints": ["/tasks", "/stats", "/health", "/docs"]
    }

@app.get("/health", summary="Health Check")
def get_health():
    return {"status": "ok"}

@app.get("/tasks", response_model=List[Task], summary="List & Filter Tasks")
def read_all_tasks(
    done: Optional[bool] = Query(None, description="Filter tasks by completion status"),
    search: Optional[str] = Query(None, description="Search tasks by title using SQL LIKE"),
    limit: Optional[int] = Query(None, ge=1, description="Pagination limit"),
    offset: Optional[int] = Query(0, ge=0, description="Pagination offset")
):
    return get_all_tasks_db(done=done, search=search, limit=limit, offset=offset)

@app.get("/tasks/{task_id}", response_model=Task, summary="Get Task by ID")
def read_single_task(task_id: int):
    task = get_task_by_id_db(task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    return task

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, summary="Create Task")
def create_new_task(task_in: TaskCreate):
    return create_task_db(title=task_in.title, done=task_in.done)

@app.put("/tasks/{task_id}", response_model=Task, summary="Update Task")
def update_existing_task(task_id: int, task_update: TaskUpdate):
    if task_update.title is None and task_update.done is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field (title or done) must be provided for update"
        )

    updated = update_task_db(task_id=task_id, title=task_update.title, done=task_update.done)
    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    return updated

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Task")
def delete_existing_task(task_id: int):
    success = delete_task_db(task_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/stats", summary="Task Statistics")
def get_stats():
    return get_stats_db()

@app.post("/reset", summary="Reset Seed Data")
def reset_seed():
    count = reset_db()
    return {"message": "Database reset to initial seed data", "count": count}

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
