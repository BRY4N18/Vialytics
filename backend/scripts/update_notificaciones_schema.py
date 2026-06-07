import requests

PINOT_CONTROLLER = "http://localhost:9000"


def add_tipos_necesarios_to_schema():
    schema_name = "notificacionesdespachos"
    url = f"{PINOT_CONTROLLER}/schemas/{schema_name}"

    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        print(f"Schema {schema_name} not found ({r.status_code}), creating new...")
        schema = {
            "schemaName": schema_name,
            "dimensionFieldSpecs": [
                {"name": "idnotificaciondespacho", "dataType": "INT"},
                {"name": "idaccidente", "dataType": "INT"},
                {"name": "tipos_necesarios", "dataType": "STRING"},
                {"name": "activo", "dataType": "BOOLEAN"},
            ],
            "metricFieldSpecs": [
                {"name": "numheridos", "dataType": "INT"},
                {"name": "numvehiculos", "dataType": "INT"},
            ],
            "dateTimeFieldSpecs": [
                {
                    "name": "fecha_actualizacion",
                    "dataType": "TIMESTAMP",
                    "format": "1:MILLISECONDS:EPOCH",
                    "granularity": "1:MILLISECONDS",
                }
            ],
            "primaryKeyColumns": ["idnotificaciondespacho"],
        }
        r2 = requests.post(f"{PINOT_CONTROLLER}/schemas/", json=schema, timeout=10)
        print(f"Create schema: {r2.status_code} {r2.text[:200]}")
        return

    existing = r.json()
    dims = {d["name"] for d in existing.get("dimensionFieldSpecs", [])}

    if "tipos_necesarios" not in dims:
        existing["dimensionFieldSpecs"].append(
            {"name": "tipos_necesarios", "dataType": "STRING"}
        )
        r2 = requests.put(url, json=existing, timeout=10)
        print(f"Update schema: {r2.status_code} {r2.text[:200]}")
        if r2.status_code == 200:
            print("Field 'tipos_necesarios' added successfully.")
    else:
        print("Field 'tipos_necesarios' already exists in schema.")


if __name__ == "__main__":
    add_tipos_necesarios_to_schema()
