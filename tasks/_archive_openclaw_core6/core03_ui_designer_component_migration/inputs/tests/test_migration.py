"""Tests for component migration."""
from pathlib import Path

def test_files_exist():
    for f in ['Card.jsx','Modal.jsx','Badge.jsx','Tooltip.jsx']:
        assert (Path('/workspace/src')/f).exists(), f"Missing {f}"

def test_v2_tokens_used():
    # At least one component should use new design tokens
    jsx = ''
    for f in ['Card.jsx','Modal.jsx','Badge.jsx','Tooltip.jsx']:
        jsx += (Path('/workspace/src')/f).read_text()
    # Should avoid v1 hardcoded hex colors
    assert '#ffffff' not in jsx, "Components should use design tokens, not raw #ffffff"
