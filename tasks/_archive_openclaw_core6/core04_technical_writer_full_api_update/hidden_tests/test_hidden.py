from pathlib import Path
def test_consistent_customer_id():
    for f in ['docs/README.md','docs/migration_guide.md','docs/api_reference.md']:
        content = (Path('/workspace')/f).read_text()
        assert 'customer_id' in content, f"{f} missing customer_id"
def test_migration_complete():
    guide = (Path('/workspace/docs/migration_guide.md')).read_text()
    assert len(guide.strip()) > 50, "Migration guide too short"
