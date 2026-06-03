import time
import logging
from typing import Any, Dict, List

from accidentes.shared.repositories import BaseWriteRepository, PinotRepository

logger = logging.getLogger(__name__)


class DespachoUnidadReadRepository:

    @staticmethod
    def find_by_unidad(unidad_id: int) -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            f"SELECT d.iddespacho, d.idaccidente, d.idunidademergencia, "
            f"d.fechahoradespacho, d.fechahoraconfirmacion, d.fechahorallegada, "
            f"d.activo "
            f"FROM despachos d "
            f"WHERE d.idunidademergencia = {int(unidad_id)} "
            f"ORDER BY d.fechahoradespacho DESC LIMIT 50"
        )

    @staticmethod
    def find_pendientes_by_unidad(unidad_id: int) -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            f"SELECT d.iddespacho, d.idaccidente, d.idunidademergencia, "
            f"d.fechahoradespacho, d.fechahoraconfirmacion, d.fechahorallegada, "
            f"d.activo "
            f"FROM despachos d "
            f"WHERE d.idunidademergencia = {int(unidad_id)} "
            f"AND (d.fechahoraconfirmacion IS NULL OR d.fechahoraconfirmacion = 0) "
            f"ORDER BY d.fechahoradespacho DESC LIMIT 50"
        )


class DespachoUnidadWriteRepository(BaseWriteRepository):
    topic = "despachos_topic"
    primary_key_field = "iddespacho"

    @classmethod
    def confirmar(cls, iddespacho: int) -> bool:
        ahora_ms = int(time.time() * 1000)
        payload = {
            "iddespacho": int(iddespacho),
            "fechahoraconfirmacion": ahora_ms,
            "fecha_actualizacion": ahora_ms,
        }
        try:
            from accidentes.shared.repositories import KafkaRepository
            kafka = KafkaRepository()
            return kafka.enviar_mensaje(
                topic=cls.topic,
                clave_primaria=int(iddespacho),
                datos_json=payload,
                operacion="AUDIT_INSERT",
            )
        except Exception as e:
            logger.error("Error confirmando despacho %s: %s", iddespacho, e)
            return False

    @classmethod
    def marcar_llegada(cls, iddespacho: int) -> bool:
        ahora_ms = int(time.time() * 1000)
        payload = {
            "iddespacho": int(iddespacho),
            "fechahorallegada": ahora_ms,
            "fecha_actualizacion": ahora_ms,
        }
        try:
            from accidentes.shared.repositories import KafkaRepository
            kafka = KafkaRepository()
            return kafka.enviar_mensaje(
                topic=cls.topic,
                clave_primaria=int(iddespacho),
                datos_json=payload,
                operacion="AUDIT_INSERT",
            )
        except Exception as e:
            logger.error("Error marcando llegada despacho %s: %s", iddespacho, e)
            return False


class AccidenteInfoReadRepository:

    @staticmethod
    def find_by_id(accidente_id: str) -> Dict[str, Any]:
        safe = PinotRepository.escape_sql_str(accidente_id)
        rows = PinotRepository.execute_query(
            f"SELECT idaccidente, latitudinicio, longitudinicio, "
            f"numheridos, numfallecidos, descripcion, severidad_nivel, "
            f"estado_actual, calle_nombre, ciudad_nombre "
            f"FROM accidentes "
            f"WHERE idaccidente = '{safe}' LIMIT 1"
        )
        return rows[0] if rows else {}
