"""Tests for changelog formatting."""
from pathlib import Path

def test_file_exists():
    assert (Path('/workspace/CHANGELOG.md')).exists()

def test_has_version_headers():
    content = (Path('/workspace/CHANGELOG.md')).read_text()
    assert '## [' in content, "Should use ## [version] format"

def test_has_date():
    content = (Path('/workspace/CHANGELOG.md')).read_text()
    import re
    assert re.search(r'\d{4}-\d{2}-\d{2}', content), "Should have dates"
