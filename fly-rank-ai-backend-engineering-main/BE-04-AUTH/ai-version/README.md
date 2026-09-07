# Stage 7: The AI Rematch (AI vs Me Comparison for Auth & JWT Protection)

This directory contains the Stage 7 Bonus AI Rematch exercise for Assignment A4 (BE-04-AUTH).

---

## 🤖 1. Initial Prompt (`prompt.txt`)

```text
Build a secure Authentication and Protected Routes REST API in Python 3.10+ using FastAPI and Supabase Auth.

Requirements:
1. Provider: Use Supabase Auth for managing user accounts and signing/verifying JWTs. Load SUPABASE_URL and SUPABASE_KEY from .env.
2. Endpoints:
   - POST /auth/signup: Accepts {email, password}, validates missing fields -> 400, returns 201 Created + user object.
   - POST /auth/login: Accepts {email, password}, validates fields -> 400, invalid credentials -> 401, returns 200 OK + access_token and refresh_token.
   - POST /auth/logout: Protected route requiring Bearer token, revokes session, returns 204 No Content.
   - GET /protected/profile: Protected route requiring Bearer token, verifies token via Supabase, returns 200 + user profile. Missing/invalid token -> 401.
   - GET /public/info: Public open route, returns 200 OK {"message": "..."}.
3. Reusable Guard: Implement a FastAPI dependency for extracting and verifying the Bearer token.
4. OpenAPI: Configure HTTPBearer in FastAPI so Swagger UI at /docs displays the Authorize padlock.
```

---

## 🔍 2. AI vs Me Analysis

### Question 1: How did it handle token extraction?
- **Raw Header Parsing Fragility**: The AI used raw string splitting on `Header(None)` (`authorization.split()`). If the header was missing a space or used unexpected casing, it threw uncaught `IndexError` exceptions (status `500 Server Error`) instead of returning `401 Unauthorized`.
- **Missing FastAPI `HTTPBearer`**: It parsed the `Authorization` header manually instead of using FastAPI's built-in `HTTPBearer` security scheme, causing Swagger UI at `/docs` to miss the "Authorize" padlock button.

### Question 2: What security flaws might it have introduced?
- **Uncaught Supabase Exceptions -> 500 Leak**: When an invalid or expired token was passed to `supabase.auth.get_user(token)`, the AI code did not wrap the SDK call in `try...except`. This resulted in uncaught 500 internal server error tracebacks being leaked to the client instead of a clean `401 Unauthorized` JSON response (`{"error": "Invalid or expired token"}`).
- **Hardcoded Fallback Secret Strings**: The AI provided dummy fallback secret keys inside `os.getenv()`, which could accidentally expose dummy keys in production if `.env` fails to load.

### Question 3: What did your prompt forget to specify — and what did the AI silently decide for you?
- **Forgot to specify OpenAPI security scheme explicitly**: The prompt mentioned "Swagger bearer setup", but didn't specify using `HTTPBearer(auto_error=False)`. The AI silently chose manual `Header()` parsing.
- **Forgot to specify custom exception formatting**: The prompt didn't specify JSON error key format `{"error": "..."}`, so the AI used default FastAPI `{"detail": "..."}`.

---

## 🔄 3. The Rematch & What Changed

### Improved Prompt (`improved_prompt.txt`)
Explicitly specified:
1. Using FastAPI `HTTPBearer(auto_error=False)` security scheme for Swagger UI padlock rendering.
2. Wrapping `supabase.auth.get_user(token)` in `try...except` block returning `401 Unauthorized` (`{"error": "Invalid or expired token"}`).
3. Custom exception handlers formatting all error responses as `{"error": "..."}`.

### One-Sentence Rematch Summary:
> *Explicitly specifying FastAPI `HTTPBearer` security scheme and wrapping Supabase SDK token verification in a try-except block eliminated uncaught 500 server leaks on bad tokens and enabled full Swagger UI Bearer padlock integration.*
