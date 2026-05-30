import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from accidentes.repositories import PinotRepository

print("Querying max date in Pinot:")
try:
    res = PinotRepository.execute_query("SELECT MAX(anio) FROM fechas")
    print("Max Year:", res)
    res2 = PinotRepository.execute_query("SELECT fechacompleta FROM fechas WHERE anio = 2023 LIMIT 5")
    print("Dates in 2023:", res2)
except Exception as e:
    print("Error:", e)
