"""Tests for advanced OCR correction."""
from pathlib import Path

def test_output_exists():
    assert (Path('/workspace/output/corrected_ocr/letter_001.txt')).exists()

def test_common_errors_fixed():
    text = (Path('/workspace/output/corrected_ocr/letter_001.txt')).read_text()
    assert 'Dear' in text, "0→O fix failed"
    assert 'university' in text, "1→i fix failed"
    assert 'documents' in text, "3→e fix failed"

def test_dictionary_words_present():
    text = (Path('/workspace/output/corrected_ocr/letter_001.txt')).read_text().lower()
    assert 'professor' in text
    assert 'archive' in text
