"""Hidden edge-case tests for user config parser."""
import json
import pytest
from pathlib import Path
from src.user_config import get_user_config


class TestHiddenEdgeCases:
    def test_empty_config(self, tmp_path):
        config_path = tmp_path / "empty.json"
        config_path.write_text("{}")
        result = get_user_config(str(config_path))
        assert result["preferences"]["notifications"] is True
        assert result["preferences"]["auto_save"] is False

    def test_partial_preferences(self, tmp_path):
        config_path = tmp_path / "partial.json"
        config_path.write_text(json.dumps({
            "preferences": {"auto_save": True}
        }))
        result = get_user_config(str(config_path))
        assert result["preferences"]["auto_save"] is True
        assert result["preferences"]["notifications"] is True  # default

    def test_preferences_empty_dict(self, tmp_path):
        config_path = tmp_path / "empty_prefs.json"
        config_path.write_text(json.dumps({
            "preferences": {}
        }))
        result = get_user_config(str(config_path))
        assert result["preferences"]["notifications"] is True
