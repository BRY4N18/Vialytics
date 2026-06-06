import time
import zlib
import logging
from datetime import datetime
from typing import List, Dict, Any

from accidentes.PKG1_Gestion_Accidentes.CU04_Despachar_Emergencias.repositories import (
    DespachoReadRepository,
    AccidenteInfoReadRepository,
    NotificacionWriteRepository,
)
from accidentes.shared.catalogo_repositories import UnidadEmergenciaCatalogoRepository

logger = logging.getLogger(__name__)


class DespachoService:

    @staticmethod
    def obtener_despachos(accidente_id: str) -> List[Dict[str, Any]]:
        filas = DespachoReadRepository.find_by_accidente(accidente_id)
        info_map = UnidadEmergenciaCatalogoRepository.get_info_map()

        despachos_list = []
        for d in filas:
            id_unidad = int(d.get('idunidademergencia', 1))
            nombre, tipo_u = info_map.get(id_unidad, (f"Unidad {id_unidad}", "OTROS"))

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
    def despachar_unidades(accidente_id: str, tipos: List[str]) -> Dict[str, Any]:
        return DespachoService._crear_notificacion(accidente_id, tipos)

    @staticmethod
    def _crear_notificacion(accidente_id: str, tipos: List[str]) -> Dict[str, Any]:
        ahora_ms = int(time.time() * 1000)
        notificacion_id = int(ahora_ms % 10000000)

        try:
            info = AccidenteInfoReadRepository.find_by_id(accidente_id)
        except Exception as e:
            logger.error("Error consultando accidente %s para notificacion: %s", accidente_id, e)
            info = {}

        pinot_id = zlib.crc32(accidente_id.encode('utf-8')) & 0x7FFFFFFF
        payload = {
            "idnotificaciondespacho": notificacion_id,
            "idaccidente": pinot_id,
            "numheridos": info.get("numheridos", 0) if info else 0,
            "numvehiculos": info.get("numvehiculos", 0) if info else 0,
            "activo": True,
            "fecha_actualizacion": ahora_ms,
        }

        try:
            exito = NotificacionWriteRepository.create(payload)
            if not exito:
                logger.warning("NotificacionWriteRepository.create retorno False para notificacion %s", notificacion_id)
        except Exception as e:
            logger.error("Excepcion enviando notificacion a Kafka: %s", e)

        return {
            "idnotificacion": notificacion_id,
            "idaccidente": accidente_id,
            "mensaje": "Notificación de despacho creada exitosamente",
        }
