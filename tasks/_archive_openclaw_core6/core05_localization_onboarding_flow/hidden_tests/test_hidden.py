import json
def test_consistent_terminology():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    text = json.dumps(tgt, ensure_ascii=False)
    # workspace should be consistently translated
    assert '工作区' in text
