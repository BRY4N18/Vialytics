"""
Publica los estados de unidades de emergencia al topic estadosunidadesemergencias_topic
para que Pinot los ingiera via Kafka.
"""
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from accidentes.shared.repositories import KafkaRepository

ESTADOS = {
    1: "En base",
    2: "En camino",
    3: "En escena",
    4: "En traslado",
    5: "Regreso",
    6: "Disponible",
}

def main():
    ahora_ms = int(time.time() * 1000)
    kafka = KafkaRepository()
    exito = 0
    fallo = 0

    for e_id, e_name in ESTADOS.items():
        payload = {
            "idestadounidad": e_id,
            "estadounidad": e_name,
            "activo": True,
            "fecha_actualizacion": ahora_ms,
        }
        try:
            ok = kafka.enviar_mensaje(
                topic="estadosunidadesemergencias_topic",
                clave_primaria=e_id,
                datos_json=payload,
                operacion="INSERT",
            )
            if ok:
                exito += 1
                print(f"  Publicado estado ID {e_id} ('{e_name}'): OK")
            else:
                fallo += 1
                print(f"  Fallo al publicar estado ID {e_id} ('{e_name}')")
        except Exception as e:
            fallo += 1
            print(f"  Error publicando estado ID {e_id}: {e}")

    print(f"Resumen: {exito} publicados, {fallo} fallos")


if __name__ == "__main__":
    main()
