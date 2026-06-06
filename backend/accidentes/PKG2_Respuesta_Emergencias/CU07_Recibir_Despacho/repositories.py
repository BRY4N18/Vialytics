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
            f"d.fechahoradespacho, d.fechahorallegada, "
            f"d.activo "
            f"FROM despachos d "
            f"WHERE d.idunidademergencia = {int(unidad_id)} "
            f"ORDER BY d.fechahoradespacho DESC LIMIT 50"
        )

    @staticmethod
    def find_pendientes_by_unidad(unidad_id: int) -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            f"SELECT d.iddespacho, d.idaccidente, d.idunidademergencia, "
            f"d.fechahoradespacho, d.fechahorallegada, "
            f"d.activo "
            f"FROM despachos d "
            f"WHERE d.idunidademergencia = {int(unidad_id)} "
            f"AND (d.fechahorallegada IS NULL OR d.fechahorallegada = 0) "
            f"ORDER BY d.fechahoradespacho DESC LIMIT 50"
        )


class DespachoUnidadWriteRepository(BaseWriteRepository):
    topic = "despachos_topic"
    primary_key_field = "iddespacho"


class AccidenteInfoReadRepository:

    @staticmethod
    def find_by_id(accidente_id: str) -> Dict[str, Any]:
        safe = PinotRepository.escape_sql_str(accidente_id)
        rows = PinotRepository.execute_query(
            f"SELECT idaccidente, latitudinicio, longitudinicio, "
            f"numheridos, numfallecidos, descripcion, idseveridad "
            f"FROM accidentes "
            f"WHERE idaccidente = '{safe}' LIMIT 1"
        )
        return rows[0] if rows else {}


class AccidenteVehiculoReadRepository:

    @staticmethod
    def find_by_accidente(pinot_id: int) -> List[Dict[str, Any]]:
        try:
            return PinotRepository.execute_query(
                f"SELECT v.tipovehiculo, v.modelovehiculo, v.mercanciapeligrosa "
                f"FROM conductoresaccidentes ca "
                f"JOIN vehiculos v ON ca.idvehiculo = v.idvehiculo "
                f"WHERE ca.idaccidente = {pinot_id} AND ca.activo = true",
                use_multistage=True
            )
        except Exception as e:
            logger.warning("Error consultando vehiculos para accidente %s: %s", pinot_id, e)
            return []


class NotificacionReadRepository:

    @staticmethod
    def find_activas() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            f"SELECT idnotificaciondespacho, idaccidente, "
            f"numheridos, numvehiculos, fecha_actualizacion "
            f"FROM notificacionesdespachos "
            f"WHERE activo = true "
            f"ORDER BY fecha_actualizacion DESC LIMIT 100"
        )

    @staticmethod
    def find_by_id(notificacion_id: int) -> Dict[str, Any]:
        rows = PinotRepository.execute_query(
            f"SELECT idnotificaciondespacho, idaccidente, "
            f"numheridos, numvehiculos, fecha_actualizacion "
            f"FROM notificacionesdespachos "
            f"WHERE idnotificaciondespacho = {int(notificacion_id)} "
            f"AND activo = true LIMIT 1"
        )
        return rows[0] if rows else {}


class NotificacionWriteRepository(BaseWriteRepository):
    topic = "notificacionesdespachos_topic"
    primary_key_field = "idnotificaciondespacho"

    @classmethod
    def desactivar(cls, notificacion_id: int) -> bool:
        ahora_ms = int(time.time() * 1000)
        payload = {
            "idnotificaciondespacho": int(notificacion_id),
            "activo": False,
            "fecha_actualizacion": ahora_ms,
        }
        try:
            from accidentes.shared.repositories import KafkaRepository
            kafka = KafkaRepository()
            return kafka.enviar_mensaje(
                topic=cls.topic,
                clave_primaria=int(notificacion_id),
                datos_json=payload,
                operacion="AUDIT_INSERT",
            )
        except Exception as e:
            logger.error("Error desactivando notificacion %s: %s", notificacion_id, e)
            return False
