import time
import logging
from typing import Any, Dict, List

from accidentes.shared.repositories import BaseWriteRepository, PinotRepository

logger = logging.getLogger(__name__)


class UnidadEmergenciaReadRepository:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idunidademergencia, estadounidad, fecha_actualizacion "
            "FROM unidadesemergencia"
        )


class UnidadEmergenciaWriteRepository(BaseWriteRepository):
    topic = "unidadesemergencia_topic"
    primary_key_field = "idunidademergencia"


class UnidadEstadoHistorialReadRepository:

    @staticmethod
    def get_ultimo_estado(unidad_id: int) -> str | None:
        rows = PinotRepository.execute_query(
            "SELECT estadonuevo FROM historialesestadosunidadesemergencias "
            "WHERE idunidademergencia = " + str(unidad_id) + " "
            "ORDER BY fecha_actualizacion DESC LIMIT 1"
        )
        if rows and rows[0].get("estadonuevo"):
            return str(rows[0]["estadonuevo"])
        return None

    @staticmethod
    def get_max_id() -> int:
        rows = PinotRepository.execute_query(
            "SELECT MAX(idhistorial) AS max_id FROM historialesestadosunidadesemergencias"
        )
        if rows and rows[0].get("max_id") is not None:
            return int(rows[0]["max_id"])
        return 0


class UnidadEstadoHistorialWriteRepository(BaseWriteRepository):
    topic = "historialesestadosunidadesemergencias_topic"
    primary_key_field = "idhistorial"
