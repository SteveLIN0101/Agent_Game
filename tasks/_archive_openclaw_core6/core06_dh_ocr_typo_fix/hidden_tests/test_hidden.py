from pathlib import Path
def test_all_three_corrected():
    for i in range(1,4):
        assert (Path('/workspace/output/corrected_ocr') / f'letter_{i:03d}.txt').exists()
def test_original_meaning_preserved():
    text = (Path('/workspace/output/corrected_ocr/letter_001.txt')).read_text()
    assert 'Zhang' in text
    assert '1919' in text
