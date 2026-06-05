"""Tests for config documentation."""
from pathlib import Path

def test_file_exists():
    assert (Path('/workspace/docs/config_reference.md')).exists()

def test_new_keys_documented():
    doc = (Path('/workspace/docs/config_reference.md')).read_text()
    for key in ['CACHE_TTL', 'MAX_RETRIES', 'LOG_LEVEL']:
        assert key in doc, f"Missing config key: {key}"
