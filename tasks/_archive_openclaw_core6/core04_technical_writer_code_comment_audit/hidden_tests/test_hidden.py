from pathlib import Path
def test_tier_logic_commented():
    code = (Path('/workspace/src/complex_algorithm.py')).read_text()
    # Complex tier logic should have explanatory comments
    assert 'tier' in code.lower() or 'gold' in code.lower()
    # Should explain WHY, not just WHAT
    comment_lines = [l.strip() for l in code.split('\n') if l.strip().startswith('#')]
    assert len(comment_lines) >= 3
