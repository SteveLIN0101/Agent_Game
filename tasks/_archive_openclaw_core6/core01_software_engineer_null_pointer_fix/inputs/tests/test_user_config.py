"""Tests for user config parser."""
import json
import pytest
from pathlib import Path
from src.user_config import get_user_config, get_theme, get_language


class TestGetUserConfig:
    def test_default_config_no_file(self, tmp_path):
        config_path = tmp_path / "nonexistent.json"
        result = get_user_config(str(config_path))
        assert result["theme"] == "light"
        assert result["language"] == "en"
        assert result["preferences"] == {"notifications": True, "auto_save": False}

    def test_full_config(self, tmp_path):
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({
            "theme": "dark",
            "language": "zh",
            "preferences": {
                "notifications": False,
                "auto_save": True,
            },
        }))
        result = get_user_config(str(config_path))
        assert result["theme"] == "dark"
        assert result["language"] == "zh"
        assert result["preferences"]["notifications"] is False
        assert result["preferences"]["auto_save"] is True

    def test_missing_preferences_key(self, tmp_path):
        """Config without preferences key should not crash."""
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({
            "theme": "dark",
        }))
        result = get_user_config(str(config_path))
        assert result["preferences"]["notifications"] is True
        assert result["preferences"]["auto_save"] is False

    def test_null_preferences(self, tmp_path):
        """Config with null preferences should not crash."""
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({
            "theme": "light",
            "preferences": None,
        }))
        result = get_user_config(str(config_path))
        assert result["preferences"]["notifications"] is True


class TestHelpers:
    def test_get_theme(self):
        assert get_theme({"theme": "dark"}) == "dark"

    def test_get_language(self):
        assert get_language({"language": "zh"}) == "zh"
