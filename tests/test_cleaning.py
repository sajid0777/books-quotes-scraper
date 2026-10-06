from processing.cleaning import clean_price, clean_rating, clean_tags, clean_text, strip_quotes, normalize_url


def test_clean_text_whitespace_and_nbsp():
    assert clean_text("  Hello\n World\xa0!") == "Hello World !"


def test_cleaners():
    assert strip_quotes("“ hello ”") == "hello"
    assert clean_price(" £51.77 ") == 51.77
    assert clean_rating("star-rating Three") == 3
    assert clean_tags(["Z", "a", "Z"]) == "a;z"
    assert normalize_url("../page", "https://example.com/a/b") == "https://example.com/page"

