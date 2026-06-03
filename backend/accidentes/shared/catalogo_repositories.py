import logging
from typing import Any, Dict, List

from accidentes.shared.repositories import PinotRepository

logger = logging.getLogger(__name__)


class TipoReportadoCatalogoRepository:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idtiporeportado, tiporeportado "
            "FROM tiposreportados WHERE activo = true LIMIT 50"
        )


class TipoEstadoCatalogoRepository:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idtipoestadoincidente, tipoestadoincidente "
            "FROM tiposestadosincidentes WHERE activo = true LIMIT 100"
        )


class PaisCatalogoRepository:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idpais, pais FROM paises WHERE activo = true LIMIT 100"
        )


class EstadoCatalogoRepository:

    @staticmethod
    def get_all(pais: str = "") -> List[Dict[str, Any]]:
        if pais:
            safe = PinotRepository.escape_sql_str(pais)
            return PinotRepository.execute_query(
                f"SELECT idestado, estado, pais FROM estados "
                f"WHERE activo = true AND pais = '{safe}' LIMIT 100"
            )
        return PinotRepository.execute_query(
            "SELECT idestado, estado, pais FROM estados "
            "WHERE activo = true LIMIT 100"
        )


class CondadoCatalogoRepository:

    @staticmethod
    def get_all(estado: str = "") -> List[Dict[str, Any]]:
        if estado:
            safe = PinotRepository.escape_sql_str(estado)
            return PinotRepository.execute_query(
                f"SELECT idcondado, condado, estado FROM condados "
                f"WHERE activo = true AND estado = '{safe}' LIMIT 200"
            )
        return PinotRepository.execute_query(
            "SELECT idcondado, condado, estado FROM condados "
            "WHERE activo = true LIMIT 200"
        )


class CiudadCatalogoRepository:

    @staticmethod
    def get_all(condado: str = "") -> List[Dict[str, Any]]:
        if condado:
            safe = PinotRepository.escape_sql_str(condado)
            return PinotRepository.execute_query(
                f"SELECT idciudad, ciudad, condado FROM ciudades "
                f"WHERE activo = true AND condado = '{safe}' LIMIT 500"
            )
        return PinotRepository.execute_query(
            "SELECT idciudad, ciudad, condado FROM ciudades "
            "WHERE activo = true LIMIT 500"
        )


class CalleCatalogoRepository:

    @staticmethod
    def get_all(ciudad: str = "") -> List[Dict[str, Any]]:
        if ciudad:
            safe = PinotRepository.escape_sql_str(ciudad)
            return PinotRepository.execute_query(
                f"SELECT idcalle, calle, ciudad FROM calles "
                f"WHERE activo = true AND ciudad = '{safe}' LIMIT 1000"
            )
        return PinotRepository.execute_query(
            "SELECT idcalle, calle, ciudad FROM calles "
            "WHERE activo = true LIMIT 1000"
        )


class ClimaCatalogoRepository:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idestadoclima, condicionclima, direccionviento, temperaturaf, "
            "sensaciontermicaf, humedadporcentaje, presionpulgadas, visibilidadmillas, "
            "velocidadvientomph, precipitacionpulgadas "
            "FROM estadoclima WHERE activo = true LIMIT 100"
        )


class ElementoFisicoCatalogoRepository:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idelementofisico, cercacruce, cercasemaforo, cercaparada, "
            "cercaestacion, cercabache, cercaviatren "
            "FROM elementosfisicos WHERE activo = true LIMIT 100"
        )


class PeriodoDiaCatalogoRepository:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT idperiododia, amaneceranochecer, crepusculocivil, "
            "crepusculonautico, crepusculoastronomico "
            "FROM periodosdias WHERE activo = true LIMIT 100"
        )


_UNIDADES_CATALOGO = [
    {"idunidademergencia": 1, "unidademergencia": "Alfa 1", "tipounidademergencia": "AMBULANCIA", "estadounidad": "EN_BASE", "activo": True},
    {"idunidademergencia": 2, "unidademergencia": "Alfa 2", "tipounidademergencia": "AMBULANCIA", "estadounidad": "EN_BASE", "activo": True},
    {"idunidademergencia": 3, "unidademergencia": "Rescate 1", "tipounidademergencia": "BOMBEROS", "estadounidad": "EN_BASE", "activo": True},
    {"idunidademergencia": 4, "unidademergencia": "Bomberos 4", "tipounidademergencia": "BOMBEROS", "estadounidad": "EN_BASE", "activo": True},
    {"idunidademergencia": 5, "unidademergencia": "ATM Movil 10", "tipounidademergencia": "TRANSITO", "estadounidad": "EN_BASE", "activo": True},
    {"idunidademergencia": 6, "unidademergencia": "ATM Movil 12", "tipounidademergencia": "TRANSITO", "estadounidad": "EN_BASE", "activo": True},
    {"idunidademergencia": 7, "unidademergencia": "Patrulla 105", "tipounidademergencia": "POLICIA", "estadounidad": "EN_BASE", "activo": True},
    {"idunidademergencia": 8, "unidademergencia": "Patrulla 109", "tipounidademergencia": "POLICIA", "estadounidad": "EN_BASE", "activo": True},
]


class UnidadEmergenciaCatalogoRepository:

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        rows = PinotRepository.execute_query(
            "SELECT idunidademergencia, unidademergencia, tipounidademergencia, "
            "estadounidad FROM unidadesemergencia WHERE activo = true LIMIT 100"
        )
        if rows:
            return rows
        logger.warning("Error querying unidades from Pinot, using fallback")
        return _UNIDADES_CATALOGO

    @staticmethod
    def get_info_map() -> Dict[int, tuple]:
        return {u["idunidademergencia"]: (u["unidademergencia"], u["tipounidademergencia"]) for u in _UNIDADES_CATALOGO}
