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
