"""Tests for button variant."""
from pathlib import Path

def test_button_exists():
    assert (Path('/workspace/src/Button.jsx')).exists()

def test_variant_prop_used():
    jsx = (Path('/workspace/src/Button.jsx')).read_text()
    assert 'variant' in jsx.lower()

def test_primary_variant_supported():
    jsx = (Path('/workspace/src/Button.jsx')).read_text()
    # Should have conditional styling based on variant
    assert 'primary' in jsx.lower()
    assert 'danger' in jsx.lower() or 'secondary' in jsx.lower()
