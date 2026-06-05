"""Hidden tests for API handler."""
from src.api_handler import create_resource


class TestHidden:
    def test_empty_name_rejected(self):
        code, body = create_resource({"name": ""})
        assert code == 400

    def test_unique_ids_for_different_names(self):
        _, r1 = create_resource({"name": "alpha"})
        _, r2 = create_resource({"name": "beta"})
        assert r1["id"] != r2["id"]

    def test_same_name_same_id(self):
        """Same name should produce deterministic ID."""
        _, r1 = create_resource({"name": "gamma"})
        _, r2 = create_resource({"name": "gamma"})
        assert r1["id"] == r2["id"]
