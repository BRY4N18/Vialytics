import time
import logging
from typing import Any, Dict, Optional

from accidentes.shared.utils import uuid_to_pinot_id
from accidentes.shared.repositories import KafkaRepository

logger = logging.getLogger(__name__)


class EstadoService:
    @staticmethod
    def _enviar_kafka_seguro(kafka_repo, topic, clave, datos):
        try:
            kafka_repo.enviar_mensaje(
                topic=topic,
                clave_primaria=clave,
                datos_json=datos,
                operacion="INSERT"
            )
        except Exception as e:
            logger.warning("Error enviando a Kafka (topic=%s): %s", topic, e)

    @staticmethod
    def actualizar_estado(
        accidente_id: str,
        nuevo_estado_id: int,
        nota: Optional[str],
        idusuario_id: int,
    ) -> Dict[str, Any]:
        ahora_ms = int(time.time() * 1000)
        pinot_id_accidente = uuid_to_pinot_id(accidente_id)
        try:
            kafka_repo = KafkaRepository()
        except Exception as e:
            logger.warning("Kafka no disponible, continuando sin Kafka: %s", e)
            kafka_repo = None

        id_estado_rel = int(time.time() * 1000) % 1000000000
        payload_estado = {
            "idaccidentetipoestadoincidente": id_estado_rel,
            "idaccidente": pinot_id_accidente,
            "idtipoestadoincidente": nuevo_estado_id,
            "activo": True,
            "fechahoramodificado": ahora_ms,
            "fecha_actualizacion": ahora_ms
        }
        if kafka_repo:
            EstadoService._enviar_kafka_seguro(
                kafka_repo,
                "accidentestiposestadosincidentes_topic",
                id_estado_rel,
                payload_estado,
            )

        if nota:
            id_nota = int(time.time() * 1000) % 1000000000
            payload_nota = {
                "idnotaaccidentes": id_nota,
                "idaccidente": pinot_id_accidente,
                "idusuario": idusuario_id,
                "nota": nota,
                "tipo": True,
                "activo": True,
                "fecha_actualizacion": ahora_ms
            }
            if kafka_repo:
                EstadoService._enviar_kafka_seguro(
                    kafka_repo,
                    "notasaccidentes_topic",
                    id_nota,
                    payload_nota,
                )

        estado_map_nombre = {1: "ACTIVO", 2: "EN_ATENCION", 3: "EN_ATENCION", 4: "CONTROLADO", 5: "ARCHIVADO"}
        estado_nombre = estado_map_nombre.get(nuevo_estado_id, "Reportado")

        return {
            "estado": estado_nombre,
            "idaccidente": accidente_id
        }
