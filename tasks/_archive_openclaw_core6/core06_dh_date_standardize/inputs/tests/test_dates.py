"""Visible tests for date standardization."""
import csv
from pathlib import Path
import re

WORKSPACE = Path('/workspace')
DATA_DIR = WORKSPACE / 'data'
OUTPUT_DIR = WORKSPACE / 'output'


def test_input_exists():
    assert (DATA_DIR / 'dates.csv').exists(), "data/dates.csv not found"


def test_output_exists():
    assert (OUTPUT_DIR / 'standardized_dates.csv').exists(), "output/standardized_dates.csv not found"


def test_report_exists():
    assert (OUTPUT_DIR / 'report.md').exists(), "output/report.md not found"


def test_output_has_correct_columns():
    with open(OUTPUT_DIR / 'standardized_dates.csv', newline='') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
    for col in ['id', 'event', 'date', 'source']:
        assert col in columns, f"Missing column: {col}"


def test_all_dates_are_yyyy_mm_dd():
    """All dates in output must be YYYY-MM-DD format."""
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    with open(OUTPUT_DIR / 'standardized_dates.csv', newline='') as f:
        reader = csv.DictReader(f)
        issues = []
        for row in reader:
            if not date_pattern.match(row['date']):
                issues.append(f"{row['id']}: {row['date']}")
    assert not issues, f"Non-standard dates found:\n" + "\n".join(issues)


def test_row_count_matches():
    """Output should have same number of rows as input."""
    with open(DATA_DIR / 'dates.csv', newline='') as f:
        input_count = sum(1 for _ in f) - 1
    with open(OUTPUT_DIR / 'standardized_dates.csv', newline='') as f:
        output_count = sum(1 for _ in f) - 1
    assert input_count == output_count, f"Row count mismatch: {input_count} vs {output_count}"
