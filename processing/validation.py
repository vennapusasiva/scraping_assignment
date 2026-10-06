import logging
from typing import Dict, Any, Tuple, Optional
from urllib.parse import urlparse

logger = logging.getLogger("ScraperPipeline")


def is_valid_url(url: Optional[str]) -> bool:
    """Verifies basic structure and schema of source URLs."""
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False


def validate_record(record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validates record integrity against domain business logic.
    Returns (is_valid, failure_reason).
    """
    # 1. Source Identification Check
    if not record.get("source") or record.get("source") not in ["Books to Scrape", "Quotes to Scrape"]:
        return False, "Missing or unrecognized source"

    # 2. Source URL Validation
    if not is_valid_url(record.get("source_url")):
        return False, "Invalid or missing source_url"

    # 3. Core Field Check
    if not record.get("name_or_title"):
        return False, "Missing essential title/quote text"

    # 4. Source-Specific Rules
    source = record.get("source")
    
    if source == "Books to Scrape":
        price = record.get("price")
        if price is None or not isinstance(price, (int, float)) or price < 0:
            return False, f"Invalid book price: {price}"
        
        rating = record.get("rating")
        if rating is not None and (rating < 1.0 or rating > 5.0):
            return False, f"Book rating out of bounds: {rating}"

    elif source == "Quotes to Scrape":
        if not record.get("author"):
            return False, "Quote missing required author field"

    return True, None