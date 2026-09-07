# FlyRank AI Internship — Assignment A4: Auth · Login & Protect

A secure, production-grade Authentication API built using **Python 3.10+**, **FastAPI**, and **Supabase Auth SDK**, featuring user registration, JWT login authentication, token verification via reusable FastAPI dependencies, session logout, and interactive Swagger UI bearer authorization.

---

## 🚀 Quick Start (One Documented Command)

1. Copy the template environment file and add your Supabase project credentials:
   ```bash
   cp BE-04-AUTH/.env.example BE-04-AUTH/.env
   ```

2. Run the authentication server with a single command from the project root:
   ```bash
   source BE-04-AUTH/.venv/bin/activate && uvicorn BE-04-AUTH.main:app --reload --port 8000
   ```

Once running, access:
- **API Base URL:** `http://localhost:8000`
- **Interactive Swagger UI Docs:** `http://localhost:8000/docs`

---

## 🔐 Environment Variables (`.env`)

Secrets are managed via environment variables. `BE-04-AUTH/.env` is git-ignored to prevent credential leaks, while `BE-04-AUTH/.env.example` is committed:

### `BE-04-AUTH/.env.example`
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key
PORT=8000
```

---

## 📋 Endpoints Reference Table

| HTTP Method | Endpoint | Description | Auth Required? | Header Format | Status Codes |
|-------------|----------|-------------|----------------|---------------|--------------|
| `GET` | `/` | API Root Info | ❌ Public | None | `200 OK` |
| `GET` | `/health` | Health Check | ❌ Public | None | `200 OK` |
| `GET` | `/public/info` | Public Info | ❌ Public | None | `200 OK` |
| `POST` | `/auth/signup` | User Sign Up | ❌ Public | None | `201 Created`, `400 Bad Request` |
| `POST` | `/auth/login` | User Login (JWT) | ❌ Public | None | `200 OK`, `400 Bad Request`, `401 Unauthorized` |
| `POST` | `/auth/logout` | User Logout | ✅ Protected | `Authorization: Bearer <token>` | `204 No Content`, `401 Unauthorized` |
| `GET` | `/protected/profile` | Read User Profile | ✅ Protected | `Authorization: Bearer <token>` | `200 OK`, `401 Unauthorized` |
| `GET` | `/protected/dashboard` | Read Dashboard | ✅ Protected | `Authorization: Bearer <token>` | `200 OK`, `401 Unauthorized` |

---

## 🧪 Sample `curl -i` Outputs

### 1. User Sign Up (`POST /auth/signup`)
```http
HTTP/1.1 201 Created
date: Fri, 07 Aug 2026 11:10:00 GMT
server: uvicorn
content-length: 98
content-type: application/json

{"id":"0920d39e-4a6c-48c0-a433-87a31a9807fa","email":"test@example.com","created_at":"2026-08-07T11:00:00Z"}
```

### 2. User Login (`POST /auth/login`)
```http
HTTP/1.1 200 OK
date: Fri, 07 Aug 2026 11:10:00 GMT
server: uvicorn
content-length: 245
content-type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "mock_refresh_token_123",
  "token_type": "bearer"
}
```

### 3. Read Protected Profile (`GET /protected/profile` with Bearer Token)
```http
HTTP/1.1 200 OK
date: Fri, 07 Aug 2026 11:10:00 GMT
server: uvicorn
content-length: 104
content-type: application/json

{
  "id": "0920d39e-4a6c-48c0-a433-87a31a9807fa",
  "email": "test@example.com",
  "created_at": "2026-08-07T11:00:00Z"
}
```

### 4. Unauthenticated Access (`GET /protected/profile` without Token)
```http
HTTP/1.1 401 Unauthorized
date: Fri, 07 Aug 2026 11:10:00 GMT
server: uvicorn
content-length: 34
content-type: application/json

{"error":"Access token required"}
```

### 5. Tampered / Expired Token (`GET /protected/profile` with Invalid Token)
```http
HTTP/1.1 401 Unauthorized
date: Fri, 07 Aug 2026 11:10:00 GMT
server: uvicorn
content-length: 37
content-type: application/json

{"error":"Invalid or expired token"}
```

---

## 🛠️ Interactive Swagger UI Bearer Authorization

FastAPI automatically displays an **Authorize** padlock button at `http://localhost:8000/docs`:
1. Click **Authorize** at the top right of the Swagger UI page.
2. Paste your `access_token` returned from `/auth/login`.
3. Protected routes (`/protected/profile`, `/protected/dashboard`, `/auth/logout`) will display lock icons and automatically attach the `Authorization: Bearer <token>` header to all requests.

---

## 🤖 Stage 7: AI vs Me (AI Rematch)

As part of the Stage 7 bonus challenge, we benchmarked hand-built auth code against an AI-generated solution in [`BE-04-AUTH/ai-version/`](ai-version/).

Key findings:
- **What AI did well:** Quick generation of basic FastAPI signup/login endpoints.
- **Where AI failed:** Manual string splitting on `Header()` without `HTTPBearer` (missing Swagger padlock), and uncaught Supabase SDK exceptions causing 500 server error leaks on bad tokens instead of clean `401 Unauthorized`.
- **Rematch takeaway:** Specifying FastAPI `HTTPBearer` security scheme and catching Supabase Auth exceptions enabled 100% test pass rate and clean Swagger UI integration.

See full analysis in [BE-04-AUTH/ai-version/README.md](ai-version/README.md).

---

## 🧪 Running Automated Tests

Run the test suite powered by `pytest` and `httpx`:

```bash
BE-04-AUTH/.venv/bin/pytest BE-04-AUTH/test_main.py -v
```
