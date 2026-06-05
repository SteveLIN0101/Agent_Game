from pathlib import Path
def test_three_variants():
    jsx = (Path('/workspace/src/Button.jsx')).read_text()
    assert 'primary' in jsx.lower()
    assert 'secondary' in jsx.lower()
    assert 'danger' in jsx.lower()
def test_variant_changes_style():
    jsx = (Path('/workspace/src/Button.jsx')).read_text()
    # Variant should cause different background color
    assert 'background' in jsx.lower() or 'color' in jsx.lower() or 'className' in jsx
