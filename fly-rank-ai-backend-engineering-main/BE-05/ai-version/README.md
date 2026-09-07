# Stage 7: The AI Rematch (AI vs Me Comparison for Web Scraper Pipeline)

This directory contains the Stage 7 Bonus AI Rematch exercise for Assignment BE-05 (The Polite Scraper).

---

## 🤖 1. Initial Prompt (`prompt.txt`)

```text
Build a polite web scraper in Python using httpx and BeautifulSoup that extracts clean text records for a RAG corpus.

Requirements:
1. Politeness: Identify with a custom User-Agent, check robots.txt before fetching, and enforce a delay between requests.
2. Boilerplate Cleaning: Remove script tags, style tags, and nav elements from the HTML before extracting text.
3. Structured Fields: Extract title, main content text, word count, and URL.
4. Output: Save records into a JSONL file.
```

---

## 🔍 2. AI vs Me Analysis

### Question 1: How did it handle politeness (`robots.txt` & User-Agent)?
- **Fake Browser User-Agent**: The AI defaulted to a browser string (`Mozilla/5.0...`) instead of identifying as an honest bot (`FlyRankPoliteBot/1.0`).
- **Naive `robots.txt` Checking**: It performed a raw string match for `"Disallow: /"` instead of parsing specific path rules (`Disallow: /admin/`, `Disallow: /private/`) with `urllib.robotparser`.
- **No Per-Domain Delay Tracking**: Called `time.sleep(delay)` naively before every request without tracking per-domain last-request timestamps.

### Question 2: What boilerplate flaws or extraction issues did it have?
- **Left Boilerplate Noise in Content**: Only stripped `<script>` and `<style>`, leaving `<nav>`, `<footer>`, `<header>`, `<aside>`, `<form>`, and `<iframe>` elements in the extracted text.
- **Whole-Page `get_text()`**: Called `soup.get_text()` on the entire document body instead of locating the main container (`<article>`, `<main>`, `#content`), polluting the RAG corpus with navigation links and copyright footers.

### Question 3: What did your prompt forget to specify — and what did the AI silently decide for you?
- **Forgot to specify `urllib.robotparser`**: The prompt didn't specify *how* to parse `robots.txt`, so the AI wrote a 3-line string check.
- **Forgot to specify Pydantic schema validation & SQLite storage**: The AI dumped raw dictionaries into JSONL without schema validation or SQLite table persistence.

---

## 🔄 3. The Rematch & What Changed

### Improved Prompt (`improved_prompt.txt`)
Explicitly specified:
1. Identifying User-Agent string (`FlyRankPoliteBot/1.0`).
2. `urllib.robotparser.RobotFileParser` for path compliance and `Crawl-delay`.
3. Targeted container extraction (`<article>`, `<main>`, `#content`) with noise element decomposition (`nav`, `footer`, `header`, `aside`, `form`, `iframe`).
4. Pydantic `ScrapedRecord` data modeling and dual export (`corpus.jsonl` and SQLite `corpus.db`).

### One-Sentence Rematch Summary:
> *Specifying `urllib.robotparser` and targeted HTML container decomposition eliminated navigation boilerplate noise from extracted text and ensured 100% compliance with `robots.txt` path rules.*
