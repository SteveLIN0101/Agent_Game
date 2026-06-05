"""CSV export utilities."""

import csv
import io


def export_to_csv(users: list[dict]) -> str:
    """Export user list to CSV format.

    BUG: Column names are swapped — email column gets username data and vice versa.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # BUG: header order doesn't match data order
    writer.writerow(["id", "email", "username", "created_at"])

    for u in users:
        # BUG: email and username are swapped in the row
        writer.writerow([
            u["id"],
            u["username"],   # BUG: should be u["email"]
            u["email"],      # BUG: should be u["username"]
            u["created_at"],
        ])

    return output.getvalue()


def parse_csv(csv_text: str) -> list[dict]:
    """Parse CSV text back into list of dicts."""
    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)
