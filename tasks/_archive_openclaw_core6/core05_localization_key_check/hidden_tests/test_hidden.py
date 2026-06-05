"""Hidden tests for key check."""
import json
def test_exact_key_count():
    with open('/workspace/source/strings_en.json') as f: src=json.load(f)
    with open('/workspace/output/strings_zh.json') as f: tgt=json.load(f)
    assert len(src)==len(tgt), f"Key count mismatch: {len(src)} vs {len(tgt)}"
