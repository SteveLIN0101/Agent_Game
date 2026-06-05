"""Hidden tests for date standardization."""
import csv
from pathlib import Path

OUTPUT_DIR = Path('/workspace/output')


def read_output():
    with open(OUTPUT_DIR / 'standardized_dates.csv', newline='') as f:
        return list(csv.DictReader(f))


def test_specific_dates_correct():
    rows = {r['id']: r['date'] for r in read_output()}
    assert rows.get('E001') == '1920-01-12', f"E001 expected 1920-01-12, got {rows.get('E001')}"
    assert rows.get('E002') == '1920-01-15', f"E002 expected 1920-01-15, got {rows.get('E002')}"
    assert rows.get('E005') == '1920-01-12', f"E005 expected 1920-01-12, got {rows.get('E005')}"
    assert rows.get('E006') == '1920-02-03', f"E006 expected 1920-02-03, got {rows.get('E006')}"
    assert rows.get('E008') == '1920-03-01', f"E008 (March 1920) expected 1920-03-01, got {rows.get('E008')}"
    assert rows.get('E014') == '1920-07-01', f"E014 (July 1920) expected 1920-07-01, got {rows.get('E014')}"


def test_month_names_handled():
    """January, February, March, etc. should all be correctly parsed."""
    rows = {r['id']: r['date'] for r in read_output()}
    # E001: Jan 12, 1920
    assert rows['E001'] == '1920-01-12'
    # E006: Feb 3, 1920
    assert rows['E006'] == '1920-02-03'
    # E008: March 1920
    assert rows['E008'] == '1920-03-01'
    # E010: Apr 15th, 1920
    assert rows['E010'] == '1920-04-15'
    # E012: May 30, 1920
    assert rows['E012'] == '1920-05-30'


def test_report_mentions_methods():
    report = (Path('/workspace') / 'output/report.md').read_text().lower()
    assert 'date' in report, "Report should mention date processing"
    assert 'format' in report or '格式' in report, "Report should mention format standardization"
