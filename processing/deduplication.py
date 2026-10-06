import re
import hashlib
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("ScraperPipeline")


def normalize_string_for_hash(text: str) -> str:
    """Standardizes string by lowering case, removing punctuation, and collapsing whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # Strip punctuation
    text = re.sub(r"\s+", " ", text).strip()
    return text


def generate_record_hash(record: Dict[str, Any]) -> str:
    """Generates a deterministic SHA256 signature for fuzzy duplicate detection."""
    source = (record.get("source") or "").lower().strip()
    title = normalize_string_for_hash(record.get("name_or_title") or "")
    author = normalize_string_for_hash(record.get("author") or "")

    # Combine key signature fields
    raw_key = f"{source}|{title}|{author}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def deduplicate_records(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    """
    Filters records by identifying and discarding duplicate entity hashes.
    Returns (unique_records, duplicate_count).
    """
    seen_hashes = set()
    unique_records = []
    duplicate_count = 0

    for rec in records:
        rec_hash = generate_record_hash(rec)
        if rec_hash in seen_hashes:
            duplicate_count += 1
            logger.debug(f"Duplicate record caught: '{rec.get('name_or_title')}' [{rec.get('source')}]")
        else:
            seen_hashes.add(rec_hash)
            unique_records.append(rec)

    return unique_records, duplicate_count