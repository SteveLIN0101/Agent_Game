from pathlib import Path
def test_dark_bg_not_pure_black():
    css = (Path('/workspace/styles/theme.css')).read_text()
    if 'prefers-color-scheme: dark' in css:
        idx = css.find('prefers-color-scheme: dark')
        after = css[idx:idx+500]
        assert '#000' not in after and '#000000' not in after, "Dark bg should not be pure black"
