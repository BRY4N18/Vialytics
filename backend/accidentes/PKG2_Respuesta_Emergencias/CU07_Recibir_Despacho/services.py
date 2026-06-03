import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from accidentes.PKG2_Respuesta_Emergencias.CU07_Recibir_Despacho.repositories import (
    DespachoUnidadReadRepository,
    DespachoUnidadWriteRepository,
    AccidenteInfoReadRepository,
)
from accidentes.shared.catalogo_repositories import UnidadEmergenciaCatalogoRepository

logger = logging.getLogger(__name__)

UNIDADES_INFO = UnidadEmergenciaCatalogoRepository.get_info_map()


class RecibirDespachoService:

    @staticmethod
    def obtener_despachos(unidad_id: int, solo_pendientes: bool = False) -> List[Dict[str, Any]]:
        if solo_pendientes:
            filas = DespachoUnidadReadRepository.find_pendientes_by_unidad(unidad_id)
        else:
            filas = DespachoUnidadReadRepository.find_by_unidad(unidad_id)

        nombre_unidad, tipo_u = UNIDADES_INFO.get(unidad_id, (f"Unidad {unidad_id}", "OTROS"))

        resultado = []
        for d in filas:
            accidente_id = str(d.get('idaccidente', ''))
            f_despacho_val = d.get('fechahoradespacho', int(time.time() * 1000))
            f_conf_val = d.get('fechahoraconfirmacion', 0)
            f_llegada_val = d.get('fechahorallegada', 0)

            def ts_to_str(ts):
                try:
                    if ts and int(ts) > 0:
                        return datetime.fromtimestamp(int(ts) / 1000.0).isoformat()
                except Exception:
                    pass
                return ''

            despacho = {
                "iddespacho": int(d.get('iddespacho', 0)),
                "idaccidente": accidente_id,
                "idunidademergencia": unidad_id,
                "unidad_nombre": nombre_unidad,
                "tipo_unidad": tipo_u,
                "fechahoradespacho": ts_to_str(f_despacho_val),
                "fechahoraconfirmacion": ts_to_str(f_conf_val),
                "fechahorallegada": ts_to_str(f_llegada_val),
                "accidente": {},
            }

            if accidente_id:
                info = AccidenteInfoReadRepository.find_by_id(accidente_id)
                if info:
                    despacho["accidente"] = {
                        "idaccidente": info.get("idaccidente", accidente_id),
                        "latitudinicio": info.get("latitudinicio"),
                        "longitudinicio": info.get("longitudinicio"),
                        "numheridos": info.get("numheridos", 0),
                        "numfallecidos": info.get("numfallecidos", 0),
                        "descripcion": info.get("descripcion", ""),
                        "severidad_nivel": info.get("severidad_nivel"),
                        "estado_actual": info.get("estado_actual", ""),
                        "calle_nombre": info.get("calle_nombre", ""),
                        "ciudad_nombre": info.get("ciudad_nombre", ""),
                    }

            resultado.append(despacho)

        return resultado

    @staticmethod
    def confirmar_despacho(iddespacho: int) -> bool:
        exito = DespachoUnidadWriteRepository.confirmar(iddespacho)
        if not exito:
            logger.error("No se pudo confirmar el despacho %s", iddespacho)
            raise RuntimeError("Error al confirmar el despacho en Kafka")
        return True

    @staticmethod
    def marcar_llegada(iddespacho: int) -> bool:
        exito = DespachoUnidadWriteRepository.marcar_llegada(iddespacho)
        if not exito:
            logger.error("No se pudo marcar llegada del despacho %s", iddespacho)
            raise RuntimeError("Error al marcar llegada del despacho en Kafka")
        return True
