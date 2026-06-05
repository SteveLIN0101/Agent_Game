import csv
def test_peking_normalized_to_beijing():
    with open('/workspace/output/extracted_places.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    # Peking mention should map to Beijing
    peking_rows = [r for r in rows if 'Peking' in r.get('mention','')]
    for r in peking_rows:
        assert r.get('canonical_place')=='Beijing', f"Peking should normalize to Beijing"
def test_nanking_normalized():
    with open('/workspace/output/extracted_places.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    nanking = [r for r in rows if 'Nanking' in r.get('mention','')]
    for r in nanking:
        assert r.get('canonical_place')=='Nanjing'
