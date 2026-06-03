import time
import logging

from accidentes.shared.repositories import BaseWriteRepository, PinotRepository

logger = logging.getLogger(__name__)

DEFAULT_CLIMA_ID = 1620546972
DEFAULT_ESTACION_ID = 1


class ClimaRepository:

    @staticmethod
    def find_id_by_condicion(condicion: str) -> int:
        if not condicion:
            return DEFAULT_CLIMA_ID
        safe = PinotRepository.escape_sql_str(condicion)
        safe = safe.replace("%", "\\%").replace("_", "\\_")
        rows = PinotRepository.execute_query(
            f"SELECT idestadoclima FROM estadoclima "
            f"WHERE condicionclima LIKE '%{safe}%' LIMIT 1"
        )
        if rows:
            return int(rows[0].get("idestadoclima"))
        return DEFAULT_CLIMA_ID


class EstacionRepository:

    @staticmethod
    def find_id_by_codigo(codigo: str) -> int:
        if not codigo:
            return DEFAULT_ESTACION_ID
        safe = PinotRepository.escape_sql_str(codigo)
        rows = PinotRepository.execute_query(
            f"SELECT idreferenciaestacion FROM referenciaestacion "
            f"WHERE codigoaeropuerto = '{safe}' LIMIT 1"
        )
        if rows:
            return int(rows[0].get("idreferenciaestacion"))
        return DEFAULT_ESTACION_ID


class AccidenteReadRepository:

    @staticmethod
    def exists_by_id(accidente_id: str) -> bool:
        safe = PinotRepository.escape_sql_str(accidente_id)
        rows = PinotRepository.execute_query(
            f"SELECT idaccidente FROM accidentes "
            f"WHERE idaccidente = '{safe}' LIMIT 1"
        )
        return bool(rows)


class AccidenteWriteRepository(BaseWriteRepository):
    topic = "accidentes_topic"
    primary_key_field = "idaccidente"


class VehiculoRepository(BaseWriteRepository):
    topic = "vehiculos_topic"
    primary_key_field = "idvehiculo"


class ConductorRepository(BaseWriteRepository):
    topic = "conductores_topic"
    primary_key_field = "idconductor"


class EstadoConductorRepository(BaseWriteRepository):
    topic = "estadosconductores_topic"
    primary_key_field = "idestadoconductor"


class ConductorAccidenteRepository(BaseWriteRepository):
    topic = "conductoresaccidentes_topic"
    primary_key_field = "idconductoraccidente"


class AccidenteEstadoRepository(BaseWriteRepository):
    topic = "accidentestiposestadosincidentes_topic"
    primary_key_field = "idaccidentetipoestadoincidente"

    @classmethod
    def create(cls, payload):
        payload.setdefault("fechahoramodificado", int(time.time() * 1000))
        return super().create(payload)


class NotaRepository(BaseWriteRepository):
    topic = "notasaccidentes_topic"
    primary_key_field = "idnotaaccidentes"
