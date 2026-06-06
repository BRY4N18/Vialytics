import requests

for table in ["conductoresaccidentes", "accidentes"]:
    print(f"\n=== {table} ===")
    r = requests.get(f"http://localhost:9000/tables/{table}/schema", timeout=5)
    data = r.json()
    for spec_type in ["dimensionFieldSpecs", "metricFieldSpecs", "dateTimeFieldSpecs"]:
        for field in data.get(spec_type, []):
            print(f'  {field["name"]:40s} {field["dataType"]:15s} {field["fieldType"]}')
