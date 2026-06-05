import csv
def test_hu_shi_variants_normalized():
    with open('/workspace/output/normalized_entities.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    hu_rows = [r for r in rows if 'Hu Shi' in r.get('canonical_name','') or 'Hu Shi' in r.get('extracted_name','')]
    assert len(hu_rows) >= 2, "Hu Shi and Hu Shih should both be matched"
def test_unknown_flagged():
    with open('/workspace/output/normalized_entities.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    unknown = [r for r in rows if 'Unknown' in str(r.values())]
    assert len(unknown) > 0, "Unknown entities should be flagged"
