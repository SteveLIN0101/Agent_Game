"""Tests for spacing token compliance."""
from pathlib import Path
import re

def test_css_exists():
    assert (Path('/workspace/styles/layout.css')).exists()

def test_var_spacing_used():
    css = (Path('/workspace/styles/layout.css')).read_text()
    # Remove :root block
    no_root = re.sub(r':root\s*\{[^}]*\}', '', css, flags=re.DOTALL)
    assert 'var(--spacing-' in no_root, "No spacing tokens used outside :root"

def test_no_hardcoded_px_spacing():
    css = (Path('/workspace/styles/layout.css')).read_text()
    no_root = re.sub(r':root\s*\{[^}]*\}', '', css, flags=re.DOTALL)
    # Allow max-width and 0 values, flag px used for padding/margin/gap
    hardcoded = re.findall(r'(?:padding|margin|gap)\s*:\s*\d+px', no_root)
    assert not hardcoded, f"Hardcoded px spacing: {hardcoded}"
