import pytest
from processing.validation import validate_record, is_valid_url


def test_is_valid_url():
    assert is_valid_url("https://books.toscrape.com") is True
    assert is_valid_url("http://quotes.toscrape.com/page/1/") is True
    assert is_valid_url("invalid-url-string") is False
    assert is_valid_url(None) is False


def test_validate_record_success():
    book_record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/book1",
        "name_or_title": "Book Title",
        "price": 10.99,
        "rating": 4.0
    }
    valid, reason = validate_record(book_record)
    assert valid is True
    assert reason is None


def test_validate_record_failure():
    invalid_book = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/book1",
        "name_or_title": "Book Title",
        "price": -5.00  # Invalid negative price
    }
    valid, reason = validate_record(invalid_book)
    assert valid is False
    assert "Invalid book price" in reason