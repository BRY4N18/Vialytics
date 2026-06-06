import time
import logging
from typing import Any, Dict, List

from accidentes.shared.repositories import BaseWriteRepository, PinotRepository

logger = logging.getLogger(__name__)


class UnidadEmergenciaReadRepository:

    @staticmethod
    def get_all(activo: bool = None) -> List[Dict[str, Any]]:
        sql = "SELECT idunidademergencia, unidademergencia, tipounidademergencia, activo FROM unidadesemergencia"
        where = []
        if activo is not None:
            where.append(f"activo = {'true' if activo else 'false'}")
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " LIMIT 100"
        return PinotRepository.execute_query(sql)

    @staticmethod
    def get_by_id(unidad_id: int) -> Dict[str, Any] | None:
        rows = PinotRepository.execute_query(
            "SELECT idunidademergencia, unidademergencia, tipounidademergencia, "
            "activo FROM unidadesemergencia "
            "WHERE idunidademergencia = " + str(unidad_id) + " LIMIT 1"
        )
        if rows:
            return rows[0]
        return None

    @staticmethod
    def get_max_id() -> int:
        rows = PinotRepository.execute_query(
            "SELECT MAX(idunidademergencia) AS max_id FROM unidadesemergencia"
        )
        if rows and rows[0].get("max_id") is not None:
            return int(rows[0]["max_id"])
        return 0


class UnidadEmergenciaWriteRepository(BaseWriteRepository):
    topic = "unidadesemergencia_topic"
    primary_key_field = "idunidademergencia"
