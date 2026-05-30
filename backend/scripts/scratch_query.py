import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accidentes.repositories import PinotRepository

def run_q(sql):
    print(f"\nQuery: {sql}")
    try:
        res = PinotRepository.execute_query(sql)
        print(f"Result count: {len(res)}")
        for r in res[:5]:
            print(r)
    except Exception as e:
        print("Error:", e)

run_q("SELECT idpais, pais FROM paises LIMIT 5")
run_q("SELECT idestado, estado, pais FROM estados LIMIT 5")
run_q("SELECT idcondado, condado, estado FROM condados LIMIT 5")
run_q("SELECT idciudad, ciudad, condado FROM ciudades LIMIT 5")
run_q("SELECT idcalle, calle, ciudad FROM calles LIMIT 5")
run_q("SELECT idestadoclima, condicionclima FROM estadoclima LIMIT 5")
