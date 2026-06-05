"""File reader with config parsing."""


def read_config_file(path: str) -> dict[str, str]:
    """Read a key=value config file and return a dict.

    BUG: Missing encoding='utf-8' — crashes on non-ASCII characters.
    """
    result = {}
    with open(path) as f:  # BUG: should be open(path, encoding='utf-8')
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                result[key.strip()] = value.strip()
    return result


def read_text_file(path: str) -> str:
    """Read entire text file contents."""
    with open(path) as f:  # BUG: missing encoding='utf-8'
        return f.read()
