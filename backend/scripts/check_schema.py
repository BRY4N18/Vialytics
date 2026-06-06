import requests

for table in ["estadosunidadesemergencias", "historialesestadosunidadesemergencias"]:
    print(f"\n=== {table} ===")
    try:
        r = requests.get(f"http://localhost:9000/tables/{table}/schema", timeout=10)
        data = r.json()
        for spec_type in ["dimensionFieldSpecs", "metricFieldSpecs", "dateTimeFieldSpecs"]:
            for field in data.get(spec_type, []):
                print(f'  {field["name"]:40s} {field["dataType"]:15s} {field.get("fieldType","")}')
        print(f'  PK: {data.get("primaryKeyColumns", [])}')
    except Exception as e:
        print(f"  Error: {e}")
