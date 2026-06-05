from pathlib import Path
import re
def test_all_spacing_uses_var():
    css = (Path('/workspace/styles/layout.css')).read_text()
    no_root = re.sub(r':root\s*\{[^}]*\}', '', css, flags=re.DOTALL)
    px_vals = re.findall(r'\d+px', no_root)
    # Only max-width or 0 should remain
    for v in px_vals:
        assert v == '0px' or 'max-width' in css, f"Unexpected px value: {v}"
