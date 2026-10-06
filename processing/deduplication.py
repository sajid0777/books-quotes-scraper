"""Normalized fingerprints and duplicate separation."""
import hashlib
import re


def make_fingerprint(rec):
    if rec.get("source") == "Books to Scrape":
        parts = [rec.get("source", ""), rec.get("name_or_title", "")]
    else:
        parts = [rec.get("source", ""), rec.get("author", ""), str(rec.get("name_or_title", ""))[:50]]
    key = " ".join(" ".join(re.sub(r"[^\w\s]", "", str(part).lower()).split()) for part in parts)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def find_duplicates(records):
    seen, unique, duplicates = set(), [], []
    for rec in records:
        fingerprint = make_fingerprint(rec)
        target = duplicates if fingerprint in seen else unique
        target.append(rec)
        seen.add(fingerprint)
    return unique, duplicates

