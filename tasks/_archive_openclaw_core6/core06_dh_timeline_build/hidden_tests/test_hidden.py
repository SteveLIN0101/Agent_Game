import csv
def test_five_events():
    with open('/workspace/output/timeline.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows)==5
def test_evidence_column():
    with open('/workspace/output/evidence_table.md') as f:
        text = f.read()
    assert 'note_' in text or 'note' in text.lower()
