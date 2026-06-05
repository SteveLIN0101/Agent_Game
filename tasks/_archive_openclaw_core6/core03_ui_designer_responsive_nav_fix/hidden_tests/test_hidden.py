from pathlib import Path
def test_no_horizontal_overflow():
    css = (Path('/workspace/styles/nav.css')).read_text()
    jsx = (Path('/workspace/src/Navbar.jsx')).read_text()
    # Should handle narrow viewports
    has_responsive = '@media' in css or 'flex-wrap' in css or 'overflow-x' in css or 'toggle' in jsx.lower() or 'menu' in jsx.lower()
    assert has_responsive, "No responsive handling found"
