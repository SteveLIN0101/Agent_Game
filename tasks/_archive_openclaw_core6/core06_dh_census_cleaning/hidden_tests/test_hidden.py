import csv
def test_occupations_standardized():
    with open('/workspace/output/cleaned_census.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    occs = {r['record_id']:r.get('occupation_code','') for r in rows}
    assert occs['R001']=='teacher', f"R001: {occs['R001']}"
    assert occs['R004']=='teacher', f"R004 teachr should map to teacher: {occs['R004']}"
    assert occs['R007'] in ['unclassified',''], f"R007 empty should be unclassified"
def test_places_normalized():
    with open('/workspace/output/cleaned_census.csv',newline='') as f:
        rows = list(csv.DictReader(f))
    places = {r['record_id']:r.get('place_canonical','') for r in rows}
    assert places['R001']=='Beijing', f"Peking should be Beijing: {places['R001']}"
    assert places['R005']=='Tianjin', f"Tientsin should be Tianjin: {places['R005']}"
    assert places['R006']=='Guangzhou', f"Canton should be Guangzhou: {places['R006']}"
