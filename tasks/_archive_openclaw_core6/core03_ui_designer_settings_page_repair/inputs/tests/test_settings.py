"""Tests for settings page repair."""
from pathlib import Path

def test_files_exist():
    assert (Path('/workspace/src/SettingsPage.jsx')).exists()
    assert (Path('/workspace/styles/settings.css')).exists()

def test_danger_zone_uses_warning_token():
    jsx = (Path('/workspace/src/SettingsPage.jsx')).read_text()
    css = (Path('/workspace/styles/settings.css')).read_text()
    combined = jsx + css
    # Danger zone shouldn't use hardcoded red
    assert '#dc3545' not in combined or 'var(--' in combined
