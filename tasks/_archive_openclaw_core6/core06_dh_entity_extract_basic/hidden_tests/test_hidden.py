import csv
def test_specific_sender():
    with open('/workspace/output/metadata.csv',newline='') as f:
        rows = {r['doc_id']:r for r in csv.DictReader(f)}
    assert rows['letter_001']['sender']=='Liang Qichao'
    assert rows['letter_002']['sender']=='Hu Shi'
def test_dates_correct():
    with open('/workspace/output/metadata.csv',newline='') as f:
        rows = {r['doc_id']:r for r in csv.DictReader(f)}
    assert rows['letter_001']['date']=='1919-05-04'
