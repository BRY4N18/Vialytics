import requests

# Check what ids exist in conductoresaccidentes
r = requests.post("http://localhost:9000/sql", json={"sql": "SELECT DISTINCT idaccidente FROM conductoresaccidentes LIMIT 20"}, timeout=5)
data = r.json()
if "resultTable" in data and data["resultTable"].get("rows"):
    cols = data["resultTable"]["dataSchema"]["columnNames"]
    print("conductoresaccidentes.idaccidente values:")
    for row in data["resultTable"]["rows"]:
        print(" ", dict(zip(cols, row)))
else:
    print("result:", data)
