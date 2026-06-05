"""Tests for context-aware translation."""
import json
from pathlib import Path

def test_board_is_kanban():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    for v in tgt.values():
        if '委员会' in v:
            assert False, "board should not be 委员会"
