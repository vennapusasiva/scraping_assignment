# AI Usage & Transparency Log

## 1. AI Tools Used
* **Primary AI Tool:** Claude / ChatGPT (Generative AI Assistant)
* **Environment / Interface:** Interactive Conversational Assistant

---

## 2. Tool Usage Breakdown
The AI tool was utilized across key software development phases:

* **Architecture & Scaffolding:** Structuring a modular Python ETL repository layout (`scrapers/`, `processing/`, `tests/`, `output/`).
* **Regex & String Parsing:** Designing regular expressions to cleanly parse British currency strings (`£51.77` → `51.77`) and convert CSS word-ratings (`"Three"`) into floats (`3.0`).
* **Unit Test Design:** Generating test cases for `pytest` to test edge cases in text cleaning, validation rules, and cryptographic SHA-256 deduplication.
* **Debugging:** Identifying missing type hints (`NameError: name 'Optional' is not defined` in `validation.py`).
* **Documentation:** Generating structured Markdown documentation (`README.md` and `AI_USAGE.md`).

---

## 3. Representative Prompts Used

### Prompt 1 (Data Cleaning & Regex):
> *"Write a Python function using regex to extract floating-point price values from raw strings like '£51.77' or 'Â£12.99', returning None if parsing fails."*

### Prompt 2 (Deduplication):
> *"How do I build a deterministic SHA-256 fingerprinting system in Python that normalizes whitespace, lowercase characters, and title strings before hashing to prevent duplicate records?"*

### Prompt 3 (Debugging & Unit Testing):
> *"My pytest suite is throwing `NameError: name 'Optional' is not defined` on line 8 of processing/validation.py. How do I fix this while keeping type annotations?"*

---

## 4. AI-Assisted Code Modules

1. **`processing/cleaning.py`**:
   * Regex extraction logic for pricing (`clean_price`).
   * Mapping table for rating word conversion (`clean_rating`).
2. **`processing/deduplication.py`**:
   * String normalization helper (`normalize_string`).
   * In-memory hash tracking set logic (`deduplicate_records`).
3. **`processing/validation.py`**:
   * Type annotations (`Optional[str]`, `Tuple[bool, Optional[str]]`).
   * Domain-specific validation checks for rating boundaries and required fields.
4. **`tests/` directory**:
   * Unit test assertions in `test_cleaning.py`, `test_validation.py`, and `test_deduplication.py`.

---

## 5. Important Changes Made After Reviewing AI Output

* **Deduplication Logic Refinement:** AI initially suggested deduplicating solely on title/text (`name_or_title`). Refactored the fingerprinting key to combine `source + name_or_title + author` to ensure quotes with identical wording across different authors or sources were not falsely flagged as duplicates.
* **Pagination Relative URL Resolution:** The initial AI snippet assumed static page counts (`page-1.html` to `page-50.html`). Updated the scraper loop to dynamically parse the `li.next > a` element and use `urllib.parse.urljoin()` to handle relative pagination paths robustly.
* **Explicit Type Hint Imports:** Added `from typing import Optional, Dict, Any, Tuple` to fix execution crashes under Python strict type checks.

---

## 6. Incorrect or Incomplete AI Suggestions Discovered

* **Over-greedy Regex:** An initial AI-suggested price regex (`r'\d+\.\d+'`) dropped integer prices (e.g., `£50`). Corrected the pattern to `r'[\d.]+'` and cast it explicitly to `float()`.
* **Missing Encodings:** AI code examples used basic `open("output/final_dataset.csv", "w")` without specifying character encoding. Manually added `encoding="utf-8"` to prevent Windows platform `UnicodeEncodeError` when saving special characters and quotes.

---

## 7. How Final Solution Was Tested and Verified

1. **Unit Testing:** Ran `pytest -v` across 9 custom test cases covering string stripping, price extraction, rating bounds, missing fields, and duplicate hashing. All 9 tests passed.
2. **End-to-End Pipeline Execution:** Executed `python main.py` to confirm the scraper successfully crawled all 50 pages of Books to Scrape and 10 pages of Quotes to Scrape.
3. **Output Inspection:** Manually verified `output/final_dataset.csv` and `output/summary_report.json` to ensure clean fields, accurate timestamps, proper record totals (1,100 records), and non-empty log output in `logs/pipeline.log`.