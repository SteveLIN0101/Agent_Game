from pathlib import Path
def test_focus_visible_has_visible_style():
    css = (Path('/workspace/styles/global.css')).read_text()
    assert ':focus-visible' in css
    # Should have a visible indicator like box-shadow or outline
    idx = css.find(':focus-visible')
    after = css[idx:idx+200]
    assert 'box-shadow' in after or 'outline' in after, ":focus-visible should have visible style"
