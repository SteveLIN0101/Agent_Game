"""Tests for tutorial generation."""
from pathlib import Path

def test_files_exist():
    assert (Path('/workspace/docs/tutorial.md')).exists()
    assert (Path('/workspace/examples/tutorial_code.py')).exists()

def test_tutorial_has_setup_section():
    tut = (Path('/workspace/docs/tutorial.md')).read_text()
    assert 'setup' in tut.lower() or 'install' in tut.lower() or '准备' in tut.lower() or '环境' in tut.lower()

def test_tutorial_code_runnable():
    code = (Path('/workspace/examples/tutorial_code.py')).read_text()
    try:
        compile(code, 'tutorial_code.py', 'exec')
    except SyntaxError as e:
        assert False, f"Syntax error: {e}"
