import json
def test_version_placeholder_fixed():
    with open('/workspace/output/strings_zh_fixed.json') as f:
        tgt = json.load(f)
    assert '{version}' in tgt.get('about.version',''), "Placeholder should be {version}"
def test_missing_key_restored():
    with open('/workspace/output/strings_zh_fixed.json') as f:
        tgt = json.load(f)
    assert 'user.settings' in tgt
