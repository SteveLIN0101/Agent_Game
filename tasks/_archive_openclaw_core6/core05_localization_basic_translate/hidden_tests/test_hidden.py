"""Hidden tests for basic translation."""
import json
from pathlib import Path

WORKSPACE = Path('/workspace')


def load_target():
    with open(WORKSPACE / 'output/strings_zh.json') as f:
        return json.load(f)


def test_glossary_compliance():
    """All glossary terms must use the specified translation."""
    import csv
    glossary = {}
    with open(WORKSPACE / 'reference/glossary.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            glossary[row['source']] = row['target']
    
    tgt = load_target()
    # Check that forbidden translations are not used
    text = json.dumps(tgt, ensure_ascii=False)
    assert '空间站' not in text, "workspace must not be translated as 空间站"
    assert '开票系统' not in text, "billing must not be translated as 开票系统"
    assert '模版' not in text, "template must not be translated as 模版"


def test_billing_translated():
    tgt = load_target()
    billing_value = tgt.get('nav.billing', '')
    assert '账单' in billing_value or '计费' in billing_value, \
        f"billing should be translated correctly, got: {billing_value}"


def test_qa_report_has_checks():
    with open(WORKSPACE / 'output/localization_qa.json') as f:
        qa = json.load(f)
    assert 'checked_placeholders' in qa or 'placeholder' in str(qa).lower(), \
        "QA report should mention placeholder checks"
    assert 'checked_glossary' in qa or 'glossary' in str(qa).lower(), \
        "QA report should mention glossary checks"
