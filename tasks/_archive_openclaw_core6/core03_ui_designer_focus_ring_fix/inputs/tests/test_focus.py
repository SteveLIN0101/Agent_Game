"""Tests for focus indicators."""
from pathlib import Path

def test_css_exists():
    assert (Path('/workspace/styles/global.css')).exists()

def test_focus_visible_present():
    css = (Path('/workspace/styles/global.css')).read_text()
    assert ':focus-visible' in css, "Missing :focus-visible styles"

def test_no_outline_none_without_replacement():
    css = (Path('/workspace/styles/global.css')).read_text()
    # If outline:none is used, there must be :focus-visible with visible style
    if 'outline: none' in css or 'outline:none' in css:
        assert ':focus-visible' in css, "outline:none without :focus-visible replacement"
