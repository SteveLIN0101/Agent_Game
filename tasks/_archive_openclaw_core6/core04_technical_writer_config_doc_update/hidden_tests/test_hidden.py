from pathlib import Path
def test_defaults_correct():
    doc = (Path('/workspace/docs/config_reference.md')).read_text()
    assert '3600' in doc, "CACHE_TTL default should be 3600"
    assert '3' in doc, "MAX_RETRIES should be documented"
    assert 'INFO' in doc, "LOG_LEVEL default should be INFO"
