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
