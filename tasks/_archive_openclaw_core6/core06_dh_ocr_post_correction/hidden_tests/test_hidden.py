from pathlib import Path
def test_no_digit_substitutions_remaining():
    text = (Path('/workspace/output/corrected_ocr/letter_001.txt')).read_text()
    # Common patterns that should be fixed
    assert 'Pr0fess0r' not in text
    assert 'd0cum3nts' not in text
def test_period_dates_preserved():
    text = (Path('/workspace/output/corrected_ocr/letter_001.txt')).read_text()
    assert '1880' in text or '1895' in text
