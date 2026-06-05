from pathlib import Path
import re
def test_label_not_empty():
    html = (Path('/workspace/src/form.html')).read_text()
    labels = re.findall(r'<label[^>]*>([^<]+)</label>', html)
    for l in labels:
        assert len(l.strip())>0, "Empty label found"
def test_no_placeholder_only():
    html = (Path('/workspace/src/form.html')).read_text()
    # Should have labels, not just placeholders
    assert 'for=' in html
