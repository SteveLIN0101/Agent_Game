import json
def test_zero_case_handled():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    assert tgt['msg.zero'] != tgt['msg.many'], "Zero and many should use different phrasing"
