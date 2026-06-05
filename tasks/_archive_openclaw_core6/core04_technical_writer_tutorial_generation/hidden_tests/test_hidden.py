from pathlib import Path
def test_tutorial_covers_crud():
    tut = (Path('/workspace/docs/tutorial.md')).read_text().lower()
    concepts = ['create', 'read', 'list', 'error']
    found = sum(1 for c in concepts if c in tut)
    assert found >= 2, f"Tutorial should cover CRUD operations, found {found}/4"
