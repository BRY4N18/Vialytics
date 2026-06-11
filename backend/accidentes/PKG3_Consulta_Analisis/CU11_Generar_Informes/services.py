import logging
from typing import Any, Dict, List, Optional

from accidentes.PKG3_Consulta_Analisis.CU11_Generar_Informes.repositories import (
    ReportePinotRepository,
    ReporteAccidenteRepository,
)

logger = logging.getLogger(__name__)


class ReporteService:

    @staticmethod
    async def ejecutar_query(sql: str) -> List[Dict[str, Any]]:
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith("SELECT") or "INTO" in sql_upper:
            logger.error(f"Rejected non-SELECT SQL: {sql[:100]}")
            return []
        return await ReportePinotRepository.execute_query(sql)

    @staticmethod
    async def obtener_accidentes_mapa(
        excluir_estados: Optional[List[str]] = None,
        severidad: Optional[int] = None,
        horas: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return await ReporteAccidenteRepository.find_all_mapa(
            excluir_estados=excluir_estados,
            severidad=severidad,
            horas=horas,
        )
