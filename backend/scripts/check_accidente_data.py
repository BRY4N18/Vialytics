import requests

r = requests.post("http://localhost:9000/sql", json={"sql": "SELECT idaccidente, descripcion, latitudinicio, longitudinicio, numheridos, numvehiculos, numfallecidos FROM accidentes ORDER BY fecha_actualizacion DESC LIMIT 5"}, timeout=5)
data = r.json()
if "resultTable" in data and data["resultTable"].get("rows"):
    cols = data["resultTable"]["dataSchema"]["columnNames"]
    for row in data["resultTable"]["rows"]:
        print(dict(zip(cols, row)))
else:
    print(data)
