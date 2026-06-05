from pathlib import Path
def test_param_mapping_documented():
    guide = (Path('/workspace/docs/migration_guide.md')).read_text()
    assert 'customer_id' in guide
    assert 'line_items' in guide
    assert 'due_date' in guide
