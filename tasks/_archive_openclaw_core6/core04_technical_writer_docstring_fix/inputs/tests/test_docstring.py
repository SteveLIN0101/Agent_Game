"""Tests for docstring completeness."""
from pathlib import Path
import ast

def test_file_exists():
    assert (Path('/workspace/src/api_client.py')).exists()

def test_all_methods_have_docstrings():
    code = (Path('/workspace/src/api_client.py')).read_text()
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name != '__init__':
                body = node.body
                assert body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, (ast.Constant, ast.Str)), f"{node.name} missing docstring"
