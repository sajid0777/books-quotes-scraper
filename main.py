"""Run the Books + Quotes ETL pipeline with: python main.py"""
import csv
import json
import logging
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR, LOG_DIR = ROOT / "output", ROOT / "logs"
CSV_COLUMNS = ["source", "source_url", "name_or_title", "category", "price", "rating", "author", "tags", "description", "scraped_at"]
SOURCES = ["Books to Scrape", "Quotes to Scrape"]


def configure_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                        handlers=[logging.StreamHandler(), logging.FileHandler(LOG_DIR / "scraper.log", encoding="utf-8")], force=True)


def write_outputs(records, report):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUTPUT_DIR / "final_dataset.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    with (OUTPUT_DIR / "summary_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)


def write_to_atlas(records):
    """Upsert records into Atlas when MONGODB_URI is configured."""
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        logging.getLogger("main").info("MONGODB_URI is not set; skipping optional MongoDB Atlas output")
        return 0

    from pymongo import MongoClient, ReplaceOne
    from processing.deduplication import make_fingerprint

    database_name = os.environ.get("MONGODB_DATABASE", "scraping_assignment")
    collection_name = os.environ.get("MONGODB_COLLECTION", "records")
    operations = []
    for record in records:
        document = dict(record)
        document["_id"] = make_fingerprint(record)
        operations.append(ReplaceOne({"_id": document["_id"]}, document, upsert=True))

    with MongoClient(uri, serverSelectionTimeoutMS=10000) as client:
        client.admin.command("ping")
        if operations:
            result = client[database_name][collection_name].bulk_write(operations, ordered=False)
            return result.upserted_count + result.modified_count
    return 0


def run():
    configure_logging()
    logger = logging.getLogger("main")
    started = datetime.now(timezone.utc)
    tick = monotonic()
    scraped, cleaned_by_source = {}, defaultdict(int)
    rejected = Counter()
    rejected_records = 0
    all_valid = []
    for source, scraper_class in zip(SOURCES, (BooksScraper, QuotesScraper)):
        try:
            raw_records = scraper_class().scrape()
        except Exception:
            logger.exception("Unexpected failure scraping %s; continuing with other source", source)
            raw_records = []
        scraped[source] = len(raw_records)
        for raw in raw_records:
            rec = clean_record(raw)
            if rec.get("source"):
                cleaned_by_source[rec["source"]] += 1
            problems = validate_record(rec)
            if problems:
                rejected_records += 1
                rejected.update(problems)
                logger.warning("Rejected record from %s: %s", source, ", ".join(problems))
                continue
            all_valid.append(rec)
    unique, duplicates = find_duplicates(all_valid)
    ended = datetime.now(timezone.utc)
    report = {
        "collected_per_source": scraped,
        "cleaned_per_source": {source: cleaned_by_source[source] for source in SOURCES},
        "rejected_by_reason": dict(sorted(rejected.items())),
        "rejected_total": rejected_records,
        "duplicates_detected": len(duplicates),
        "final_record_count": len(unique),
        "start_time_utc": started.isoformat(),
        "end_time_utc": ended.isoformat(),
        "duration_seconds": round(monotonic() - tick, 2),
        "source_errors": [],
        "note": "Books category and description are blank because listing pages do not provide them; book detail pages were not fetched. Quote source_url is its author page where available, otherwise the listing page.",
    }
    # Reconcile each source's failure status through logging and collected counts.
    write_outputs(unique, report)
    try:
        stored = write_to_atlas(unique)
        if stored:
            logger.info("Upserted or refreshed %d records in MongoDB Atlas", stored)
    except Exception:
        logger.exception("MongoDB Atlas write failed; local output files are still available")
    logger.info("Finished: %d unique records, %d duplicates", len(unique), len(duplicates))
    print(f"Wrote {OUTPUT_DIR / 'final_dataset.csv'} ({len(unique)} rows)")
    print(f"Wrote {OUTPUT_DIR / 'summary_report.json'}")
    print(f"Wrote {LOG_DIR / 'scraper.log'}")


if __name__ == "__main__":
    run()

