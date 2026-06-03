import time
import logging
from datetime import datetime
from typing import List, Dict, Any

from accidentes.PKG1_Gestion_Accidentes.CU04_Despachar_Emergencias.repositories import (
    DespachoReadRepository,
    DespachoWriteRepository,
    UnidadEmergenciaWriteRepository,
)
from accidentes.shared.catalogo_repositories import UnidadEmergenciaCatalogoRepository

logger = logging.getLogger(__name__)

UNIDADES_INFO = UnidadEmergenciaCatalogoRepository.get_info_map()


class DespachoService:

    @staticmethod
    def obtener_despachos(accidente_id: str) -> List[Dict[str, Any]]:
        filas = DespachoReadRepository.find_by_accidente(accidente_id)

        despachos_list = []
        for d in filas:
            id_unidad = int(d.get('idunidademergencia', 1))
            nombre, tipo_u = UNIDADES_INFO.get(id_unidad, (f"Unidad {id_unidad}", "OTROS"))

            f_despacho_val = d.get('fechahoradespacho', int(time.time() * 1000))
            f_llegada_val = d.get('fechahorallegada', 0)

            try:
                f_despacho_str = datetime.fromtimestamp(f_despacho_val / 1000.0).isoformat()
                f_llegada_str = datetime.fromtimestamp(f_llegada_val / 1000.0).isoformat() if f_llegada_val > 0 else ""
            except Exception as exc:
                logger.warning("Error convirtiendo timestamp de despacho: %s", exc)
                f_despacho_str = datetime.now().isoformat()
                f_llegada_str = ""

            despachos_list.append({
                "iddespacho": int(d.get('iddespacho', 1)),
                "idaccidente": accidente_id,
                "idunidademergencia": id_unidad,
                "unidad_nombre": nombre,
                "tipo_unidad": tipo_u,
                "fechahoradespacho": f_despacho_str,
                "fechahoraconfirmacion": f_despacho_str,
                "fechahorallegada": f_llegada_str
            })

        return despachos_list

    @staticmethod
    def _despachar_una_unidad(accidente_id: str, unidad_id: int) -> Dict[str, Any]:
        iddespacho = int(time.time() * 1000) % 1000000000 + unidad_id
        ahora_ms = int(time.time() * 1000)

        DespachoWriteRepository.create({
            "iddespacho": iddespacho,
            "idaccidente": accidente_id,
            "idunidademergencia": unidad_id,
            "activo": True,
            "fechahoradespacho": ahora_ms,
            "fechahorallegada": 0,
        })

        nombre, tipo_u = UNIDADES_INFO.get(unidad_id, (f"Unidad {unidad_id}", "OTROS"))

        UnidadEmergenciaWriteRepository.create({
            "idunidademergencia": unidad_id,
            "unidademergencia": nombre,
            "tipounidademergencia": tipo_u,
            "estadounidad": "EN_CAMINO",
            "activo": True,
        })

        return {
            "iddespacho": iddespacho,
            "idaccidente": accidente_id,
            "idunidademergencia": unidad_id,
            "unidad_nombre": nombre,
            "tipo_unidad": tipo_u,
            "fechahoradespacho": time.strftime('%Y-%m-%dT%H:%M:%S'),
            "fechahoraconfirmacion": time.strftime('%Y-%m-%dT%H:%M:%S'),
            "fechahorallegada": ""
        }

    @staticmethod
    def despachar_unidades(accidente_id: str, unidades_ids: List[int]) -> List[Dict[str, Any]]:
        despachos = []
        for uid in unidades_ids:
            try:
                despacho = DespachoService._despachar_una_unidad(accidente_id, uid)
                despachos.append(despacho)
            except Exception as e:
                logger.error(f"Error despachando unidad {uid} para accidente {accidente_id}: {e}")
        return despachos
