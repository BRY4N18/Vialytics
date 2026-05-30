import requests

url = "http://localhost:9000/tables"
try:
    response = requests.get(url, timeout=5)
    print("Status:", response.status_code)
    if response.status_code == 200:
        data = response.json()
        print("Tables:")
        for t in data.get("tables", []):
            print(t)
    else:
        print("Error response:", response.text)
except Exception as e:
    print("Error:", e)
