"""Hidden tests for color token fix."""
import re
from pathlib import Path


def test_all_hex_colors_replaced():
    """No hardcoded hex colors should remain in CSS rules (outside :root)."""
    content = (Path('/workspace') / 'styles' / 'theme.css').read_text()
    lines = content.split('\n')
    in_root = False
    violations = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if ':root' in stripped:
            in_root = True
            continue
        if in_root and '}' in stripped:
            in_root = False
            continue
        if in_root:
            continue
        if stripped.startswith('/*') or stripped.startswith('*'):
            continue
        # Check for hex colors
        if re.search(r'(?<!var\(--) #[0-9a-fA-F]{3,6}(?![-\w])', stripped):
            violations.append(f"Line {i}: {stripped}")
    assert len(violations) == 0, f"Found hardcoded hex colors:\n" + "\n".join(violations)


def test_var_functions_used():
    """CSS rules should use var() for colors."""
    content = (Path('/workspace') / 'styles' / 'theme.css').read_text()
    assert 'var(--' in content, "No var() references found in theme.css"


def test_design_notes_contains_changes():
    """design_notes.md should describe the changes made."""
    notes = (Path('/workspace') / 'design_notes.md').read_text()
    assert len(notes.strip()) > 0, "design_notes.md is empty"
    assert 'color' in notes.lower() or 'token' in notes.lower() or '变量' in notes.lower(), \
        "design_notes.md should mention color/token changes"
