"""Hidden tests for length limits."""
import json

def test_short_strings_preserved():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    # Short labels like "Save", "Cancel" should be 2-4 chars in Chinese
    for key in ['action.save', 'action.cancel', 'action.delete']:
        assert len(tgt[key]) <= 4, f"{key} too long: {len(tgt[key])} chars"
