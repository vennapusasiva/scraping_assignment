import pytest
from processing.deduplication import deduplicate_records, normalize_string_for_hash


def test_normalize_string():
    assert normalize_string_for_hash("  Example Book Title!  ") == "example book title"


def test_deduplicate_records():
    records = [
        {"source": "Books to Scrape", "name_or_title": "The Secret Garden", "author": None},
        {"source": "Books to Scrape", "name_or_title": " The Secret Garden ", "author": None},  # Duplicate
        {"source": "Quotes to Scrape", "name_or_title": "The World as I See It", "author": "Albert Einstein"},
    ]
    uniques, dup_count = deduplicate_records(records)
    assert len(uniques) == 2
    assert dup_count == 1