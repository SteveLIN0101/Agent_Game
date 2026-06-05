"""Hidden tests for placeholder fix."""
import json

def test_exact_placeholder_count():
    with open('/workspace/source/strings_en.json') as f:
        src = json.load(f)
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    import re
    for key in src:
        src_ph = set(re.findall(r'\{[^}]+\}', src[key]))
        tgt_ph = set(re.findall(r'\{[^}]+\}', tgt[key]))
        assert src_ph == tgt_ph, f"Placeholder mismatch in {key}: {src_ph} vs {tgt_ph}"
