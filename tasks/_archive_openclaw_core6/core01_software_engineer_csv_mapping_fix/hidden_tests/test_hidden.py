"""Hidden tests for CSV exporter."""
from src.csv_exporter import export_to_csv, parse_csv


class TestHidden:
    def test_empty_list(self):
        result = export_to_csv([])
        lines = result.strip().split("\n")
        assert len(lines) == 1  # header only

    def test_special_characters_in_email(self):
        users = [{"id": "1", "username": "test", "email": "test+tag@domain.co.uk", "created_at": "2025-01-01"}]
        result = export_to_csv(users)
        parsed = parse_csv(result)
        assert parsed[0]["email"] == "test+tag@domain.co.uk"

    def test_unicode_in_username(self):
        users = [{"id": "1", "username": "张三", "email": "zhang@example.com", "created_at": "2025-01-01"}]
        result = export_to_csv(users)
        parsed = parse_csv(result)
        assert parsed[0]["username"] == "张三"
        assert parsed[0]["email"] == "zhang@example.com"
