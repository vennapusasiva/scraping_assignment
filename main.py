import csv
import json
import logging
import time
from typing import List, Dict, Any

import config
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper
from processing.cleaning import clean_record
from processing.validation import validate_record
from processing.deduplication import deduplicate_records

# Initialize Pipeline Logger
logger = logging.getLogger("ScraperPipeline")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(config.LOG_FILE_PATH, encoding="utf-8")
console_handler = logging.StreamHandler()

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def main():
    start_time = time.time()
    logger.info("================ Starting Web Scraping & Data Pipeline ================")

    # Metrics Tracker
    metrics = {
        "execution_start": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "sources": {
            "Books to Scrape": {"raw": 0, "cleaned": 0, "rejected": 0, "duplicates": 0, "final": 0},
            "Quotes to Scrape": {"raw": 0, "cleaned": 0, "rejected": 0, "duplicates": 0, "final": 0}
        },
        "total_raw_collected": 0,
        "total_cleaned": 0,
        "total_rejected": 0,
        "total_duplicates_removed": 0,
        "total_final_records": 0,
        "execution_time_seconds": 0.0
    }

    # Step 1: Scrape Sources
    scrapers = [BooksScraper(), QuotesScraper()]
    raw_records: List[Dict[str, Any]] = []

    for scraper in scrapers:
        try:
            scraped = scraper.scrape()
            metrics["sources"][scraper.name]["raw"] = len(scraped)
            raw_records.extend(scraped)
        except Exception as e:
            logger.critical(f"Unhandled exception during scraping in {scraper.name}: {e}", exc_info=True)

    metrics["total_raw_collected"] = len(raw_records)
    logger.info(f"Scraping completed. Raw records collected: {metrics['total_raw_collected']}")

    # Step 2: Clean & Validate Records
    cleaned_records: List[Dict[str, Any]] = []
    
    for raw in raw_records:
        source_name = raw.get("source", "Unknown")
        cleaned = clean_record(raw)
        
        is_valid, failure_reason = validate_record(cleaned)
        if is_valid:
            cleaned_records.append(cleaned)
            if source_name in metrics["sources"]:
                metrics["sources"][source_name]["cleaned"] += 1
        else:
            logger.warning(f"Validation Failure [{source_name}]: {failure_reason} -> Record: {raw.get('name_or_title')}")
            metrics["total_rejected"] += 1
            if source_name in metrics["sources"]:
                metrics["sources"][source_name]["rejected"] += 1

    metrics["total_cleaned"] = len(cleaned_records)

    # Step 3: Deduplication
    unique_records, duplicate_count = deduplicate_records(cleaned_records)
    metrics["total_duplicates_removed"] = duplicate_count
    metrics["total_final_records"] = len(unique_records)

    # Attribute duplicates per source for the report
    for rec in unique_records:
        src = rec.get("source")
        if src in metrics["sources"]:
            metrics["sources"][src]["final"] += 1

    for src, data in metrics["sources"].items():
        data["duplicates"] = data["cleaned"] - data["final"]

    # Step 4: Export Consolidated CSV
    fieldnames = [
        "source", "source_url", "name_or_title", "category", 
        "price", "rating", "author", "tags", "description", "scraped_at"
    ]

    try:
        with open(config.CSV_OUTPUT_PATH, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_records)
        logger.info(f"Final dataset successfully written to: {config.CSV_OUTPUT_PATH}")
    except Exception as e:
        logger.error(f"Failed to export CSV output: {e}", exc_info=True)

    # Step 5: Export Summary Report JSON
    elapsed_time = round(time.time() - start_time, 2)
    metrics["execution_time_seconds"] = elapsed_time

    try:
        with open(config.SUMMARY_REPORT_PATH, mode="w", encoding="utf-8") as json_file:
            json.dump(metrics, json_file, indent=4)
        logger.info(f"Summary metrics exported to: {config.SUMMARY_REPORT_PATH}")
    except Exception as e:
        logger.error(f"Failed to export Summary JSON: {e}", exc_info=True)

    logger.info("================ Pipeline Finished Successfully ================")
    print(f"\nPipeline Finished in {elapsed_time}s.")
    print(f"Total Raw Collected: {metrics['total_raw_collected']}")
    print(f"Total Validated:     {metrics['total_cleaned']}")
    print(f"Total Duplicates:    {metrics['total_duplicates_removed']}")
    print(f"Final Consolidated:  {metrics['total_final_records']}\n")


if __name__ == "__main__":
    main()