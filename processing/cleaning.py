"""Pure data-cleaning helpers."""
import re
from urllib.parse import urljoin, urlparse

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def clean_text(value):
    if value is None:
        return None
    cleaned = " ".join(str(value).replace("\xa0", " ").split())
    return cleaned or None


def strip_quotes(value):
    cleaned = clean_text(value)
    return clean_text(cleaned.strip("“”\"'")) if cleaned else None


def clean_price(value):
    if value is None:
        return None
    match = re.search(r"\d+(?:,\d{3})*(?:\.\d+)?", str(value).replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(value):
    if isinstance(value, int) and value in range(1, 6):
        return value
    for word in (str(value or "").lower().split()):
        if word in RATING_MAP:
            return RATING_MAP[word]
    return None


def clean_tags(value):
    if not value:
        return None
    values = value if isinstance(value, (list, tuple, set)) else str(value).split(";")
    tags = sorted({clean_text(tag).lower() for tag in values if clean_text(tag)})
    return ";".join(tags) or None


def normalize_url(value, base=None):
    if not value:
        return None
    result = urljoin(base or "", str(value).strip())
    parsed = urlparse(result)
    return result if parsed.scheme in {"http", "https"} and parsed.netloc else None


def clean_record(raw):
    rec = dict(raw)
    rec["name_or_title"] = strip_quotes(rec.get("name_or_title")) if rec.get("source") == "Quotes to Scrape" else clean_text(rec.get("name_or_title"))
    rec["source"] = clean_text(rec.get("source"))
    rec["source_url"] = normalize_url(rec.get("source_url"))
    rec["category"] = clean_text(rec.get("category"))
    rec["author"] = clean_text(rec.get("author"))
    rec["description"] = clean_text(rec.get("description"))
    rec["price"] = clean_price(rec.get("price"))
    rec["rating"] = clean_rating(rec.get("rating"))
    rec["tags"] = clean_tags(rec.get("tags"))
    return rec

