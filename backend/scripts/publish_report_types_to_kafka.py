import os
import sys
import django
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accidentes.repositories import KafkaRepository

def publish_report_types():
    print("Publishing official report channels strictly to Pinot (via Kafka) - No SQLite...")
    kafka = KafkaRepository()
    ahora_ms = int(time.time() * 1000)

    report_types = {
        1: "Llamada de emergencia 911",
        2: "Camara de seguridad/ transito"
    }

    # Publish to Kafka topic 'tiposreportados_topic' for Pinot
    for r_id, r_name in report_types.items():
        payload = {
            "idtiporeportado": r_id,
            "tiporeportado": r_name,
            "activo": True,
            "fecha_actualizacion": ahora_ms
        }
        res = kafka.enviar_mensaje(
            topic="tiposreportados_topic",
            clave_primaria=r_id,
            datos_json=payload,
            operacion="INSERT"
        )
        print(f"  [Kafka] Published report type ID {r_id} ('{r_name}') to topic: {res}")

    print("\nSuccess! Report channels published strictly to Apache Pinot via Kafka.")

if __name__ == "__main__":
    publish_report_types()
