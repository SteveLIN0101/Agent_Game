"""Access control module for resource permissions."""


def can_access(username: str, resource: str, role: str = "user",
               permissions: list[str] | None = None) -> bool:
    """Check if a user can access a resource.

    Admins can access everything.
    Non-admins need explicit read permission on the resource.

    BUG: The boolean logic is wrong — admins with read permission are denied.
    """
    if permissions is None:
        permissions = []

    # BUG: should be OR, not AND
    # Admin should access regardless of permissions
    # The current logic requires BOTH admin AND read permission
    if role == "admin" and "read" in permissions:
        return True

    # Regular user with read permission
    if role != "admin" and "read" in permissions:
        return True

    return False


def list_accessible_resources(username: str, role: str,
                               permissions: dict[str, list[str]]) -> list[str]:
    """List all resources a user can access."""
    accessible = []
    for resource, perms in permissions.items():
        if can_access(username, resource, role, perms):
            accessible.append(resource)
    return accessible
