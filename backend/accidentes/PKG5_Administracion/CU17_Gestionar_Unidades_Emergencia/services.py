import time
import logging
from typing import List, Dict, Any

from accidentes.PKG5_Administracion.CU17_Gestionar_Unidades_Emergencia.repositories import (
    UnidadEmergenciaReadRepository,
    UnidadEmergenciaWriteRepository,
)
from accidentes.PKG2_Respuesta_Emergencias.CU08_Actualizar_Estado_Unidad.repositories import (
    UnidadEstadoHistorialReadRepository,
    UnidadEstadoHistorialWriteRepository,
)

logger = logging.getLogger(__name__)


class UnidadEmergenciaGestionService:

    @staticmethod
    def listar_unidades(tipo: str = None) -> List[Dict[str, Any]]:
        filas = UnidadEmergenciaReadRepository.get_all()
        for u in filas:
            u.setdefault("estadounidad", "En base")
        if tipo:
            filas = [u for u in filas if u.get("tipounidademergencia") == tipo]
        return filas

    @staticmethod
    def crear_unidad(nombre: str, tipo: str) -> Dict[str, Any]:
        max_id = UnidadEmergenciaReadRepository.get_max_id()
        nuevo_id = max_id + 1

        payload = {
            "idunidademergencia": nuevo_id,
            "unidademergencia": nombre,
            "tipounidademergencia": tipo,
            "estadounidad": "En base",
            "activo": True,
            "fecha_actualizacion": int(time.time() * 1000),
        }

        exito = UnidadEmergenciaWriteRepository.create(payload)
        if not exito:
            logger.error("Error creando unidad de emergencia %s", nombre)
            raise RuntimeError("Error al crear la unidad de emergencia")

        return payload

    @staticmethod
    def actualizar_unidad(unidad_id: int, nombre: str, tipo: str) -> Dict[str, Any]:
        existente = UnidadEmergenciaReadRepository.get_by_id(unidad_id)
        if not existente:
            raise ValueError(f"Unidad {unidad_id} no encontrada")

        estado_actual = UnidadEstadoHistorialReadRepository.get_ultimo_estado(unidad_id) or "En base"

        payload = {
            "idunidademergencia": unidad_id,
            "unidademergencia": nombre,
            "tipounidademergencia": tipo,
            "estadounidad": estado_actual,
            "activo": existente.get("activo", True),
            "fecha_actualizacion": int(time.time() * 1000),
        }

        exito = UnidadEmergenciaWriteRepository.create(payload)
        if not exito:
            logger.error("Error actualizando unidad de emergencia %s", nombre)
            raise RuntimeError("Error al actualizar la unidad de emergencia")

        return payload

    @staticmethod
    def toggle_activo(unidad_id: int, activo: bool) -> Dict[str, Any]:
        existente = UnidadEmergenciaReadRepository.get_by_id(unidad_id)
        if not existente:
            raise ValueError(f"Unidad {unidad_id} no encontrada")

        estado_actual = UnidadEstadoHistorialReadRepository.get_ultimo_estado(unidad_id) or "En base"

        payload = {
            "idunidademergencia": unidad_id,
            "unidademergencia": existente["unidademergencia"],
            "tipounidademergencia": existente["tipounidademergencia"],
            "estadounidad": estado_actual,
            "activo": activo,
            "fecha_actualizacion": int(time.time() * 1000),
        }

        exito = UnidadEmergenciaWriteRepository.create(payload)
        if not exito:
            logger.error("Error actualizando activo de unidad %s", unidad_id)
            raise RuntimeError("Error al actualizar la unidad de emergencia")

        return payload
