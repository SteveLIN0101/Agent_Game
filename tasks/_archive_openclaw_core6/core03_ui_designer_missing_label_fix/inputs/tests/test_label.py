"""Tests for accessible labels."""
from pathlib import Path

def test_email_has_label():
    html = (Path('/workspace/src/form.html')).read_text()
    assert 'for="' in html, "No for attributes found"
    assert '<label' in html.lower(), "No label elements found"

def test_all_inputs_have_labels():
    html = (Path('/workspace/src/form.html')).read_text()
    import re
    input_ids = re.findall(r'<input[^>]*id="([^"]*)"', html)
    for_inputs = re.findall(r'for="([^"]*)"', html)
    for iid in input_ids:
        assert iid in for_inputs, f"No label for input#{iid}"
