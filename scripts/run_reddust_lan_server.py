#!/usr/bin/env python3
"""Start the Red Dust LAN HTTP server for remote-agent smoke tests."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from openclaw.reddust.lan_server import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
