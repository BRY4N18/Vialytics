import time
import zlib
import logging
from typing import Any, Dict, Optional

from accidentes.shared.repositories import KafkaRepository

logger = logging.getLogger(__name__)


class EstadoService:
    @staticmethod
    def _uuid_to_pinot_id(uuid_str: str) -> int:
        return zlib.crc32(uuid_str.encode('utf-8')) & 0x7FFFFFFF

    @staticmethod
    def actualizar_estado(
        accidente_id: str,
        nuevo_estado_id: int,
        nota: Optional[str],
        idusuario_id: int,
    ) -> Dict[str, Any]:
        ahora_ms = int(time.time() * 1000)
        pinot_id_accidente = EstadoService._uuid_to_pinot_id(accidente_id)
        kafka_repo = KafkaRepository()

        id_estado_rel = int(time.time() * 1000) % 1000000000
        payload_estado = {
            "idaccidentetipoestadoincidente": id_estado_rel,
            "idaccidente": pinot_id_accidente,
            "idtipoestadoincidente": nuevo_estado_id,
            "activo": True,
            "fechahoramodificado": ahora_ms,
            "fecha_actualizacion": ahora_ms
        }
        kafka_repo.enviar_mensaje(
            topic="accidentestiposestadosincidentes_topic",
            clave_primaria=id_estado_rel,
            datos_json=payload_estado,
            operacion="INSERT"
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
            kafka_repo.enviar_mensaje(
                topic="notasaccidentes_topic",
                clave_primaria=id_nota,
                datos_json=payload_nota,
                operacion="INSERT"
            )

        estado_map_nombre = {1: "ACTIVO", 2: "EN_ATENCION", 3: "EN_ATENCION", 4: "CONTROLADO", 5: "ARCHIVADO"}
        estado_nombre = estado_map_nombre.get(nuevo_estado_id, "Reportado")

        return {
            "estado": estado_nombre,
            "idaccidente": accidente_id
        }
