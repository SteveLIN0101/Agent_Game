import json
def test_japanese_uses_kana():
    with open('/workspace/output/strings_ja.json') as f:
        ja = json.load(f)
    text = json.dumps(ja, ensure_ascii=False)
    # Should contain Japanese characters
    assert any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff' for c in text)
