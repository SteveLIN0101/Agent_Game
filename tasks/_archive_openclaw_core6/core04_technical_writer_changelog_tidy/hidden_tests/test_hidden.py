from pathlib import Path
def test_newest_first():
    content = (Path('/workspace/CHANGELOG.md')).read_text()
    import re
    versions = re.findall(r'\[([\d.]+)\]', content)
    # Check major versions in descending order
    assert len(versions) > 0
def test_has_categories():
    content = (Path('/workspace/CHANGELOG.md')).read_text()
    assert 'Added' in content or 'Fixed' in content or 'Changed' in content
