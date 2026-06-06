import requests

for table in ["vehiculos", "conductoresaccidentes"]:
    print(f"\n=== {table} SCHEMA ===")
    r = requests.get(f"http://localhost:9000/tables/{table}/schema", timeout=5)
    data = r.json()
    for spec_type in ["dimensionFieldSpecs", "metricFieldSpecs", "dateTimeFieldSpecs"]:
        for field in data.get(spec_type, []):
            print(f'  {field["name"]:40s} {field["dataType"]:15s} {field["fieldType"]}')
    
    print(f"\n  --- {table} DATA (first 5) ---")
    r2 = requests.post("http://localhost:9000/sql", json={"sql": f"SELECT * FROM {table} LIMIT 5"}, timeout=5)
    data2 = r2.json()
    if "resultTable" in data2 and data2["resultTable"].get("rows"):
        cols = data2["resultTable"]["dataSchema"]["columnNames"]
        for row in data2["resultTable"]["rows"]:
            print(" ", dict(zip(cols, row)))
