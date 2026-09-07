# FlyRank AI Internship — Backend Track

Comprehensive portfolio repository for the **FlyRank Backend AI Engineering Track**, containing all weekly assignments and the Capstone Project.

---

## 📚 Repository Map & Assignment Index

| Week | Project Directory | Storage / Engine | Core Concept & Infrastructure | Status |
|------|-------------------|------------------|-------------------------------|--------|
| **Week 2** | [`BE-01/`](BE-01/) | In-Memory Dictionary | **Build Your First CRUD API**: FastAPI REST endpoints with Pydantic validation, status codes, query filtering, pagination, and stats. | **Complete** |
| **Week 3** | [`BE-02/`](BE-02/) | SQLite (`tasks.db`) | **Connecting CRUD to Database**: Migration from in-memory to SQLite file storage using parameterized SQL queries. | **Complete** |
| **Week 3** | [`BE-04/`](BE-04/) | PostgreSQL | **Containerize Your Stack**: Full multi-container stack orchestrated via Docker Compose (`compose.yaml`) with volume persistence. | **Complete** |
| **Week 4** | [`BE-04-AUTH/`](BE-04-AUTH/) | Supabase Auth & JWT | **Auth · Login & Protect**: User sign-up, JWT login authentication, reusable FastAPI auth dependency, and Swagger UI Bearer padlock. | **Complete** |
| **Week 5** | [`BE-05/`](BE-05/) | SQLite & JSONL | **The Polite Scraper**: Web scraper pipeline (`fetch` -> `parse` -> `extract` -> `clean` -> `structure`) respecting `robots.txt`, `User-Agent`, rate limits, and RAG corpus export. | **Complete** |
| **Week 8** | [`CAPSTONE/`](CAPSTONE/) | **AI Vision & Vectors** | **AI Image Understanding & Content Matching Engine**: Production AI decision system with structured Vision classification, vector similarity matching, **Mismatch Guard** safety layer (fox/wolf rejection), and Review API. | **Complete** |

---

## 📖 Project Summaries

### 🔹 Week 2: BE-01 — Build Your First CRUD API
- **Location:** [`BE-01/`](BE-01/)
- **Summary:** An in-memory To-Do List CRUD API built using Python and FastAPI. Implements REST best practices, custom exception handlers returning `{"error": "..."}`, query filtering (`done`, `search`), pagination (`limit`, `offset`), task stats, and interactive Swagger UI documentation.
- **Quick Run:** `source BE-01/.venv/bin/activate && uvicorn BE-01.main:app --reload --port 8000`

### 🔹 Week 3: BE-02 — Connecting CRUD to Database (SQLite)
- **Location:** [`BE-02/`](BE-02/)
- **Summary:** Upgraded storage engine from transient memory to a persistent SQLite database (`tasks.db`). All raw SQL queries are parameterized with `?` placeholders to protect against SQL injection vulnerabilities. Includes automatic schema creation and 3-task idempotent seeding.
- **Quick Run:** `source BE-02/.venv/bin/activate && uvicorn BE-02.main:app --reload --port 8000`

### 🔹 Week 3: BE-04 — Containerize Your Stack (PostgreSQL + Docker Compose)
- **Location:** [`BE-04/`](BE-04/)
- **Summary:** Migrated database layer from SQLite to PostgreSQL running inside a Docker container. Orchestrates `api` and `db` services in a single `compose.yaml` stack with volume persistence (`taskdata`) and `pg_isready` healthcheck.
- **Quick Run:** `cp BE-04/.env.example BE-04/.env && docker compose -f BE-04/compose.yaml up --build -d`

### 🔹 Week 4: BE-04-AUTH — Auth · Login & Protect (Supabase Auth + JWT)
- **Location:** [`BE-04-AUTH/`](BE-04-AUTH/)
- **Summary:** Production authentication server using Supabase Auth SDK and JWT token verification. Implements user sign-up (`POST /auth/signup`), JWT login (`POST /auth/login`), session logout (`POST /auth/logout`), public info, and protected profile endpoints with reusable FastAPI `HTTPBearer` security dependency.
- **Quick Run:** `cp BE-04-AUTH/.env.example BE-04-AUTH/.env && source BE-04-AUTH/.venv/bin/activate && uvicorn BE-04-AUTH.main:app --reload --port 8000`

### 🔹 Week 5: BE-05 — The Polite Scraper (RAG Corpus Pipeline)
- **Location:** [`BE-05/`](BE-05/)
- **Summary:** A polite web scraping and data-gathering pipeline (`fetch` -> `parse` -> `extract` -> `clean` -> `structure`). Features custom `User-Agent` identification, automatic `robots.txt` rule checking (`Disallow` / `Crawl-delay`), per-domain rate limiting, exponential backoff retries, HTML boilerplate removal, and dual export to `corpus.jsonl` and SQLite `corpus.db` for RAG vector embeddings.
- **Quick Run:** `source BE-05/.venv/bin/activate && python BE-05/main.py --url "https://news.ycombinator.com" --max-pages 5 --delay 1.0`

### 🔹 Week 8: CAPSTONE — AI Image Understanding & Content Matching Engine
- **Location:** [`CAPSTONE/`](CAPSTONE/)
- **Summary:** An AI decision engine that classifies an image library using Vision AI, generates semantic vector embeddings, ranks candidates using cosine similarity, and enforces a strict **Mismatch Guard** safety layer (e.g. rejecting a wolf image for a red fox post with human-readable explanations). Includes background batch processing with per-call cost tracking, Review API, submission pack (`capstone.yaml`, `EVIDENCE.md`, `BUILDLOG.md`), and **100% Top-1 Precision** evaluation metric.
- **Quick Run:** `cp CAPSTONE/.env.example CAPSTONE/.env && source CAPSTONE/.venv/bin/activate && python CAPSTONE/seed_data.py && uvicorn CAPSTONE.main:app --reload --port 8000`

---

## 🧪 Testing All Projects

Each project directory includes a complete `pytest` test suite:

```bash
# Week 2
BE-01/.venv/bin/pytest BE-01/test_main.py -v

# Week 3
BE-02/.venv/bin/pytest BE-02/test_main.py -v
BE-04/.venv/bin/pytest BE-04/test_main.py -v

# Week 4
BE-04-AUTH/.venv/bin/pytest BE-04-AUTH/test_main.py -v

# Week 5
BE-05/.venv/bin/pytest BE-05/test_scraper.py -v

# Week 8 Capstone
CAPSTONE/.venv/bin/pytest CAPSTONE/test_capstone.py -v
```

---

*FlyRank AI Internship | Backend AI Engineering Track | August 2026*
