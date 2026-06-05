"""Log file parser with regex pattern matching."""

import re


def parse_log_entry(line: str) -> dict | None:
    """Parse a log line into structured data.

    Expected format: [LEVEL] [timestamp] message (key=value, ...)
    Example: [INFO] [2025-01-15 10:30:00] User login (user=alice, ip=192.168.1.1)

    BUG: The regex pattern doesn't properly escape special characters.
    """
    # BUG: square brackets [ ] are regex metacharacters that should be escaped
    # BUG: parentheses ( ) are regex metacharacters that should be escaped
    pattern = r'[(.*?)] [(.*?)] (.*?) [(.*)]'  # BUG: unescaped brackets/parens

    match = re.match(pattern, line)
    if not match:
        return None

    level = match.group(1)
    timestamp = match.group(2)
    message = match.group(3)
    kv_pairs_str = match.group(4)

    kv_pairs = {}
    for pair in kv_pairs_str.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            kv_pairs[k.strip()] = v.strip()

    return {
        "level": level,
        "timestamp": timestamp,
        "message": message,
        "data": kv_pairs,
    }


def filter_by_level(lines: list[str], level: str) -> list[dict]:
    """Filter log lines by level (INFO, WARN, ERROR)."""
    results = []
    for line in lines:
        parsed = parse_log_entry(line)
        if parsed and parsed["level"] == level:
            results.append(parsed)
    return results
