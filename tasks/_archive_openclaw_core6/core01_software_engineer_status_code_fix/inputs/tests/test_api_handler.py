"""Tests for API handler."""
from src.api_handler import create_resource, get_resource, delete_resource


class TestCreateResource:
    def test_returns_201_on_success(self):
        code, body = create_resource({"name": "test-resource"})
        assert code == 201, f"Expected 201, got {code}"

    def test_returns_400_on_missing_name(self):
        code, body = create_resource({})
        assert code == 400
        assert "error" in body

    def test_returns_resource_with_id(self):
        code, body = create_resource({"name": "my-item"})
        assert body["id"].startswith("res_")
        assert body["name"] == "my-item"
        assert body["status"] == "created"


class TestGetResource:
    def test_returns_200_for_valid_id(self):
        code, body = get_resource("res_0001")
        assert code == 200

    def test_returns_400_for_invalid_id(self):
        code, body = get_resource("bad-id")
        assert code == 400


class TestDeleteResource:
    def test_returns_204_on_success(self):
        code, body = delete_resource("res_0001")
        assert code == 204
