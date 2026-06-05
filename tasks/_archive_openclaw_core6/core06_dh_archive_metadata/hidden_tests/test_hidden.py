import csv
def test_entities_normalized():
    with open('/workspace/output/metadata.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if r['sender']!='unknown':
            assert r['sender'] in ['Cai Yuanpei','Hu Shi','Chen Duxiu']
