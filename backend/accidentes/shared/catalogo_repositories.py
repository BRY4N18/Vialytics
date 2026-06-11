import logging
from typing import Any, Dict, List

from accidentes.shared.repositories import PinotRepository, QueryTimeout
from accidentes.shared.cache_utils import cached_catalog, memoize
from accidentes.shared.seeds import (
    ESTADOS_UNIDAD_CATALOGO,
    TIPOS_UNIDAD_CATALOGO,
    UNIDADES_CATALOGO,
)

logger = logging.getLogger(__name__)


class TipoReportadoCatalogoRepository:

    @staticmethod
    @cached_catalog("catalogo:tiporeportado", ttl=3600)
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idtiporeportado, tiporeportado "
            "FROM tiposreportados WHERE activo = true LIMIT 50",
            timeout=QueryTimeout.CATALOGO,
        )


class TipoEstadoCatalogoRepository:

    @staticmethod
    @cached_catalog("catalogo:tipoestado", ttl=3600)
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idtipoestadoincidente, tipoestadoincidente "
            "FROM tiposestadosincidentes WHERE activo = true LIMIT 100",
            timeout=QueryTimeout.CATALOGO,
        )


class PaisCatalogoRepository:

    @staticmethod
    @cached_catalog("catalogo:pais", ttl=3600)
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idpais, pais FROM paises WHERE activo = true LIMIT 100",
            timeout=QueryTimeout.CATALOGO,
        )


class EstadoCatalogoRepository:

    @staticmethod
    @cached_catalog("catalogo:estado", ttl=1800)
    def get_all(pais: str = "") -> List[Dict[str, Any]]:
        if pais:
            safe = PinotRepository.escape_sql_str(pais)
            return PinotRepository.execute_query(
                f"SELECT idestado, estado, pais FROM estados "
                f"WHERE activo = true AND pais = '{safe}' LIMIT 100",
                timeout=QueryTimeout.CATALOGO,
            )
        return PinotRepository.execute_query(
            "SELECT idestado, estado, pais FROM estados "
            "WHERE activo = true LIMIT 100",
            timeout=QueryTimeout.CATALOGO,
        )


class CondadoCatalogoRepository:

    @staticmethod
    @cached_catalog("catalogo:condado", ttl=1800)
    def get_all(estado: str = "") -> List[Dict[str, Any]]:
        if estado:
            safe = PinotRepository.escape_sql_str(estado)
            return PinotRepository.execute_query(
                f"SELECT idcondado, condado, estado FROM condados "
                f"WHERE activo = true AND estado = '{safe}' LIMIT 200",
                timeout=QueryTimeout.CATALOGO,
            )
        return PinotRepository.execute_query(
            "SELECT idcondado, condado, estado FROM condados "
            "WHERE activo = true LIMIT 200",
            timeout=QueryTimeout.CATALOGO,
        )


class CiudadCatalogoRepository:

    @staticmethod
    @cached_catalog("catalogo:ciudad", ttl=1800)
    def get_all(condado: str = "") -> List[Dict[str, Any]]:
        if condado:
            safe = PinotRepository.escape_sql_str(condado)
            return PinotRepository.execute_query(
                f"SELECT idciudad, ciudad, condado FROM ciudades "
                f"WHERE activo = true AND condado = '{safe}' LIMIT 500",
                timeout=QueryTimeout.CATALOGO,
            )
        return PinotRepository.execute_query(
            "SELECT idciudad, ciudad, condado FROM ciudades "
            "WHERE activo = true LIMIT 500",
            timeout=QueryTimeout.CATALOGO,
        )


class CalleCatalogoRepository:

    @staticmethod
    @cached_catalog("catalogo:calle", ttl=1800)
    def get_all(ciudad: str = "") -> List[Dict[str, Any]]:
        if ciudad:
            safe = PinotRepository.escape_sql_str(ciudad)
            return PinotRepository.execute_query(
                f"SELECT idcalle, calle, ciudad FROM calles "
                f"WHERE activo = true AND ciudad = '{safe}' LIMIT 1000",
                timeout=QueryTimeout.CATALOGO,
            )
        return PinotRepository.execute_query(
            "SELECT idcalle, calle, ciudad FROM calles "
            "WHERE activo = true LIMIT 1000",
            timeout=QueryTimeout.CATALOGO,
        )


class ClimaCatalogoRepository:

    @staticmethod
    @cached_catalog("catalogo:clima", ttl=3600)
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idestadoclima, condicionclima, direccionviento, temperaturaf, "
            "sensaciontermicaf, humedadporcentaje, presionpulgadas, visibilidadmillas, "
            "velocidadvientomph, precipitacionpulgadas "
            "FROM estadoclima WHERE activo = true LIMIT 100",
            timeout=QueryTimeout.CATALOGO,
        )


class ElementoFisicoCatalogoRepository:

    @staticmethod
    @cached_catalog("catalogo:elementofisico", ttl=3600)
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idelementofisico, cercacruce, cercasemaforo, cercaparada, "
            "cercaestacion, cercabache, cercaviatren "
            "FROM elementosfisicos WHERE activo = true LIMIT 100",
            timeout=QueryTimeout.CATALOGO,
        )


class PeriodoDiaCatalogoRepository:

    @staticmethod
    @cached_catalog("catalogo:periododia", ttl=3600)
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idperiododia, amaneceranochecer, crepusculocivil, "
            "crepusculonautico, crepusculoastronomico "
            "FROM periodosdias WHERE activo = true LIMIT 100",
            timeout=QueryTimeout.CATALOGO,
        )


class EstadoUnidadCatalogoRepository:

    @staticmethod
    @cached_catalog("catalogo:estadounidad", ttl=3600)
    def get_all() -> List[Dict[str, Any]]:
        rows = PinotRepository.execute_query(
            "SELECT idestadounidad, estadounidad "
            "FROM estadosunidadesemergencias WHERE activo = true LIMIT 20",
            timeout=QueryTimeout.CATALOGO,
        )
        if rows:
            return rows
        logger.warning("Error querying estados unidad from Pinot, using fallback")
        return ESTADOS_UNIDAD_CATALOGO


class TipoUnidadCatalogoRepository:

    @staticmethod
    @memoize
    def get_all() -> List[Dict[str, Any]]:
        return TIPOS_UNIDAD_CATALOGO

    @staticmethod
    def get_nombre(id_tipo: int) -> str | None:
        for t in TIPOS_UNIDAD_CATALOGO:
            if t["idtipounidad"] == id_tipo:
                return t["tipounidad"]
        return None


class UnidadEmergenciaCatalogoRepository:

    @staticmethod
    @cached_catalog("catalogo:unidademergencia", ttl=3600)
    def get_all() -> List[Dict[str, Any]]:
        rows = PinotRepository.execute_query(
            "SELECT idunidademergencia, unidademergencia, tipounidademergencia, "
            "activo FROM unidadesemergencia WHERE activo = true LIMIT 100",
            timeout=QueryTimeout.CATALOGO,
        )
        if rows:
            return rows
        logger.warning("Error querying unidades from Pinot, using fallback")
        return UNIDADES_CATALOGO

    @staticmethod
    @cached_catalog("catalogo:unidademergencia:info_map", ttl=3600)
    def get_info_map() -> Dict[int, tuple]:
        rows = PinotRepository.execute_query(
            "SELECT idunidademergencia, unidademergencia, tipounidademergencia "
            "FROM unidadesemergencia WHERE activo = true LIMIT 100",
            timeout=QueryTimeout.CATALOGO,
        )
        if rows:
            return {u["idunidademergencia"]: (u["unidademergencia"], u["tipounidademergencia"]) for u in rows}
        logger.warning("Error querying unidades info_map from Pinot, using fallback")
        return {u["idunidademergencia"]: (u["unidademergencia"], u["tipounidademergencia"]) for u in UNIDADES_CATALOGO}
