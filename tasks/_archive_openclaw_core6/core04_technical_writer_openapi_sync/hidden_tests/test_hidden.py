from pathlib import Path
def test_no_deprecated_params():
    doc = (Path('/workspace/docs/api_reference.md')).read_text()
    assert 'items_text' not in doc, "items_text is deprecated in v2"
def test_line_items_documented():
    doc = (Path('/workspace/docs/api_reference.md')).read_text()
    assert 'line_items' in doc
