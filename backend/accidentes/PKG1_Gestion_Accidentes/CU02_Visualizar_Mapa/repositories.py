import logging
from typing import Any, Dict, List, Optional

from accidentes.shared.repositories import PinotRepository

logger = logging.getLogger(__name__)


class SeveridadRepository:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idseveridad, severidad, descripcion "
            "FROM severidades WHERE activo = true LIMIT 10"
        )


class CalleRepository:

    @staticmethod
    def find_by_ciudad(ciudad: str) -> List[int]:
        safe = PinotRepository.escape_sql_str(ciudad)
        rows = PinotRepository.execute_query(
            f"SELECT idcalle FROM calles "
            f"WHERE activo = true AND ciudad = '{safe}' LIMIT 5000"
        )
        return [r["idcalle"] for r in rows if r.get("idcalle") is not None]

    @staticmethod
    def find_by_ciudades(ciudades: List[str]) -> List[int]:
        if not ciudades:
            return []
        ci_str = ", ".join(f"'{PinotRepository.escape_sql_str(c)}'" for c in ciudades)
        rows = PinotRepository.execute_query(
            f"SELECT idcalle FROM calles "
            f"WHERE activo = true AND ciudad IN ({ci_str}) LIMIT 5000"
        )
        return [r["idcalle"] for r in rows if r.get("idcalle") is not None]

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, str]:
        if not ids:
            return {}
        ids_str = ", ".join(str(i) for i in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idcalle, calle FROM calles "
            f"WHERE idcalle IN ({ids_str}) LIMIT 1000"
        )
        return {r["idcalle"]: r.get("calle", "") for r in rows}


class CiudadRepository:

    @staticmethod
    def find_by_condado(condado: str) -> List[Dict[str, Any]]:
        safe = PinotRepository.escape_sql_str(condado)
        return PinotRepository.execute_query(
            f"SELECT idciudad, ciudad FROM ciudades "
            f"WHERE activo = true AND condado = '{safe}' LIMIT 2000"
        )

    @staticmethod
    def find_by_condados(condados: List[str]) -> List[Dict[str, Any]]:
        if not condados:
            return []
        co_str = ", ".join(f"'{PinotRepository.escape_sql_str(c)}'" for c in condados)
        return PinotRepository.execute_query(
            f"SELECT idciudad, ciudad FROM ciudades "
            f"WHERE activo = true AND condado IN ({co_str}) LIMIT 2000"
        )

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, str]:
        if not ids:
            return {}
        ids_str = ", ".join(str(i) for i in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idciudad, ciudad FROM ciudades "
            f"WHERE idciudad IN ({ids_str}) LIMIT 1000"
        )
        return {r["idciudad"]: r.get("ciudad", "") for r in rows}


class CondadoRepository:

    @staticmethod
    def find_by_estado(estado: str) -> List[str]:
        safe = PinotRepository.escape_sql_str(estado)
        rows = PinotRepository.execute_query(
            f"SELECT condado FROM condados "
            f"WHERE activo = true AND estado = '{safe}' LIMIT 2000"
        )
        return [r["condado"] for r in rows if r.get("condado") is not None]

    @staticmethod
    def find_by_estados(estados: List[str]) -> List[str]:
        if not estados:
            return []
        es_str = ", ".join(f"'{PinotRepository.escape_sql_str(e)}'" for e in estados)
        rows = PinotRepository.execute_query(
            f"SELECT condado FROM condados "
            f"WHERE activo = true AND estado IN ({es_str}) LIMIT 2000"
        )
        return [r["condado"] for r in rows if r.get("condado") is not None]


class EstadoGeograficoRepository:

    @staticmethod
    def find_by_pais(pais: str) -> List[str]:
        safe = PinotRepository.escape_sql_str(pais)
        rows = PinotRepository.execute_query(
            f"SELECT estado FROM estados "
            f"WHERE activo = true AND pais = '{safe}' LIMIT 2000"
        )
        return [r["estado"] for r in rows if r.get("estado") is not None]


class FechaRepository:

    @staticmethod
    def find_by_date_range(start_str: Optional[str], end_str: Optional[str]) -> List[int]:
        query = "SELECT idfecha FROM fechas WHERE activo = true"
        if start_str:
            safe = PinotRepository.escape_sql_str(start_str)
            query += f" AND fechacompleta >= '{safe}'"
        if end_str:
            safe = PinotRepository.escape_sql_str(end_str)
            query += f" AND fechacompleta <= '{safe}'"
        query += " LIMIT 5000"
        rows = PinotRepository.execute_query(query)
        return list(set(r["idfecha"] for r in rows if r.get("idfecha") is not None))


class AccidenteMapaRepository:

    @staticmethod
    def find_all(query: str) -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(query)
