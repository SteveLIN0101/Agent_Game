"""Tests for OpenAPI sync."""
from pathlib import Path

def test_file_exists():
    assert (Path('/workspace/docs/api_reference.md')).exists()

def test_uses_v2():
    doc = (Path('/workspace/docs/api_reference.md')).read_text()
    assert '/v2/' in doc, "Should reference /v2/ endpoint"

def test_documents_customer_id():
    doc = (Path('/workspace/docs/api_reference.md')).read_text()
    assert 'customer_id' in doc
