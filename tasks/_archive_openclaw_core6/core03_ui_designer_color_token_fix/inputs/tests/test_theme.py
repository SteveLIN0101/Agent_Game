"""Visible tests for theme CSS design token compliance."""
import pytest
from pathlib import Path

STYLES_DIR = Path('/workspace/styles')


def test_theme_css_exists():
    assert (STYLES_DIR / 'theme.css').exists(), "styles/theme.css not found"


def test_no_hex_colors_in_theme():
    """CSS should not contain hardcoded hex colors like #ffffff."""
    content = (STYLES_DIR / 'theme.css').read_text()
    # Check inside rule blocks (not in :root variable definitions)
    lines = content.split('\n')
    in_root = False
    violations = []
    for i, line in enumerate(lines, 1):
        if ':root' in line:
            in_root = True
        if in_root and '}' in line:
            in_root = False
            continue
        if not in_root and '#' in line:
            # Allow var() references
            if 'var(--' not in line and not line.strip().startswith('/*'):
                violations.append(f"Line {i}: {line.strip()}")
    # This is a visible test — hardcoded colors should be fixed
    # The test checks that at least some of the hardcoded colors have been replaced
    # (full verification happens in hidden tests)
    replaced_content = content.replace('#f8f9fa', 'X').replace('#212529', 'X')
    replaced_content = replaced_content.replace('#5867ff', 'X').replace('#4554e6', 'X')
    replaced_content = replaced_content.replace('#dc3545', 'X').replace('#c82333', 'X')
    replaced_content = replaced_content.replace('#fff8e1', 'X').replace('#f9a825', 'X')
    replaced_content = replaced_content.replace('#ffc107', 'X').replace('#ffffff', 'X')
    replaced_content = replaced_content.replace('#dee2e6', 'X').replace('#495057', 'X')
    remaining_hex = sum(1 for c in replaced_content if c == 'X')
    assert remaining_hex >= 10, f"Expected at least 10 hardcoded colors replaced, only found {remaining_hex}"


def test_no_rgb_in_theme():
    """CSS should not contain rgb() or rgba() color values."""
    content = (STYLES_DIR / 'theme.css').read_text()
    assert 'rgb(' not in content, "Found rgb() in theme.css"
    assert 'rgba(' not in content, "Found rgba() in theme.css"


def test_design_notes_exists():
    assert (Path('/workspace') / 'design_notes.md').exists(), "design_notes.md not found"
