import requests
import json

PINOT_CONTROLLER = "http://localhost:9000"
PINOT_SQL = "http://localhost:9000/sql"

def print_sep(label):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")

def do_query(label, sql, use_multistage=False):
    print(f"\n--- {label} ---")
    payload = {"sql": sql}
    if use_multistage:
        payload["queryOptions"] = "useMultistageEngine=true;maxRowsInJoin=50000000;joinOverflowMode=BREAK"
    try:
        r = requests.post(PINOT_SQL, json=payload, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code != 200:
            print(f"Error: {r.text[:300]}")
            return []
        data = r.json()
        if "exceptions" in data and data["exceptions"]:
            print("EXCEPTION:", json.dumps(data["exceptions"], indent=2)[:500])
            return []
        if "resultTable" not in data:
            print("No resultTable in response")
            print(json.dumps(data, indent=2)[:300])
            return []
        cols = data["resultTable"]["dataSchema"]["columnNames"]
        rows = data["resultTable"]["rows"]
        print(f"Found {len(rows)} row(s)")
        for row in rows:
            print(" ", dict(zip(cols, row)))
        return [dict(zip(cols, row)) for row in rows]
    except requests.exceptions.ConnectionError:
        print("ERROR: Connection refused - Pinot controller is down?")
        return []
    except Exception as e:
        print(f"ERROR: {e}")
        return []

# 1) Check table exists
print_sep("1) VERIFICAR QUE LA TABLA EXISTE")
do_query("List all tables", "SHOW TABLES")

# 2) Check schemas
print_sep("2) VERIFICAR SCHEMA DE notificacionesdespachos")
try:
    r = requests.get(f"{PINOT_CONTROLLER}/schemas/notificacionesdespachos", timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        schema = r.json()
        dims = [d["name"] for d in schema.get("dimensionFieldSpecs", [])]
        metrics = [m["name"] for m in schema.get("metricFieldSpecs", [])]
        print(f"Dimensions: {dims}")
        print(f"Metrics: {metrics}")
        print(f"PK: {schema.get('primaryKeyColumns', [])}")
        if "tipos_necesarios" in dims:
            print("  >>> 'tipos_necesarios' SI esta en el schema")
        else:
            print("  >>> 'tipos_necesarios' NO esta en el schema")
    else:
        print(f"Schema not found or error: {r.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

# 3) Check table config
print_sep("3) VERIFICAR CONFIG DE LA TABLA")
try:
    r = requests.get(f"{PINOT_CONTROLLER}/tables/notificacionesdespachos", timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        tbl = r.json()
        ttype = tbl.get("tableType", "N/A")
        stream_cfg = tbl.get("tableIndexConfig", {}).get("streamConfigs", {})
        topic = stream_cfg.get("stream.kafka.topic.name", "N/A")
        broker = stream_cfg.get("stream.kafka.broker.list", "N/A")
        offset = stream_cfg.get("stream.kafka.consumer.prop.auto.offset.reset", "N/A")
        print(f"  Table type: {ttype}")
        print(f"  Topic: {topic}")
        print(f"  Broker: {broker}")
        print(f"  Offset reset: {offset}")
        print(f"  Upsert mode: {tbl.get('upsertConfig', {}).get('mode', 'N/A')}")
    else:
        print(f"Table not found or error: {r.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

# 4) Count active notifications
print_sep("4) CONTAR NOTIFICACIONES ACTIVAS")
do_query("COUNT activas", "SELECT COUNT(*) AS total FROM notificacionesdespachos WHERE activo = true")

# 5) Count total notifications
print_sep("5) CONTAR TOTAL NOTIFICACIONES")
do_query("COUNT total", "SELECT COUNT(*) AS total FROM notificacionesdespachos")

# 6) Query some recent notifications
print_sep("6) NOTIFICACIONES RECIENTES (activas)")
do_query("Recent activas",
    "SELECT idnotificaciondespacho, idaccidente, numheridos, numvehiculos, "
    "tipos_necesarios, fecha_actualizacion "
    "FROM notificacionesdespachos WHERE activo = true "
    "ORDER BY fecha_actualizacion DESC LIMIT 10")

# 7) Query all notifications (including inactive)
print_sep("7) ULTIMAS NOTIFICACIONES (incluso inactivas)")
do_query("Recent all",
    "SELECT idnotificaciondespacho, idaccidente, activo, fecha_actualizacion "
    "FROM notificacionesdespachos "
    "ORDER BY fecha_actualizacion DESC LIMIT 20")

# 8) Check consumer info
print_sep("8) CONSUMER INFO (tabla REALTIME)")
try:
    r = requests.get(f"{PINOT_CONTROLLER}/tables/notificacionesdespachos/metadata", timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        meta = r.json()
        print(json.dumps(meta, indent=2)[:1000])
    else:
        print(f"No metadata or error: {r.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*60)
print("  DIAGNOSTICO COMPLETADO")
print("="*60)
