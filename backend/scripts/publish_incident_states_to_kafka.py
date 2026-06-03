import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from accidentes.shared.repositories import KafkaRepository

def publish_states():
    print("Publishing official incident states to Kafka / Pinot...")
    kafka = KafkaRepository()
    ahora_ms = int(time.time() * 1000)

    desired_states = {
        1: "Reportado",
        2: "Asignado",
        3: "En Escena",
        4: "Despejado",
        5: "Archivado"
    }

    print("Publishing to Kafka topic 'tiposestadosincidentes_topic'...")
    for s_id, s_name in desired_states.items():
        state_payload = {
            "idtipoestadoincidente": s_id,
            "tipoestadoincidente": s_name,
            "activo": True,
            "fecha_actualizacion": ahora_ms
        }
        res = kafka.enviar_mensaje(
            topic="tiposestadosincidentes_topic",
            clave_primaria=s_id,
            datos_json=state_payload,
            operacion="INSERT"
        )
        print(f"  [Kafka] Published state ID {s_id} ('{s_name}'): {res}")

    print("\nSuccess! States published to Apache Pinot via Kafka.")

if __name__ == "__main__":
    publish_states()
