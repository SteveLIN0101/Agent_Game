"""Hidden tests for glossary."""
import json
def test_billing_correct():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    billing = tgt.get('nav.billing', '')
    assert '账单' in billing or '计费' in billing, f"billing not correctly translated: {billing}"
