"""Tests for file reader."""
import pytest
from pathlib import Path
from src.file_reader import read_config_file, read_text_file


class TestReadConfigFile:
    def test_simple_config(self, tmp_path):
        config = tmp_path / "test.cfg"
        config.write_text("key1=value1\nkey2=value2\n", encoding='utf-8')
        result = read_config_file(str(config))
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"

    def test_config_with_comments(self, tmp_path):
        config = tmp_path / "test.cfg"
        config.write_text("# comment\nname=hello\n", encoding='utf-8')
        result = read_config_file(str(config))
        assert "name" in result
        assert "# comment" not in result

    def test_config_with_chinese(self, tmp_path):
        config = tmp_path / "test.cfg"
        config.write_text("name=张三\ncity=北京\n", encoding='utf-8')
        result = read_config_file(str(config))
        assert result["name"] == "张三"
        assert result["city"] == "北京"

    def test_config_with_japanese(self, tmp_path):
        config = tmp_path / "test.cfg"
        config.write_text("greeting=こんにちは\n", encoding='utf-8')
        result = read_config_file(str(config))
        assert result["greeting"] == "こんにちは"


class TestReadTextFile:
    def test_utf8_content(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("Hello 世界", encoding='utf-8')
        content = read_text_file(str(f))
        assert "世界" in content
