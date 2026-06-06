import time
import logging
from typing import Any, Dict, List

from accidentes.shared.repositories import BaseWriteRepository, KafkaRepository, PinotRepository

logger = logging.getLogger(__name__)


class DespachoReadRepository:

    @staticmethod
    def find_by_accidente(accidente_id: str) -> List[Dict[str, Any]]:
        safe = PinotRepository.escape_sql_str(accidente_id)
        return PinotRepository.execute_query(
            f"SELECT iddespacho, idunidademergencia, fechahoradespacho, "
            f"fechahorallegada FROM despachos "
            f"WHERE idaccidente = '{safe}'"
        )


class DespachoWriteRepository(BaseWriteRepository):
    topic = "despachos_topic"
    primary_key_field = "iddespacho"


class UnidadEmergenciaWriteRepository(BaseWriteRepository):
    topic = "unidadesemergencia_topic"
    primary_key_field = "idunidademergencia"


class AccidenteInfoReadRepository:

    @staticmethod
    def find_by_id(accidente_id: str) -> Dict[str, Any]:
        safe = PinotRepository.escape_sql_str(accidente_id)
        rows = PinotRepository.execute_query(
            f"SELECT idaccidente, numheridos, numvehiculos "
            f"FROM accidentes "
            f"WHERE idaccidente = '{safe}' LIMIT 1"
        )
        return rows[0] if rows else {}


class NotificacionWriteRepository(BaseWriteRepository):
    topic = "notificacionesdespachos_topic"
    primary_key_field = "idnotificaciondespacho"
