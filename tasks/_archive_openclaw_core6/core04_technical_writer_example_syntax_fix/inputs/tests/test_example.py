"""Tests for example code."""
from pathlib import Path

def test_file_exists():
    assert (Path('/workspace/examples/create_invoice.py')).exists()

def test_compiles_without_syntax_error():
    code = (Path('/workspace/examples/create_invoice.py')).read_text()
    try:
        compile(code, 'create_invoice.py', 'exec')
    except SyntaxError as e:
        assert False, f"Syntax error: {e}"

def test_uses_v2():
    code = (Path('/workspace/examples/create_invoice.py')).read_text()
    assert '/v2/' in code, "Should use /v2/ endpoint"
    assert '/v1/' not in code
