import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app
from auth_service import get_supabase_client

client = TestClient(app)

def test_swagger_ui_endpoint():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower() or "html" in response.text.lower()

def test_openapi_security_schemes():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    assert "components" in openapi
    assert "securitySchemes" in openapi["components"]
    assert "HTTPBearer" in openapi["components"]["securitySchemes"]
    assert openapi["components"]["securitySchemes"]["HTTPBearer"]["type"] == "http"
    assert openapi["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"

def test_supabase_client_initialized():
    sb = get_supabase_client()
    assert sb is not None
    assert hasattr(sb, "auth")

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["auth_provider"] == "Supabase Auth"

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "supabase": "connected"}

def test_public_info_endpoint():
    response = client.get("/public/info")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome stranger! This info is public."}

def test_signup_success():
    response = client.post("/auth/signup", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 201
    user = response.json()
    assert user["email"] == "test@example.com"
    assert "id" in user

def test_signup_validation_missing_fields():
    response = client.post("/auth/signup", json={"email": "test@example.com"})
    assert response.status_code == 400
    assert response.json() == {"error": "Email and password are required"}

def test_login_success():
    client.post("/auth/signup", json={"email": "loginuser@example.com", "password": "securepassword"})
    response = client.post("/auth/login", json={"email": "loginuser@example.com", "password": "securepassword"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login_invalid_credentials():
    response = client.post("/auth/login", json={"email": "unknown@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json() == {"error": "Invalid login credentials"}

def test_protected_profile_missing_token():
    response = client.get("/protected/profile")
    assert response.status_code == 401
    assert response.json() == {"error": "Access token required"}

def test_protected_profile_valid_token():
    client.post("/auth/signup", json={"email": "profileuser@example.com", "password": "password123"})
    login_resp = client.post("/auth/login", json={"email": "profileuser@example.com", "password": "password123"})
    token = login_resp.json()["access_token"]

    response = client.get("/protected/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profileuser@example.com"
    assert "id" in data

def test_protected_profile_tampered_token():
    client.post("/auth/signup", json={"email": "profileuser2@example.com", "password": "password123"})
    login_resp = client.post("/auth/login", json={"email": "profileuser2@example.com", "password": "password123"})
    token = login_resp.json()["access_token"] + "_tampered"

    response = client.get("/protected/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json() == {"error": "Invalid or expired token"}

def test_reusable_auth_guard_dashboard():
    client.post("/auth/signup", json={"email": "dashuser@example.com", "password": "password123"})
    login_resp = client.post("/auth/login", json={"email": "dashuser@example.com", "password": "password123"})
    token = login_resp.json()["access_token"]

    resp_valid = client.get("/protected/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert resp_valid.status_code == 200
    assert "dashuser@example.com" in resp_valid.json()["message"]

    resp_invalid = client.get("/protected/dashboard", headers={"Authorization": "Bearer invalid_token"})
    assert resp_invalid.status_code == 401

def test_logout_endpoint():
    client.post("/auth/signup", json={"email": "logoutuser@example.com", "password": "password123"})
    login_resp = client.post("/auth/login", json={"email": "logoutuser@example.com", "password": "password123"})
    token = login_resp.json()["access_token"]

    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204
    assert response.content == b""
