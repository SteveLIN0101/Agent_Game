"""Hidden tests for log parser."""
from src.log_parser import parse_log_entry


class TestHidden:
    def test_message_with_special_chars(self):
        line = "[INFO] [2025-01-01 00:00:00] Test [nested] brackets (key=val)"
        result = parse_log_entry(line)
        assert result is not None
        assert "nested" in result["message"]

    def test_debug_level(self):
        line = "[DEBUG] [2025-07-01 12:00:00] Trace (func=main, line=42)"
        result = parse_log_entry(line)
        assert result is not None
        assert result["level"] == "DEBUG"

    def test_empty_kv_pairs(self):
        line = "[INFO] [2025-01-01 00:00:00] No data ()"
        result = parse_log_entry(line)
        assert result is not None
        assert result["data"] == {}
