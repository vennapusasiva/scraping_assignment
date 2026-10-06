import pytest
from processing.cleaning import clean_text, clean_price, clean_rating, clean_record


def test_clean_text():
    assert clean_text("  A Light in the   Attic  ") == "A Light in the Attic"
    assert clean_text('"Quote text"') == "Quote text"
    assert clean_text("") is None
    assert clean_text(None) is None


def test_clean_price():
    assert clean_price("£51.77") == 51.77
    assert clean_price("$19.99") == 19.99
    assert clean_price(42.50) == 42.50
    assert clean_price("No Price") is None
    assert clean_price(None) is None


def test_clean_rating():
    assert clean_rating(3.0) == 3.0
    assert clean_rating("4") == 4.0
    assert clean_rating(6.0) is None
    assert clean_rating(-1.0) is None
    assert clean_rating(None) is None


def test_clean_record():
    raw = {
        "source": " Books to Scrape ",
        "source_url": "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "name_or_title": " A Light in the Attic ",
        "category": "Books",
        "price": "£51.77",
        "rating": 3.0,
        "author": None,
        "tags": None,
        "description": "  Availability: In stock  "
    }
    cleaned = clean_record(raw)
    assert cleaned["source"] == "Books to Scrape"
    assert cleaned["name_or_title"] == "A Light in the Attic"
    assert cleaned["price"] == 51.77
    assert cleaned["rating"] == 3.0
    assert "scraped_at" in cleaned