import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Directory Paths
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
CSV_OUTPUT_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_REPORT_PATH = OUTPUT_DIR / "summary_report.json"
LOG_FILE_PATH = LOG_DIR / "pipeline.log"

# Network Configurations
DEFAULT_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.0  # exponential backoff multiplier
REQUEST_DELAY = 0.5   # delay between page requests in seconds

# User Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Target URLs
BOOKS_BASE_URL = "https://books.toscrape.com/"
QUOTES_BASE_URL = "https://quotes.toscrape.com/"

# Word-to-number mapping for ratings in Books to Scrape
RATING_MAP = {
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
    "five": 5.0
}