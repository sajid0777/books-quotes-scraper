from processing.deduplication import find_duplicates


def test_duplicates_ignore_case_spacing_and_punctuation():
    base = {"source": "Books to Scrape", "author": None}
    records = [
        {**base, "name_or_title": "Example Book Title"},
        {**base, "name_or_title": "  Example Book Title! "},
        {**base, "name_or_title": "EXAMPLE BOOK TITLE"},
    ]
    unique, duplicates = find_duplicates(records)
    assert len(unique) == 1
    assert len(duplicates) == 2

