import time
import logging
from typing import Any, Dict, List

from accidentes.shared.repositories import BaseWriteRepository, PinotRepository

logger = logging.getLogger(__name__)


class RetiroReadRepository:

    @staticmethod
    def find_by_unidad(unidad_id: int) -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            f"SELECT d.iddespacho, d.idaccidente, d.idunidademergencia, "
            f"d.fechahoradespacho, d.fechahorallegada, d.activo "
            f"FROM despachos d "
            f"WHERE d.idunidademergencia = {int(unidad_id)} "
            f"ORDER BY d.fechahoradespacho DESC LIMIT 50"
        )

    @staticmethod
    def find_by_id(retiro_id: int) -> Dict[str, Any]:
        rows = PinotRepository.execute_query(
            f"SELECT d.iddespacho, d.idaccidente, d.idunidademergencia, "
            f"d.fechahoradespacho, d.fechahorallegada, d.activo "
            f"FROM despachos d "
            f"WHERE d.iddespacho = {int(retiro_id)} LIMIT 1"
        )
        return rows[0] if rows else {}

    @staticmethod
    def find_pendientes() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            f"SELECT d.iddespacho, d.idaccidente, d.idunidademergencia, "
            f"d.fechahoradespacho, d.fechahorallegada, d.activo "
            f"FROM despachos d "
            f"WHERE d.fechahorallegada IS NULL OR d.fechahorallegada = 0 "
            f"ORDER BY d.fechahoradespacho DESC LIMIT 50"
        )


class RetiroWriteRepository(BaseWriteRepository):
    topic = "despachos_topic"
    primary_key_field = "iddespacho"


class EvidenciaFotoWriteRepository(BaseWriteRepository):
    topic = "evidenciasfotos_topic"
    primary_key_field = "idevidenciafoto"
