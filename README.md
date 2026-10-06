# Multi-Source Web Scraping & Data Processing Pipeline

## 1. Assignment / Project Overview
This project is an end-to-end Python multi-source web scraping and ETL (Extract, Transform, Load) pipeline. It extracts structured records from two distinct web sources—**Books to Scrape** and **Quotes to Scrape**—and standardizes them into a unified dataset. 

The pipeline handles dynamic pagination, cleans string formats, normalizes currencies and ratings, enforces domain-specific validation rules, eliminates duplicate entries using cryptographic hashing, and outputs production-ready deliverables alongside detailed logging and execution metrics.

## #Python Version

Required Version: Python 3.8 or higher (Tested on Python 3.8.8)

## **#Installation & Setup Instructions **

**Step 1: Clone or Open Project**
Navigate to your project root directory in your terminal or VS Code: cd scraping_assignment

**Step 2: Create and Activate Virtual Environment**
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\activate

**Step 3: Install Dependencies**
pip install --upgrade pip
pip install -r requirements.txt

Dependencies defined in requirements.txt:

requests (>= 2.28.0) — HTTP library for fetching web pages.

beautifulsoup4 (>= 4.11.0) — HTML parser for DOM traversal and data extraction.

pytest (>= 7.0.0) — Test framework for unit testing cleaning, validation, and deduplication logic.


**How to Run**

*Running Unit Tests*

Execute unit tests to verify data cleaning, validation, and deduplication logic:
pytest -v

*Running the Full Pipeline*

Execute the driver script to start harvesting, processing, and exporting data:
python main.py

**How Pagination Works**

Pagination is handled dynamically without hardcoding total page counts or page ranges:

BooksScraper: Begins at index.html. After parsing items on the active page, it inspects the DOM for an HTML li.next > a element. If found, it resolves the relative URL against the base URL using urllib.parse.urljoin and recursively fetches the next page until no next button exists (mapping all 50 pages).

QuotesScraper: Starts at /page/1/. It extracts quote cards and checks for a li.next > a element at the bottom of the page. It follows relative links until the pagination navigation terminates (mapping all 10 pages).

### **Data Model**

Both scrapers normalize raw scraped fields into a unified 10-column schema:
Field Name,Type,Description,Source Mapping
source,str,Name of origin site,"""Books to Scrape"" / ""Quotes to Scrape"""
source_url,str,Canonical URL of item/author,Detail page URL / Author profile URL
name_or_title,str,Primary identifier text,Book Title / Quote Content
category,str,Broad taxonomy category,"""Books"" / ""Quotes"""
price,float,Item price (GBP),Extracted numeric float / None
rating,float,Rating on a 1.0–5.0 scale,Extracted numeric float / None
author,str,Name of author/creator,None / Quote Author
tags,str,Comma-separated tags,None / Tag array joined by commas
description,str,Additional meta/stock info,Availability string / None
scraped_at,str,Extraction UTC timestamp,ISO-8601 formatted timestamp

#### **Cleaning Approach**
Implemented in processing/cleaning.py:

Text Stripping & Normalization: Strips leading/trailing whitespace, invisible unicode characters (\xa0), and enclosing curly quotes (“ and ”).

Price Parsing: Uses regular expressions (r'[\d.]+') to strip currency symbols (£) and converts text to floating-point values (51.77).

Rating Normalization: Maps CSS rating class strings ("One", "Two", "Three", "Four", "Five") to numeric floats (1.0 through 5.0).

Tag Formatting: Normalizes quote tag arrays into clean, uniform comma-separated strings.

#### **Validation Approach**

Implemented in processing/validation.py:
Each record must pass strict business criteria prior to downstream pipeline entry:

Source Check: source must match recognized source titles.

URL Integrity: source_url must parse into a valid HTTP/HTTPS scheme and domain (netloc).

Core Field Presence: name_or_title cannot be null or empty string.

Source-Specific Rules:

Books: price must be a non-negative float (>= 0.0); rating (if present) must be between 1.0 and 5.0.

Quotes: author field cannot be empty or null.

Invalid records are rejected, logged with failure reasons, and tallied in the final summary metrics.

#### **Deduplication Approach**

*Implemented in processing/deduplication.py:*

Fingerprint Generation: Generates a deterministic SHA-256 hash key using normalized representations of key fields (source + name_or_title + author).

String Normalization: Converts strings to lowercase, removes punctuation/whitespace, and normalizes characters before hashing.

*Hash-Set Tracking:*

 Tracks processed fingerprints in an in-memory hash set. If a record yields an existing hash key, it is flagged as a duplicate, discarded, and counted in execution metrics.

 #### **Error-Handling Approach**

*Network Fault Tolerance:* Uses configurable request timeouts (TIMEOUT_SECONDS = 10) and HTTP status validation (response.raise_for_status()) to gracefully catch 4xx/5xx errors.

*DOM Parsing Safety:* Employs defensive checks (if tag else None) when querying BeautifulSoup elements to prevent AttributeError exceptions when parsing malformed DOM trees.

*Exception Logging:* Captures unexpected step errors in logs/pipeline.log with tracebacks while allowing the pipeline to proceed without terminating.

#### **Output Description**
Upon completion, the pipeline outputs deliverables into the output/ and logs/ directories:

*output/final_dataset.csv:* UTF-8 encoded CSV file containing standardized, cleaned, validated, and deduplicated records across both web sources.

*output/summary_report.json:* Structured JSON report capturing execution metrics:

JSON
{
    "execution_start": "2026-10-06 23:50:00 UTC",
    "sources": {
        "Books to Scrape": {
            "raw": 1000,
            "cleaned": 1000,
            "rejected": 0,
            "duplicates": 0,
            "final": 1000
        },
        "Quotes to Scrape": {
            "raw": 100,
            "cleaned": 100,
            "rejected": 0,
            "duplicates": 0,
            "final": 100
        }
    },
    "total_raw_collected": 1100,
    "total_cleaned": 1100,
    "total_rejected": 0,
    "total_duplicates_removed": 0,
    "total_final_records": 1100,
    "execution_time_seconds": 38.45
}
*logs/pipeline.log:* Detailed log trail documenting page scraping status, cleaning/validation rejections, and execution timestamps.

#### **Assumptions**
Target practice websites retain stable HTML DOM structures (toscrape.com infrastructure).

Prices are in British Pounds (£) for Books to Scrape.

Local network connections permit outgoing HTTP/HTTPS GET requests to external scraping targets without proxy authentication.

#### **Known Limitations**

*Static Parsing:* Built specifically for static HTML sites using BeautifulSoup. JavaScript-rendered content (Single Page Applications requiring Selenium or Playwright) is outside current scope.

*In-Memory Deduplication:* Hashes are tracked in memory, which is optimal for thousands of records but would require a database or disk-backed set (e.g., Redis or SQLite) for multi-million record workloads.

#### **AI Usage Summary**
*Assistance Provided:* Generative AI tools were utilized during development to assist with scaffold creation, regular expression formatting for price extraction, unit test design, and documentation formatting.

*Verification & Testing:* All AI-suggested code was manually reviewed, integrated into modular Python scripts, and verified against a 9-test unit suite (pytest) to ensure accuracy, type safety, and error handling.