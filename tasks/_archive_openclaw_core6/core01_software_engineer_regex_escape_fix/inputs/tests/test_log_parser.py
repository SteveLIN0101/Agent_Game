"""Tests for log parser."""
from src.log_parser import parse_log_entry, filter_by_level


class TestParseLogEntry:
    def test_info_log(self):
        line = "[INFO] [2025-01-15 10:30:00] User login (user=alice, ip=192.168.1.1)"
        result = parse_log_entry(line)
        assert result is not None, "Failed to parse valid log line"
        assert result["level"] == "INFO"
        assert result["timestamp"] == "2025-01-15 10:30:00"
        assert result["message"] == "User login"
        assert result["data"]["user"] == "alice"
        assert result["data"]["ip"] == "192.168.1.1"

    def test_error_log(self):
        line = "[ERROR] [2025-06-01 14:22:00] Connection failed (host=db1, code=500)"
        result = parse_log_entry(line)
        assert result is not None
        assert result["level"] == "ERROR"
        assert result["data"]["host"] == "db1"

    def test_warn_log_with_single_kv(self):
        line = "[WARN] [2025-03-10 08:00:00] Disk usage high (usage=95%)"
        result = parse_log_entry(line)
        assert result is not None
        assert result["level"] == "WARN"
        assert result["data"]["usage"] == "95%"


class TestFilterByLevel:
    def test_filter_info(self):
        lines = [
            "[INFO] [2025-01-01 00:00:00] Start (a=1)",
            "[ERROR] [2025-01-01 00:01:00] Fail (b=2)",
            "[INFO] [2025-01-01 00:02:00] End (c=3)",
        ]
        results = filter_by_level(lines, "INFO")
        assert len(results) == 2
        assert all(r["level"] == "INFO" for r in results)
