import time
import logging
from typing import List, Optional, Dict, Any

from accidentes.PKG2_Respuesta_Emergencias.CU08_Actualizar_Estado_Unidad.repositories import (
    UnidadEmergenciaWriteRepository,
    UnidadEstadoHistorialReadRepository,
    UnidadEstadoHistorialWriteRepository,
)
from accidentes.shared.catalogo_repositories import UnidadEmergenciaCatalogoRepository

logger = logging.getLogger(__name__)

CATALOGO_UNIDADES = UnidadEmergenciaCatalogoRepository.get_all()


class UnidadEmergenciaService:

    @staticmethod
    def obtener_unidades(tipo: Optional[str] = None) -> List[Dict[str, Any]]:
        resultado = []
        for uni in CATALOGO_UNIDADES:
            uid = uni["idunidademergencia"]
            uni_copia = uni.copy()
            estado = UnidadEstadoHistorialReadRepository.get_ultimo_estado(uid) or "En base"
            uni_copia["estadounidad"] = estado
            if tipo and uni_copia["tipounidademergencia"] != tipo:
                continue
            resultado.append(uni_copia)
        return resultado

    @staticmethod
    def actualizar_estado(unidad_id: int, nuevo_estado: str) -> Dict[str, Any]:
        unidad_encontrada = None
        for uni in CATALOGO_UNIDADES:
            if uni["idunidademergencia"] == int(unidad_id):
                unidad_encontrada = uni
                break

        if not unidad_encontrada:
            raise ValueError(f"Unidad con ID {unidad_id} no encontrada en el catálogo.")

        estado_anterior = UnidadEstadoHistorialReadRepository.get_ultimo_estado(unidad_id) or "En base"

        payload = {
            "idunidademergencia": int(unidad_id),
            "unidademergencia": unidad_encontrada["unidademergencia"],
            "tipounidademergencia": unidad_encontrada["tipounidademergencia"],
            "estadounidad": nuevo_estado,
            "activo": True,
        }

        UnidadEmergenciaWriteRepository.create(payload)

        max_id = UnidadEstadoHistorialReadRepository.get_max_id()
        historial_payload = {
            "idhistorial": max_id + 1,
            "idunidademergencia": int(unidad_id),
            "unidademergencia": unidad_encontrada["unidademergencia"],
            "tipounidademergencia": unidad_encontrada["tipounidademergencia"],
            "estadoanterior": estado_anterior,
            "estadonuevo": nuevo_estado,
            "fecha_actualizacion": int(time.time() * 1000),
            "activo": True,
        }
        UnidadEstadoHistorialWriteRepository.create(historial_payload)

        return payload
