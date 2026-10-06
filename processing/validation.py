"""Record checks return stable reason codes for reporting."""
VALID_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def validate_record(rec):
    issues = []
    if rec.get("source") not in VALID_SOURCES:
        issues.append("unknown_source")
    if not rec.get("name_or_title"):
        issues.append("missing_name")
    if not str(rec.get("source_url") or "").startswith(("http://", "https://")):
        issues.append("invalid_url")
    price = rec.get("price")
    if price is not None and (not isinstance(price, (int, float)) or price < 0):
        issues.append("invalid_price")
    rating = rec.get("rating")
    if rating is not None and (not isinstance(rating, int) or rating not in range(1, 6)):
        issues.append("invalid_rating")
    return issues

