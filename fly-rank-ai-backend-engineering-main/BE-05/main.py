import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from scraper import PoliteScraperPipeline

def main():
    parser = argparse.ArgumentParser(
        description="FlyRank Polite Web Scraper — RAG Corpus Collector"
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="Seed URL to start crawling (e.g. https://news.ycombinator.com)"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Maximum number of pages to scrape (default: 5)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Rate limit crawl delay in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--jsonl",
        type=str,
        default="corpus.jsonl",
        help="Output JSONL file path (default: corpus.jsonl)"
    )
    parser.add_argument(
        "--db",
        type=str,
        default="corpus.db",
        help="Output SQLite database path (default: corpus.db)"
    )

    args = parser.parse_args()

    print("==================================================")
    print("🤖 FlyRank Polite Web Scraper")
    print(f"Target Seed URL: {args.url}")
    print(f"Max Pages:      {args.max_pages}")
    print(f"Base Delay:     {args.delay}s")
    print(f"JSONL Output:   {args.jsonl}")
    print(f"SQLite Output:  {args.db}")
    print("==================================================")

    pipeline = PoliteScraperPipeline(
        default_delay=args.delay,
        jsonl_path=args.jsonl,
        sqlite_path=args.db
    )

    records = pipeline.run(seed_url=args.url, max_pages=args.max_pages)

    print("\n✅ Scraping Pipeline Complete!")
    print(f"Total Structured Records Extracted: {len(records)}")
    if records:
        print(f"Sample Record Title: {records[0].title}")
        print(f"Sample Record Words: {records[0].word_count}")

if __name__ == "__main__":
    main()
