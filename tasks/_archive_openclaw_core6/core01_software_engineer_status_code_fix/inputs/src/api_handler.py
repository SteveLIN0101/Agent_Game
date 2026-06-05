"""Simple REST API handler."""


def create_resource(data: dict) -> tuple[int, dict]:
    """Create a new resource and return (status_code, response_body).

    BUG: Returns 200 instead of 201 for successful creation.
    """
    if not data.get("name"):
        return 400, {"error": "name is required"}

    resource_id = f"res_{hash(data['name']) % 10000:04d}"
    resource = {"id": resource_id, "name": data["name"], "status": "created"}

    # BUG: should return 201, not 200
    return 200, resource


def get_resource(resource_id: str) -> tuple[int, dict]:
    """Get a resource by ID."""
    if not resource_id.startswith("res_"):
        return 400, {"error": "invalid resource id format"}
    return 200, {"id": resource_id, "name": "Example", "status": "active"}


def delete_resource(resource_id: str) -> tuple[int, dict]:
    """Delete a resource."""
    if not resource_id.startswith("res_"):
        return 400, {"error": "invalid resource id format"}
    return 204, {}
