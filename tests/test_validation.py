from processing.validation import validate_record


def test_validation_reports_multiple_reasons():
    assert validate_record({"source": "unknown", "name_or_title": "", "source_url": "bad"}) == ["unknown_source", "missing_name", "invalid_url"]

