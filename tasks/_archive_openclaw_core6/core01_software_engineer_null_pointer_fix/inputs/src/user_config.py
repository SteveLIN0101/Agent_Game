"""User configuration parser."""

import json
from pathlib import Path


def get_user_config(config_path: str = "config.json") -> dict:
    """Load user configuration from a JSON file.

    Returns a dict with user settings. If the config file doesn't exist,
    returns default values.

    BUG: When preferences key is missing, calling .get() on None crashes.
    """
    path = Path(config_path)
    if not path.exists():
        return {"theme": "light", "language": "en", "preferences": {}}

    with open(path) as f:
        data = json.load(f)

    # BUG: data.get("preferences") may return None if key is absent
    # The .get("notifications") call on None crashes
    prefs = data.get("preferences")
    notifications = prefs.get("notifications", True)  # BUG: AttributeError if prefs is None
    auto_save = prefs.get("auto_save", False)

    return {
        "theme": data.get("theme", "light"),
        "language": data.get("language", "en"),
        "preferences": {
            "notifications": notifications,
            "auto_save": auto_save,
        },
    }


def get_theme(config: dict) -> str:
    return config.get("theme", "light")


def get_language(config: dict) -> str:
    return config.get("language", "en")
