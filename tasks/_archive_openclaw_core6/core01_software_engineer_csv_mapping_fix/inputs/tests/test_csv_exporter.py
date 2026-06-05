"""Tests for CSV exporter."""
from src.csv_exporter import export_to_csv, parse_csv


class TestExportToCSV:
    def test_single_user(self):
        users = [{"id": "1", "username": "alice", "email": "alice@example.com", "created_at": "2025-01-01"}]
        result = export_to_csv(users)
        lines = result.strip().split("\n")
        assert lines[0] == "id,email,username,created_at"
        assert "alice@example.com" in lines[1]
        assert "alice" in lines[1]

    def test_column_data_matches_header(self):
        users = [{"id": "1", "username": "bob", "email": "bob@test.com", "created_at": "2025-06-15"}]
        result = export_to_csv(users)
        parsed = parse_csv(result)
        assert parsed[0]["email"] == "bob@test.com"
        assert parsed[0]["username"] == "bob"

    def test_multiple_users(self):
        users = [
            {"id": "1", "username": "u1", "email": "u1@x.com", "created_at": "2025-01-01"},
            {"id": "2", "username": "u2", "email": "u2@x.com", "created_at": "2025-02-01"},
        ]
        result = export_to_csv(users)
        parsed = parse_csv(result)
        assert len(parsed) == 2
        assert parsed[0]["email"] == "u1@x.com"
        assert parsed[1]["username"] == "u2"


class TestParseCSV:
    def test_roundtrip(self):
        users = [{"id": "3", "username": "c", "email": "c@x.com", "created_at": "2025-03-01"}]
        csv_text = export_to_csv(users)
        parsed = parse_csv(csv_text)
        assert parsed[0]["email"] == "c@x.com"
