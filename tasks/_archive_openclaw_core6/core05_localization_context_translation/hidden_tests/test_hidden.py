import json
def test_card_is_kapian():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    text = json.dumps(tgt, ensure_ascii=False)
    assert '银行卡' not in text, "card should be 卡片 not 银行卡"
def test_channel_is_pindao():
    with open('/workspace/output/strings_zh.json') as f:
        tgt = json.load(f)
    text = json.dumps(tgt, ensure_ascii=False)
    assert '渠道' not in text, "channel should be 频道 not 渠道"
