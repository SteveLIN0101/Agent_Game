"""Tests for responsive nav."""
from pathlib import Path

def test_files_exist():
    assert (Path('/workspace/src/Navbar.jsx')).exists()
    assert (Path('/workspace/styles/nav.css')).exists()

def test_css_has_responsive_handling():
    css = (Path('/workspace/styles/nav.css')).read_text()
    assert '@media' in css or 'flex-wrap' in css or 'overflow' in css or 'hamburger' in css.lower()
