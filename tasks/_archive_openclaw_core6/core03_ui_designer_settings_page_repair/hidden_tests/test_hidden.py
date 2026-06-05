from pathlib import Path
def test_email_has_label():
    jsx = (Path('/workspace/src/SettingsPage.jsx')).read_text()
    assert 'for=' in jsx and 'email' in jsx.lower()
def test_danger_zone_at_bottom():
    jsx = (Path('/workspace/src/SettingsPage.jsx')).read_text()
    danger_idx = jsx.find('danger-zone')
    profile_idx = jsx.find('profile-section')
    assert danger_idx > profile_idx, "Danger zone should be after profile"
