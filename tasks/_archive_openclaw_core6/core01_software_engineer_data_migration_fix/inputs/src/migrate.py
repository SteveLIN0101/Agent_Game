"""Data migration from old schema to new schema."""


def migrate_data(users: list[dict], orders: list[dict]) -> list[dict]:
    """Migrate user+order data to a unified format.

    BUG: When users and orders have different lengths, rows are silently
    dropped instead of using proper JOIN semantics.
    """
    result = []
    # BUG: zip() silently truncates to the shorter list
    # Should use a proper nested loop (LEFT JOIN semantics)
    for user, order in zip(users, orders):
        result.append({
            "user_id": user["id"],
            "user_name": user["name"],
            "order_id": order["id"],
            "order_amount": order["amount"],
        })
    return result


def count_migrated(source_users: list[dict], source_orders: list[dict]) -> dict:
    """Return stats about the migration."""
    migrated = migrate_data(source_users, source_orders)
    return {
        "source_users": len(source_users),
        "source_orders": len(source_orders),
        "migrated_rows": len(migrated),
        "all_preserved": len(migrated) == max(len(source_users), len(source_orders)),
    }
