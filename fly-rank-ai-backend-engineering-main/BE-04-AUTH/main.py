from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from auth_service import get_supabase_client, sign_up_user, sign_in_user, sign_out_user
from dependencies import get_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthCredentials(BaseModel):
    email: str
    password: str

    @field_validator("email", "password")
    @classmethod
    def must_not_be_empty(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"{info.field_name.capitalize()} is required and cannot be empty")
        return v.strip()

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_supabase_client()
    logger.info("Server running and connected to Supabase")
    yield

app = FastAPI(
    title="Auth API — Supabase & JWT",
    description="A secure Authentication & Protected Routes API built with Supabase Auth for FlyRank AI Internship Backend Track",
    version="4.0",
    lifespan=lifespan
)

@app.get("/")
def get_root():
    return {
        "name": "Auth API",
        "version": "4.0",
        "auth_provider": "Supabase Auth",
        "endpoints": ["/auth/signup", "/auth/login", "/auth/logout", "/protected/profile", "/protected/dashboard", "/public/info"]
    }

@app.get("/health")
def get_health():
    return {"status": "ok", "supabase": "connected"}

@app.get("/public/info", summary="Public Open Endpoint")
def get_public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED, summary="User Registration")
def signup(creds: AuthCredentials):
    try:
        user_info = sign_up_user(email=creds.email, password=creds.password)
        return user_info
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e) if "Email" in str(e) else "Registration failed"
        )

@app.post("/auth/login", summary="User Login")
def login(creds: AuthCredentials):
    try:
        tokens = sign_in_user(email=creds.email, password=creds.password)
        return tokens
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials"
        )

@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT, summary="User Logout")
def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    token = current_user.get("token", "")
    sign_out_user(token)
    return None

@app.get("/protected/profile", summary="Protected User Profile")
def get_protected_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "created_at": current_user.get("created_at")
    }

@app.get("/protected/dashboard", summary="Protected User Dashboard")
def get_protected_dashboard(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "message": f"Welcome to your private dashboard, {current_user['email']}!",
        "user_id": current_user["id"]
    }

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Email and password are required"}
    )
