# FlyRank AI Internship — BE-05: The Polite Scraper (Week 5)

A production-grade, polite web scraping and data-gathering pipeline (`fetch` -> `parse` -> `extract` -> `clean` -> `structure`) built using **Python 3.10+**, **httpx**, **BeautifulSoup4 / lxml**, and **Pydantic**.

This workshop pipeline collects clean main text and structured metadata from web pages, respecting website rules (`robots.txt`, custom `User-Agent`, rate limits), and outputs line-delimited JSON (`corpus.jsonl`) and SQLite database (`corpus.db`) records optimized as the corpus for Week 6 RAG vector embeddings.

---

## 🚀 Quick Start (CLI Runner)

1. Activate virtual environment:
   ```bash
   source BE-05/.venv/bin/activate
   ```

2. Run the scraper CLI against any seed URL:
   ```bash
   python BE-05/main.py --url "https://news.ycombinator.com" --max-pages 5 --delay 1.0
   ```

---

## 🛡️ Politeness & Compliance Guarantees

1. **Custom `User-Agent` Identification**:
   - Headers explicitly identify the scraper bot:
     `User-Agent: FlyRankPoliteBot/1.0 (+https://github.com/0-second-shadow-0/fly-rank-ai-backend-engineering)`

2. **`robots.txt` Compliance (`robots_checker.py`)**:
   - Automatically fetches and parses `http(s)://domain/robots.txt` prior to scraping.
   - Evaluates `Disallow:` directives before requesting any URL path.
   - Respects `Crawl-delay:` directive if specified by the site owner.

3. **Per-Domain Rate Limiting (`polite_client.py`)**:
   - Enforces a minimum configurable delay (default: 1.0 second) between consecutive requests to the same host.

4. **Exponential Backoff Retries**:
   - Handles transient errors (`429 Too Many Requests`, `5xx Server Errors`) with exponential backoff delays.

---

## 🧼 Boilerplate Removal & Content Extraction (`cleaner_extractor.py`)

- **Element Decomposition**: Automatically strips non-content HTML noise:
  `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, `<aside>`, `<form>`, `<iframe>`, `<svg>`, `<noscript>`.
- **Targeted Containers**: Priority parsing for `<article>`, `<main>`, `#content`, `.post-body`, and `.entry-content`.
- **Extracted Fields**:
  - `id`: MD5 hash of canonical URL
  - `url`: Full webpage URL
  - `title`: Extracted from `<title>`, `<h1>`, or `<meta property="og:title">`
  - `author`: Extracted from `<meta name="author">` or domain
  - `published_date`: Extracted ISO 8601 timestamp
  - `content`: Clean plain-text main body paragraphs
  - `summary`: First 40 words preview
  - `tags`: Extracted meta keywords & category tags
  - `word_count`: Total word count
  - `scraped_at`: UTC timestamp string

---

## 📊 RAG Corpus Output Schema (`models.py` & `storage.py`)

Scraped data is saved concurrently to `corpus.jsonl` (line-delimited JSON) and SQLite `corpus.db`:

### `corpus.jsonl` Sample Line:
```json
{
  "id": "7fa183b092ac192f",
  "url": "https://example.com/polite-scraping",
  "title": "Polite Web Scraping Article",
  "author": "Jane Doe",
  "published_date": "2026-08-07T11:00:00Z",
  "content": "Web scraping is a foundational skill for building retrieval-augmented generation RAG AI pipelines...",
  "summary": "Web scraping is a foundational skill for building retrieval-augmented generation RAG AI pipelines...",
  "tags": ["python", "scraping", "rag", "ai"],
  "word_count": 320,
  "scraped_at": "2026-08-07T11:35:00.000000Z"
}
```

---

## ⚙️ CLI Options Reference (`main.py`)

| Argument | Default | Description |
|----------|---------|-------------|
| `--url` | *Required* | Seed URL to start crawling |
| `--max-pages` | `5` | Maximum number of pages to scrape |
| `--delay` | `1.0` | Base crawl delay in seconds |
| `--jsonl` | `corpus.jsonl` | Output JSONL file path |
| `--db` | `corpus.db` | Output SQLite database file path |

---

## 🤖 Stage 7: AI vs Me (AI Rematch)

As part of the Stage 7 bonus challenge, we benchmarked hand-built scraper code against an AI-generated solution in [`BE-05/ai-version/`](ai-version/).

Key findings:
- **What AI did well:** Quick generation of basic `httpx` and `BeautifulSoup` parsing logic.
- **Where AI failed:** Naive string matching for `robots.txt` instead of path parsing with `urllib.robotparser`, generic browser User-Agent header, and calling whole-body `get_text()` leaving nav/footer boilerplate noise in the output.
- **Rematch takeaway:** Specifying `urllib.robotparser` and targeted container decomposition (`<article>`, `<main>`) ensured clean main text extraction and 100% compliance.

See full analysis in [BE-05/ai-version/README.md](ai-version/README.md).

---

## 🧪 Running Automated Tests

Run the test suite powered by `pytest`:

```bash
BE-05/.venv/bin/pytest BE-05/test_scraper.py -v
```
