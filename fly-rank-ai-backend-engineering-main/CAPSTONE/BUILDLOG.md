# Capstone Build Log — AI Image Understanding & Content Matching Engine

This log tracks technical decisions, architecture choices, and AI assistance throughout the development of the Capstone project.

---

## 🛠️ Design & Architecture Decisions

1. **Structured Vision Output Schema**:
   - Schema enforcement via Pydantic (`VisionMetadata`). Every vision call must return JSON containing `subject`, `category`, `attributes`, `caption`, and `confidence` (0.0 to 1.0).
   - Low-confidence classifications (`confidence < 0.70`) are flagged automatically for human review rather than accepted silently into the vector index.

2. **Semantic Matching & Embeddings**:
   - Captions and blog post text are embedded into a normalized vector space using cosine similarity for matching.
   - Conceptual matching enables queries like *"The behavior of red foxes"* to match *"Vulpes vulpes"* or *"orange fox in forest"* captions.

3. **The Mismatch Guard (Safety Layer)**:
   - Evaluates the top candidate image before returning it to the user.
   - Enforces 3 safety gates:
     - **Category Mismatch Gate**: Compares detected animal/subject category against the blog post's required subject. E.g., Post: *"red fox"* vs Candidate: *"gray wolf"* -> **REJECTED**: *"Animal category mismatch: expected fox, detected wolf"*.
     - **Similarity Cutoff Gate**: Rejects matches with cosine similarity below threshold (`0.65`).
     - **Vision Confidence Gate**: Rejects classifications with vision model confidence `< 0.70`.

4. **Background Processing & Cost Metering**:
   - Vision and embedding jobs execute in background tasks with retry mechanisms.
   - Every model API call logs token consumption and estimates cost in USD (tracking input/output tokens).

---

## 🤖 AI Usage Log

- **Where AI helped**: Generating initial Pydantic schema validation models, cosine similarity matrix calculation helper functions, and seed dataset generation scripts.
- **Where AI was wrong / corrected**: AI initially suggested a simple top-1 vector search without tag verification, which incorrectly matched a wolf photo to a fox blog post. We built the explicit `MismatchGuard` class with category comparison and similarity cutoffs to reliably reject false positives.
