"""Tests for form validation."""
from pathlib import Path

def test_form_exists():
    assert (Path('/workspace/src/Form.jsx')).exists()

def test_has_validation():
    jsx = (Path('/workspace/src/Form.jsx')).read_text()
    assert 'error' in jsx.lower() or 'valid' in jsx.lower()

def test_error_displayed():
    jsx = (Path('/workspace/src/Form.jsx')).read_text()
    # Should have error state and display it
    assert 'error' in jsx.lower()
