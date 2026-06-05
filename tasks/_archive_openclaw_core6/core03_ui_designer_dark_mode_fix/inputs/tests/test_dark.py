"""Tests for dark mode support."""
from pathlib import Path

def test_css_exists():
    assert (Path('/workspace/styles/theme.css')).exists()

def test_prefers_color_scheme_present():
    css = (Path('/workspace/styles/theme.css')).read_text()
    assert 'prefers-color-scheme' in css, "Missing prefers-color-scheme media query"

def test_dark_mode_defines_colors():
    css = (Path('/workspace/styles/theme.css')).read_text()
    assert 'dark' in css.lower()
