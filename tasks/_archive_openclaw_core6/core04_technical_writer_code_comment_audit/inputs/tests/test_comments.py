"""Tests for code comments."""
from pathlib import Path

def test_file_exists():
    assert (Path('/workspace/src/complex_algorithm.py')).exists()

def test_has_comments():
    code = (Path('/workspace/src/complex_algorithm.py')).read_text()
    # Should have comments (lines starting with #)
    comment_lines = [l for l in code.split('\n') if l.strip().startswith('#')]
    assert len(comment_lines) >= 3, f"Expected >= 3 comment lines, got {len(comment_lines)}"

def test_functions_unchanged():
    code = (Path('/workspace/src/complex_algorithm.py')).read_text()
    assert 'def calculate_invoice_totals' in code
    assert 'def apply_late_fees' in code
    assert 'rounding_factor' in code
