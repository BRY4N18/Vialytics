import logging
from typing import Any, Dict, List, Optional

from accidentes.shared.repositories import PinotRepository

logger = logging.getLogger(__name__)


class AccidenteExpedienteRepository:

    @staticmethod
    def find_by_id(accidente_id: str) -> List[Dict[str, Any]]:
        safe = PinotRepository.escape_sql_str(accidente_id)
        return PinotRepository.execute_query(
            f"SELECT idaccidente, latitudinicio, longitudinicio, idseveridad, activo, "
            f"numheridos, numfallecidos, numvehiculos, numvictimas, descripcion, "
            f"horainicio, horafin, codigopostal, duracionminutos, fechahoraclima, "
            f"idcalle, idciudad, idpais, idestado, idcondado, "
            f"idperiododia, idestadoclima, idelementofisico, "
            f"idtiporeportado, idreferenciaestacion, idfecha, idusuario, "
            f"fecha_actualizacion "
            f"FROM accidentes WHERE idaccidente = '{safe}' LIMIT 1"
        )


class SeveridadExpedienteRepository:

    @staticmethod
    def find_by_id(idseveridad: int) -> Optional[Dict[str, Any]]:
        rows = PinotRepository.execute_query(
            f"SELECT severidad, descripcion FROM severidades "
            f"WHERE idseveridad = {idseveridad} LIMIT 1"
        )
        return rows[0] if rows else None


class EstadoIncidenteExpedienteRepository:

    @staticmethod
    def find_latest_by_accidente(pinot_id_accidente: int) -> Optional[int]:
        rows = PinotRepository.execute_query(
            f"SELECT idtipoestadoincidente FROM accidentestiposestadosincidentes "
            f"WHERE idaccidente = {pinot_id_accidente} AND activo = true "
            f"ORDER BY fechahoramodificado DESC LIMIT 1"
        )
        if rows:
            return rows[0].get("idtipoestadoincidente")
        return None


class DespachoRepository:

    @staticmethod
    def find_by_accidente(pinot_id_accidente: int) -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            f"SELECT iddespacho, idunidademergencia, fechahoradespacho, "
            f"fechahoraconfirmacion, fechahorallegada "
            f"FROM despachos WHERE idaccidente = {pinot_id_accidente} LIMIT 20"
        )


class NotaExpedienteRepository:

    @staticmethod
    def find_by_accidente(pinot_id_accidente: int) -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            f"SELECT idnotaaccidentes, nota, tipo, fecha_actualizacion "
            f"FROM notasaccidentes WHERE idaccidente = {pinot_id_accidente} LIMIT 50"
        )


class ConductorAccidenteExpedienteRepository:

    @staticmethod
    def find_by_accidente(pinot_id_accidente: int) -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            f"SELECT idconductor, idvehiculo, idestadoconductor "
            f"FROM conductoresaccidentes "
            f"WHERE idaccidente = {pinot_id_accidente} AND activo = true LIMIT 50"
        )

    @staticmethod
    def find_vehiculo_ids_by_accidente(pinot_id_accidente: int) -> List[int]:
        rows = PinotRepository.execute_query(
            f"SELECT idvehiculo FROM conductoresaccidentes "
            f"WHERE idaccidente = {pinot_id_accidente} AND activo = true LIMIT 20"
        )
        return [r["idvehiculo"] for r in rows if r.get("idvehiculo") is not None]


class ConductorExpedienteRepository:

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, Dict[str, Any]]:
        if not ids:
            return {}
        ids_str = ", ".join(str(x) for x in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idconductor, nombres, apellidos, identificacion, genero, "
            f"tipolicencia, estadolicencia, ciudadresidencia, aniosexperiencia "
            f"FROM conductores WHERE idconductor IN ({ids_str}) LIMIT 50"
        )
        return {r["idconductor"]: r for r in rows}


class VehiculoExpedienteRepository:

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, Dict[str, Any]]:
        if not ids:
            return {}
        ids_str = ", ".join(str(x) for x in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idvehiculo, tipovehiculo, modelovehiculo, categoriausovehiculo, "
            f"mercanciapeligrosa, ejes "
            f"FROM vehiculos WHERE idvehiculo IN ({ids_str}) LIMIT 50"
        )
        return {r["idvehiculo"]: r for r in rows}

    @staticmethod
    def find_by_id(vehiculo_id: int) -> Optional[Dict[str, Any]]:
        rows = PinotRepository.execute_query(
            f"SELECT * FROM vehiculos WHERE idvehiculo = {vehiculo_id} LIMIT 1"
        )
        return rows[0] if rows else None


class EstadoConductorExpedienteRepository:

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, Dict[str, Any]]:
        if not ids:
            return {}
        ids_str = ", ".join(str(x) for x in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idestadoconductor, estadosobriedad, nivelatencion, "
            f"condicionfisica, usoseguridad "
            f"FROM estadosconductores WHERE idestadoconductor IN ({ids_str}) LIMIT 50"
        )
        return {r["idestadoconductor"]: r for r in rows}


class ClimaExpedienteRepository:

    @staticmethod
    def find_by_id(idestadoclima: int) -> Optional[Dict[str, Any]]:
        rows = PinotRepository.execute_query(
            f"SELECT condicionclima, temperaturaf, humedadporcentaje, "
            f"visibilidadmillas, velocidadvientomph "
            f"FROM estadoclima WHERE idestadoclima = {idestadoclima} LIMIT 1"
        )
        return rows[0] if rows else None

    @staticmethod
    def find_full_by_id(idestadoclima: int) -> Optional[Dict[str, Any]]:
        rows = PinotRepository.execute_query(
            f"SELECT * FROM estadoclima WHERE idestadoclima = {idestadoclima} LIMIT 1"
        )
        return rows[0] if rows else None

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, Dict[str, Any]]:
        if not ids:
            return {}
        ids_str = ", ".join(str(x) for x in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idestadoclima, condicionclima, temperaturaf, humedadporcentaje, "
            f"visibilidadmillas, velocidadvientomph "
            f"FROM estadoclima WHERE idestadoclima IN ({ids_str}) LIMIT 100"
        )
        return {r["idestadoclima"]: r for r in rows if r.get("idestadoclima") is not None}


class PeriodoDiaExpedienteRepository:

    @staticmethod
    def find_by_id(idperiododia: int) -> Optional[Dict[str, Any]]:
        rows = PinotRepository.execute_query(
            f"SELECT amaneceranochecer, crepusculocivil, crepusculonautico, "
            f"crepusculoastronomico "
            f"FROM periododia WHERE idperiododia = {idperiododia} LIMIT 1"
        )
        return rows[0] if rows else None

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, Dict[str, Any]]:
        if not ids:
            return {}
        ids_str = ", ".join(str(x) for x in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idperiododia, amaneceranochecer, crepusculocivil, crepusculonautico, "
            f"crepusculoastronomico "
            f"FROM periododia WHERE idperiododia IN ({ids_str}) LIMIT 100"
        )
        return {r["idperiododia"]: r for r in rows if r.get("idperiododia") is not None}


class ElementoFisicoExpedienteRepository:

    @staticmethod
    def find_by_id(idelementofisico: int) -> Optional[Dict[str, Any]]:
        rows = PinotRepository.execute_query(
            f"SELECT cercacruce, cercasemaforo, cercaparada, cercaestacion, "
            f"cercabache, cercaviatren "
            f"FROM elementofisico WHERE idelementofisico = {idelementofisico} LIMIT 1"
        )
        return rows[0] if rows else None

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, Dict[str, Any]]:
        if not ids:
            return {}
        ids_str = ", ".join(str(x) for x in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idelementofisico, cercacruce, cercasemaforo, cercaparada, cercaestacion, "
            f"cercabache, cercaviatren "
            f"FROM elementofisico WHERE idelementofisico IN ({ids_str}) LIMIT 100"
        )
        return {r["idelementofisico"]: r for r in rows if r.get("idelementofisico") is not None}


class EstacionExpedienteRepository:

    @staticmethod
    def find_by_id(idreferenciaestacion: int) -> Optional[Dict[str, Any]]:
        rows = PinotRepository.execute_query(
            f"SELECT codigoaeropuerto, zonahoraria "
            f"FROM referenciaestacion "
            f"WHERE idreferenciaestacion = {idreferenciaestacion} LIMIT 1"
        )
        return rows[0] if rows else None

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, Dict[str, Any]]:
        if not ids:
            return {}
        ids_str = ", ".join(str(x) for x in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idreferenciaestacion, codigoaeropuerto, zonahoraria "
            f"FROM referenciaestacion "
            f"WHERE idreferenciaestacion IN ({ids_str}) LIMIT 100"
        )
        return {r["idreferenciaestacion"]: r for r in rows if r.get("idreferenciaestacion") is not None}


class PaisExpedienteRepository:

    @staticmethod
    def find_by_id(idpais: int) -> Optional[str]:
        rows = PinotRepository.execute_query(
            f"SELECT pais FROM paises WHERE idpais = {idpais} LIMIT 1"
        )
        return str(rows[0]["pais"]) if rows else None

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, str]:
        if not ids:
            return {}
        ids_str = ", ".join(str(x) for x in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idpais, pais FROM paises WHERE idpais IN ({ids_str}) LIMIT 100"
        )
        return {r["idpais"]: str(r.get("pais", "")) for r in rows if r.get("idpais") is not None}


class EstadoGeograficoExpedienteRepository:

    @staticmethod
    def find_by_id(idestado: int) -> Optional[str]:
        rows = PinotRepository.execute_query(
            f"SELECT estado FROM estados WHERE idestado = {idestado} LIMIT 1"
        )
        return str(rows[0]["estado"]) if rows else None

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, str]:
        if not ids:
            return {}
        ids_str = ", ".join(str(x) for x in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idestado, estado FROM estados WHERE idestado IN ({ids_str}) LIMIT 100"
        )
        return {r["idestado"]: str(r.get("estado", "")) for r in rows if r.get("idestado") is not None}


class CondadoExpedienteRepository:

    @staticmethod
    def find_by_id(idcondado: int) -> Optional[str]:
        rows = PinotRepository.execute_query(
            f"SELECT condado FROM condados WHERE idcondado = {idcondado} LIMIT 1"
        )
        return str(rows[0]["condado"]) if rows else None

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, str]:
        if not ids:
            return {}
        ids_str = ", ".join(str(x) for x in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idcondado, condado FROM condados WHERE idcondado IN ({ids_str}) LIMIT 200"
        )
        return {r["idcondado"]: str(r.get("condado", "")) for r in rows if r.get("idcondado") is not None}


class TipoReportadoExpedienteRepository:

    @staticmethod
    def find_by_id(idtiporeportado: int) -> Optional[str]:
        rows = PinotRepository.execute_query(
            f"SELECT descripcion FROM tiporeportado "
            f"WHERE idtiporeportado = {idtiporeportado} LIMIT 1"
        )
        return str(rows[0]["descripcion"]) if rows else None

    @staticmethod
    def find_by_ids(ids: List[int]) -> Dict[int, str]:
        if not ids:
            return {}
        ids_str = ", ".join(str(x) for x in ids)
        rows = PinotRepository.execute_query(
            f"SELECT idtiporeportado, tiporeportado FROM tiposreportados WHERE idtiporeportado IN ({ids_str}) LIMIT 100"
        )
        return {r["idtiporeportado"]: str(r.get("tiporeportado", "")) for r in rows if r.get("idtiporeportado") is not None}


class EvidenciaFotoRepository:

    @staticmethod
    def find_by_accidente(pinot_id_accidente: int) -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            f"SELECT urlevidenciafoto, fechahora FROM evidenciasfotos "
            f"WHERE idaccidente = {pinot_id_accidente} AND activo = true LIMIT 50"
        )
