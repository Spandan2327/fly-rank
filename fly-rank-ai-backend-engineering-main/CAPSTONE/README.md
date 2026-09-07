# FlyRank AI Internship — Capstone Project: AI Image Understanding & Content Matching Engine

A production-grade **AI Image Understanding & Content Matching Engine** built using **Python 3.10+**, **FastAPI**, **Pydantic v2**, **SQLite**, and **Vector Embeddings**.

This system analyzes an image library (~50 images across categories like red fox, wolf, dog, bear, deer), extracts validated structured metadata via Vision AI, generates semantic vector embeddings, ranks candidates using cosine similarity, and enforces a strict **Mismatch Guard** (refusing incorrect pairings with human-readable explanations).

---

## 🏗️ Architecture Overview

```text
Images ──(Batch Job)──► Vision Model ──► {subject, category, attributes, caption, confidence}
                                            │
                                            ▼
                                     embed(caption) ────────► image_vectors
                                                                   │
Posts ───────────────────────────────► embed(post text) ──────────► post_vectors
                                                                   │
                                                                   ▼
GET /posts/:id/images ───────────────────────────► Similarity Ranking (image_vectors × post_vector)
                                                                   │
                                                                   ▼
                                                   Mismatch Guard (safety layer)
                                                   ├── Accepted Match (ranked & explained)
                                                   └── Rejected / "No Confident Match" + Reason
                                                                   │
                                                                   ▼
                                                    Review API (approve / reject)
```

---

## 🚀 Quick Start (One Documented Command)

1. Activate virtual environment and copy environment variables:
   ```bash
   cp CAPSTONE/.env.example CAPSTONE/.env && source CAPSTONE/.venv/bin/activate
   ```

2. Seed database and run the server with a single command:
   ```bash
   python CAPSTONE/seed_data.py && uvicorn CAPSTONE.main:app --reload --port 8000
   ```

Once running:
- **API Base URL:** `http://localhost:8000`
- **Interactive Swagger UI Docs:** `http://localhost:8000/docs`

---

## 🛡️ The Mismatch Guard (Production Safety Layer)

The Mismatch Guard evaluates the top candidate image against three safety gates before suggesting it to a user:

1. **Gate 1: Vision Confidence Check**:
   - Classifications with vision model confidence `< 0.70` are flagged as `FLAGGED_LOW_CONFIDENCE` and rejected with `NO_CONFIDENT_MATCH`.

2. **Gate 2: Category Mismatch Check**:
   - Compares detected image category/subject against required blog post topic. E.g., Post: *"red fox"* vs Candidate: *"gray wolf"* -> **REJECTED**: *"Animal category mismatch: expected red fox, detected wolf"*.

3. **Gate 3: Similarity Cutoff Check**:
   - Rejects matches with cosine similarity score below threshold (`< 0.65`).

---

## 📋 Endpoints Reference Table

| HTTP Method | Endpoint | Description | Status Codes |
|-------------|----------|-------------|--------------|
| `GET` | `/` | API Metadata | `200 OK` |
| `GET` | `/health` | Health Check | `200 OK` |
| `POST` | `/batch/process-images` | Trigger background vision processing batch job | `200 OK` |
| `GET` | `/posts/{id}/images` | Get ranked image suggestions with Mismatch Guard check | `200 OK`, `404` |
| `POST` | `/suggestions/{id}/approve` | Human-in-the-loop approval workflow | `200 OK`, `404` |
| `POST` | `/suggestions/{id}/reject` | Human-in-the-loop rejection workflow | `200 OK`, `404` |
| `GET` | `/stats/costs` | AI tokens used & USD cost tracking summary | `200 OK` |
| `GET` | `/eval` | Run evaluation suite & return Top-1 Precision metric | `200 OK` |

---

## 📊 Evaluation & Precision Metric

Run the automated evaluation suite to calculate Top-1 precision on labeled ground truth dataset:

```bash
curl http://localhost:8000/eval
```

*Output:*
```json
{
  "eval_count": 5,
  "correct_matches": 5,
  "top_1_precision_percentage": 100.0
}
```

---

## 🧪 Running Automated Tests

Run the acceptance probe test suite:

```bash
CAPSTONE/.venv/bin/pytest CAPSTONE/test_capstone.py -v
```
