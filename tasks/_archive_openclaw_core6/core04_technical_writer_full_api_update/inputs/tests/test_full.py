"""Tests for full API update."""
from pathlib import Path

def test_files_exist():
    for f in ['docs/README.md','docs/migration_guide.md','docs/api_reference.md']:
        assert (Path('/workspace')/f).exists(), f"Missing {f}"

def test_all_mention_v2():
    for f in ['docs/README.md','docs/migration_guide.md','docs/api_reference.md']:
        content = (Path('/workspace')/f).read_text()
        assert '/v2/' in content, f"{f} should mention /v2/"

def test_no_deprecated_params():
    for f in ['docs/README.md','docs/api_reference.md']:
        content = (Path('/workspace')/f).read_text()
        assert 'items_text' not in content, f"{f} still has items_text"
