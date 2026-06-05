import csv
def test_entities_normalized():
    with open('/workspace/output/corpus_metadata.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        assert r['sender'] in ['Liang Qichao','Hu Shi','Chen Duxiu','Cai Yuanpei','unknown']
        assert r['recipient'] in ['Liang Qichao','Hu Shi','Chen Duxiu','Cai Yuanpei','unknown']
