"""Tests for migration guide."""
from pathlib import Path

def test_files_exist():
    assert (Path('/workspace/docs/migration_guide.md')).exists()
    assert (Path('/workspace/examples/create_invoice_v2.py')).exists()

def test_migration_mentions_endpoints():
    guide = (Path('/workspace/docs/migration_guide.md')).read_text()
    assert '/v1/invoices' in guide or '/v2/invoices' in guide

def test_example_v2_runnable_syntax():
    code = (Path('/workspace/examples/create_invoice_v2.py')).read_text()
    try:
        compile(code, 'test.py', 'exec')
    except SyntaxError as e:
        assert False, f"Syntax error in v2 example: {e}"
