from pathlib import Path
def test_aria_on_error():
    jsx = (Path('/workspace/src/Form.jsx')).read_text()
    assert 'aria-' in jsx.lower() or 'role=' in jsx.lower(), "Error should have aria attribute"
