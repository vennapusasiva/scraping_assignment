import re
import unicodedata
from datetime import datetime, timezone
from typing import Dict, Any, Optional


def clean_text(text: Optional[str]) -> Optional[str]:
    """Cleans whitespace, strips quotes/newlines, and normalizes unicode characters."""
    if not text:
        return None
    # Normalize unicode forms (NFKD)
    normalized = unicodedata.normalize("NFKD", text)
    # Strip leading/trailing quotation marks if wrapping quotes
    cleaned = normalized.strip().strip('""''“”')
    # Collapse multiple whitespaces/newlines into single space
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned if cleaned else None


def clean_price(price_raw: Any) -> Optional[float]:
    """Extracts numeric price value from string representations like '£51.77'."""
    if price_raw is None:
        return None
    if isinstance(price_raw, (int, float)):
        return float(price_raw)
    
    # Extract numerical digits and decimal points
    match = re.search(r"(\d+\.\d+|\d+)", str(price_raw))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def clean_rating(rating_raw: Any) -> Optional[float]:
    """Validates and casts rating values to float."""
    if rating_raw is None:
        return None
    try:
        val = float(rating_raw)
        return val if 1.0 <= val <= 5.0 else None
    except (ValueError, TypeError):
        return None


def clean_record(raw_record: Dict[str, Any]) -> Dict[str, Any]:
    """Applies standardized transformations across all fields in a single record."""
    return {
        "source": clean_text(raw_record.get("source")),
        "source_url": clean_text(raw_record.get("source_url")),
        "name_or_title": clean_text(raw_record.get("name_or_title")),
        "category": clean_text(raw_record.get("category")),
        "price": clean_price(raw_record.get("price")),
        "rating": clean_rating(raw_record.get("rating")),
        "author": clean_text(raw_record.get("author")),
        "tags": clean_text(raw_record.get("tags")),
        "description": clean_text(raw_record.get("description")),
        "scraped_at": datetime.now(timezone.utc).isoformat()
    }