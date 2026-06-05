"""Tests for API documentation accuracy."""
import yaml
from pathlib import Path

WORKSPACE = Path('/workspace')


def load_v2_spec():
    with open(WORKSPACE / 'api/openapi_v2.yaml') as f:
        return yaml.safe_load(f)


def test_readme_exists():
    assert (WORKSPACE / 'docs/README.md').exists(), "docs/README.md not found"


def test_readme_mentions_v2_endpoint():
    content = (WORKSPACE / 'docs/README.md').read_text()
    assert '/v2/invoices' in content, "README should mention /v2/invoices endpoint"


def test_readme_mentions_customer_id():
    content = (WORKSPACE / 'docs/README.md').read_text()
    assert 'customer_id' in content, "README should document customer_id parameter"


def test_readme_mentions_line_items():
    content = (WORKSPACE / 'docs/README.md').read_text()
    assert 'line_items' in content, "README should document line_items parameter"


def test_readme_marks_deprecated_params():
    content = (WORKSPACE / 'docs/README.md').read_text()
    assert 'deprecated' in content.lower() or 'user' not in content.split('##')[0], \
        "README should mark deprecated parameters"
