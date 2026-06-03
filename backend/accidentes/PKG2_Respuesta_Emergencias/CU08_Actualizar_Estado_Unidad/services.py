import time
import logging
from typing import List, Optional, Dict, Any

from accidentes.PKG2_Respuesta_Emergencias.CU08_Actualizar_Estado_Unidad.repositories import (
    UnidadEmergenciaReadRepository,
    UnidadEmergenciaWriteRepository,
)
from accidentes.shared.catalogo_repositories import UnidadEmergenciaCatalogoRepository

logger = logging.getLogger(__name__)

CATALOGO_UNIDADES = UnidadEmergenciaCatalogoRepository.get_all()


class UnidadEmergenciaService:

    @staticmethod
    def obtener_unidades(tipo: Optional[str] = None) -> List[Dict[str, Any]]:
        filas = UnidadEmergenciaReadRepository.get_all()

        ultimo_estado_map = {}
        filas_ordenadas = sorted(filas, key=lambda x: x.get('fecha_actualizacion', 0))
        for fila in filas_ordenadas:
            uid = int(fila.get('idunidademergencia', 0))
            est = str(fila.get('estadounidad', 'EN_BASE'))
            if uid > 0:
                ultimo_estado_map[uid] = est

        resultado = []
        for uni in CATALOGO_UNIDADES:
            uid = uni["idunidademergencia"]
            uni_copia = uni.copy()
            if uid in ultimo_estado_map:
                uni_copia["estadounidad"] = ultimo_estado_map[uid]
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

        payload = {
            "idunidademergencia": int(unidad_id),
            "unidademergencia": unidad_encontrada["unidademergencia"],
            "tipounidademergencia": unidad_encontrada["tipounidademergencia"],
            "estadounidad": nuevo_estado,
            "activo": True,
        }

        UnidadEmergenciaWriteRepository.create(payload)
        return payload
