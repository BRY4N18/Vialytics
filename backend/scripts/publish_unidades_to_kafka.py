"""
Publica las unidades de emergencia iniciales al topic unidadesemergencia_topic
para que Pinot las ingiera via Kafka.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

import time
import logging

from accidentes.shared.repositories import KafkaRepository

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

UNIDADES = [
    {"idunidademergencia": 1, "unidademergencia": "Alfa 1", "tipounidademergencia": "AMBULANCIA", "estadounidad": "En base", "activo": True},
    {"idunidademergencia": 2, "unidademergencia": "Alfa 2", "tipounidademergencia": "AMBULANCIA", "estadounidad": "En base", "activo": True},
    {"idunidademergencia": 3, "unidademergencia": "Rescate 1", "tipounidademergencia": "BOMBEROS", "estadounidad": "En base", "activo": True},
    {"idunidademergencia": 4, "unidademergencia": "Bomberos 4", "tipounidademergencia": "BOMBEROS", "estadounidad": "En base", "activo": True},
    {"idunidademergencia": 5, "unidademergencia": "ATM Movil 10", "tipounidademergencia": "TRANSITO", "estadounidad": "En base", "activo": True},
    {"idunidademergencia": 6, "unidademergencia": "ATM Movil 12", "tipounidademergencia": "TRANSITO", "estadounidad": "En base", "activo": True},
    {"idunidademergencia": 7, "unidademergencia": "Grua 1", "tipounidademergencia": "GRUA", "estadounidad": "En base", "activo": True},
    {"idunidademergencia": 8, "unidademergencia": "Grua 2", "tipounidademergencia": "GRUA", "estadounidad": "En base", "activo": True},
]

def main():
    ahora_ms = int(time.time() * 1000)
    kafka = KafkaRepository()
    exito = 0
    fallo = 0

    for u in UNIDADES:
        u["fecha_actualizacion"] = ahora_ms
        try:
            ok = kafka.enviar_mensaje(
                topic="unidadesemergencia_topic",
                clave_primaria=u["idunidademergencia"],
                datos_json=u,
                operacion="INSERT",
            )
            if ok:
                exito += 1
                logger.info("Publicada unidad %s (%s)", u["unidademergencia"], u["tipounidademergencia"])
            else:
                fallo += 1
                logger.warning("Fallo al publicar unidad %s", u["unidademergencia"])
        except Exception as e:
            fallo += 1
            logger.error("Error publicando unidad %s: %s", u["idunidademergencia"], e)

    logger.info("Resumen: %d publicadas, %d fallos", exito, fallo)


if __name__ == "__main__":
    main()
