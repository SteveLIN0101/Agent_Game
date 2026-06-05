"""Tests for OCR correction."""
from pathlib import Path

def test_outputs_exist():
    assert (Path('/workspace/output/corrected_ocr/letter_001.txt')).exists()
    assert (Path('/workspace/output/report.md')).exists()

def test_zero_to_o_fixed():
    text = (Path('/workspace/output/corrected_ocr/letter_001.txt')).read_text()
    # "C0lleague" should become "Colleague"
    assert 'Colleague' in text or 'colleague' in text.lower()

def test_no_digit_zero_in_words():
    text = (Path('/workspace/output/corrected_ocr/letter_001.txt')).read_text()
    # Words shouldn't have embedded digit 0
    import re
    bad = re.findall(r'[a-zA-Z]0[a-zA-Z]', text)
    assert not bad, f"Found un-corrected 0-in-words: {bad}"
