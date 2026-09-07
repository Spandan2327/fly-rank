import os
from fastapi import FastAPI, HTTPException, Depends, Header, status
from pydantic import BaseModel
from supabase import create_client

app = FastAPI(title="Auth API", version="4.0")

# AI Flaw 1: Hardcoded credentials fallback in code
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xyz.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy_anon_key")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class AuthCreds(BaseModel):
    email: str
    password: str

# AI Flaw 2: Token extraction relies on raw string split without handling missing "Bearer " prefix safely
def verify_bearer_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Simple split that crashes if header doesn't contain space
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = parts[1]
    
    # AI Flaw 3: Does not handle Supabase auth client exceptions cleanly, returning 500 internal server error on bad tokens
    user = supabase.auth.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@app.get("/")
def get_root():
    return {"name": "Auth API", "provider": "Supabase"}

@app.get("/public/info")
def get_public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.post("/auth/signup", status_code=201)
def signup(creds: AuthCreds):
    if not creds.email or not creds.password:
        raise HTTPException(status_code=400, detail="Missing fields")
    res = supabase.auth.sign_up({"email": creds.email, "password": creds.password})
    return res.user

@app.post("/auth/login")
def login(creds: AuthCreds):
    res = supabase.auth.sign_in_with_password({"email": creds.email, "password": creds.password})
    if not res.session:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    return {"access_token": res.session.access_token, "refresh_token": res.session.refresh_token}

@app.post("/auth/logout", status_code=204)
def logout(user = Depends(verify_bearer_token)):
    supabase.auth.sign_out()
    return None

@app.get("/protected/profile")
def get_profile(user = Depends(verify_bearer_token)):
    return user
