from pathlib import Path
def test_docstrings_contain_params():
    code = (Path('/workspace/src/api_client.py')).read_text()
    assert 'Args:' in code or 'Parameters' in code or 'Args' in code
    assert 'Returns:' in code or 'return' in code.lower()
