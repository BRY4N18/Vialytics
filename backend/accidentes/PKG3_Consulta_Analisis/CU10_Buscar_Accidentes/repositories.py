import logging
from typing import Any, Dict, List

from accidentes.shared.repositories import PinotRepository

logger = logging.getLogger(__name__)


class BusquedaCalleRepository:

    @staticmethod
    def find_by_search(term: str) -> List[int]:
        if not term:
            return []
        safe = PinotRepository.escape_sql_str(term)
        safe = safe.replace("%", "\\%").replace("_", "\\_")
        rows = PinotRepository.execute_query(
            f"SELECT idcalle FROM calles "
            f"WHERE LOWER(calle) LIKE '%{safe.lower()}%' LIMIT 100"
        )
        return [r["idcalle"] for r in rows if r.get("idcalle") is not None]


class BusquedaCiudadRepository:

    @staticmethod
    def find_by_search(term: str) -> List[int]:
        if not term:
            return []
        safe = PinotRepository.escape_sql_str(term)
        safe = safe.replace("%", "\\%").replace("_", "\\_")
        rows = PinotRepository.execute_query(
            f"SELECT idciudad FROM ciudades "
            f"WHERE LOWER(ciudad) LIKE '%{safe.lower()}%' LIMIT 100"
        )
        return [r["idciudad"] for r in rows if r.get("idciudad") is not None]


class VehiculoBusquedaRepository:

    @staticmethod
    def find_by_search(term: str) -> List[int]:
        if not term:
            return []
        safe = PinotRepository.escape_sql_str(term)
        safe = safe.replace("%", "\\%").replace("_", "\\_")
        rows = PinotRepository.execute_query(
            f"SELECT idvehiculo FROM vehiculos WHERE "
            f"LOWER(modelovehiculo) LIKE '%{safe.lower()}%' "
            f"OR LOWER(tipovehiculo) LIKE '%{safe.lower()}%' "
            f"LIMIT 500"
        )
        return [r["idvehiculo"] for r in rows if r.get("idvehiculo") is not None]


class ConductorAccidenteBusquedaRepository:

    @staticmethod
    def find_accidente_ids_by_vehiculos(vehiculo_ids: List[int]) -> List[str]:
        if not vehiculo_ids:
            return []
        ids_str = ", ".join(str(v) for v in vehiculo_ids)
        rows = PinotRepository.execute_query(
            f"SELECT DISTINCT idaccidente FROM conductoresaccidentes "
            f"WHERE idvehiculo IN ({ids_str}) LIMIT 500"
        )
        return [str(r["idaccidente"]) for r in rows if r.get("idaccidente") is not None]


class EstadoIncidenteRepository:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idaccidente, idtipoestadoincidente, fechahoramodificado "
            "FROM accidentestiposestadosincidentes "
            "WHERE activo = true LIMIT 100000"
        )

    @staticmethod
    def find_by_accidente_ids(accidente_ids: List[str]) -> List[Dict[str, Any]]:
        if not accidente_ids:
            return []
        ids_str = ", ".join(f"'{PinotRepository.escape_sql_str(a)}'" for a in accidente_ids)
        return PinotRepository.execute_query(
            f"SELECT idaccidente, idtipoestadoincidente, fechahoramodificado "
            f"FROM accidentestiposestadosincidentes "
            f"WHERE idaccidente IN ({ids_str}) AND activo = true LIMIT 500"
        )


class AccidenteBusquedaRepository:

    @staticmethod
    def count(where_clause: str) -> int:
        rows = PinotRepository.execute_query(
            f"SELECT count(*) FROM accidentes WHERE {where_clause}"
        )
        if rows:
            return int(rows[0].get("count(*)", 0))
        return 0

    @staticmethod
    def find_paginated(columns: str, where_clause: str,
                       page_size: int, offset: int) -> List[Dict[str, Any]]:
        query = (
            f"SELECT {columns} FROM accidentes "
            f"WHERE {where_clause} "
            f"ORDER BY fecha_actualizacion DESC "
            f"LIMIT {page_size} OFFSET {offset}"
        )
        return PinotRepository.execute_query(query)
