"""Hidden edge-case tests for file reader."""
from pathlib import Path
from src.file_reader import read_config_file


class TestHidden:
    def test_emoji_in_config(self, tmp_path):
        config = tmp_path / "test.cfg"
        config.write_text("mood=😀\nstatus=✅\n", encoding='utf-8')
        result = read_config_file(str(config))
        assert result["mood"] == "😀"

    def test_accented_characters(self, tmp_path):
        config = tmp_path / "test.cfg"
        config.write_text("cafe=café\nresume=résumé\n", encoding='utf-8')
        result = read_config_file(str(config))
        assert result["cafe"] == "café"

    def test_mixed_encoding_content(self, tmp_path):
        config = tmp_path / "test.cfg"
        config.write_text("mixed=Latin + 中文 + 日本語 + 한국어\n", encoding='utf-8')
        result = read_config_file(str(config))
        assert "中文" in result["mixed"]
