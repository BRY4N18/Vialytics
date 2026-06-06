import requests, json

PINOT_URL = "http://localhost:9000/sql"

def do_query(label, sql, use_multistage=False):
    print(f"\n=== {label} ===")
    payload = {"sql": sql}
    if use_multistage:
        payload["queryOptions"] = "useMultistageEngine=true;maxRowsInJoin=50000000;joinOverflowMode=BREAK"
    try:
        r = requests.post(PINOT_URL, json=payload, timeout=10)
        print(f"Status: {r.status_code}")
        data = r.json()
        if "resultTable" in data and data["resultTable"].get("rows"):
            cols = data["resultTable"]["dataSchema"]["columnNames"]
            rows = data["resultTable"]["rows"]
            print(f"Found {len(rows)} rows")
            for row in rows:
                print(" ", dict(zip(cols, row)))
        elif "resultTable" in data:
            print("Empty result (no rows)")
        elif "exceptions" in data and data["exceptions"]:
            print("EXCEPTION:", json.dumps(data["exceptions"], indent=2))
        else:
            print("Unexpected:", json.dumps(data, indent=2)[:500])
    except Exception as e:
        print(f"ERROR: {e}")

# Test 1: notifications query
do_query("NOTIFICACIONES",
    "SELECT idnotificaciondespacho, idaccidente, numheridos, numvehiculos, fecha_actualizacion FROM notificacionesdespachos WHERE activo = true ORDER BY fecha_actualizacion DESC LIMIT 100")

# Test 2: accident info lookup (use idseveridad instead of invalid columns)
do_query("ACCIDENTE INFO",
    "SELECT idaccidente, latitudinicio, longitudinicio, numheridos, numfallecidos, descripcion, idseveridad FROM accidentes WHERE idaccidente = '6af77c80-3522-4ad5-9690-c65a5d31ea4e' LIMIT 1")

# Test 3: vehicles join (use INT for conductoresaccidentes.idaccidente)
import zlib
uuid_ejemplo = "6af77c80-3522-4ad5-9690-c65a5d31ea4e"
pinot_id = zlib.crc32(uuid_ejemplo.encode('utf-8')) & 0x7FFFFFFF
do_query("VEHICULOS JOIN",
    f"SELECT v.tipovehiculo, v.modelovehiculo, v.mercanciapeligrosa FROM conductoresaccidentes ca JOIN vehiculos v ON ca.idvehiculo = v.idvehiculo WHERE ca.idaccidente = {pinot_id} AND ca.activo = true",
    use_multistage=True)

# Test 4: vehicles join with idaccidente=0 (edge case)
do_query("VEHICULOS JOIN id=0",
    "SELECT v.tipovehiculo, v.modelovehiculo, v.mercanciapeligrosa FROM conductoresaccidentes ca JOIN vehiculos v ON ca.idvehiculo = v.idvehiculo WHERE ca.idaccidente = 0 AND ca.activo = true",
    use_multistage=True)
