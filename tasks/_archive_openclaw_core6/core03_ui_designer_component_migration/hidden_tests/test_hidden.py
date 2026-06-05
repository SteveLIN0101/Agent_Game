from pathlib import Path
def test_no_v1_colors():
    jsx = ''
    for f in ['Card.jsx','Modal.jsx','Badge.jsx','Tooltip.jsx']:
        jsx += (Path('/workspace/src')/f).read_text()
    v1_colors = ['#dee2e6','#495057','#212529','#f8f9fa','#e9ecef']
    for c in v1_colors:
        assert c not in jsx, f"v1 color {c} should be migrated"
