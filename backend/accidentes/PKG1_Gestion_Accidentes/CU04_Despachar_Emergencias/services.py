import time
import logging
from datetime import datetime
from typing import List, Dict, Any

from accidentes.shared.repositories import KafkaRepository, PinotRepository

logger = logging.getLogger(__name__)


class DespachoService:

    @staticmethod
    async def obtener_despachos(accidente_id: str) -> List[Dict[str, Any]]:
        sql = f"SELECT iddespacho, idunidademergencia, fechahoradespacho, fechahorallegada FROM despachos WHERE idaccidente = '{accidente_id}'"
        try:
            filas = PinotRepository.execute_query(sql)
        except Exception as e:
            logger.error(f"Error consultando despachos en Pinot: {e}")
            filas = []

        despachos_list = []
        for d in filas:
            id_unidad = int(d.get('idunidademergencia', 1))

            unidades_info = {
                1: ("Alfa 1", "AMBULANCIA"),
                2: ("Alfa 2", "AMBULANCIA"),
                3: ("Rescate 1", "BOMBEROS"),
                4: ("Bomberos 4", "BOMBEROS"),
                5: ("ATM Movil 10", "TRANSITO"),
                6: ("ATM Movil 12", "TRANSITO"),
                7: ("Patrulla 105", "POLICIA"),
                8: ("Patrulla 109", "POLICIA")
            }
            nombre, tipo_u = unidades_info.get(id_unidad, (f"Unidad {id_unidad}", "OTROS"))

            f_despacho_val = d.get('fechahoradespacho', int(time.time() * 1000))
            f_llegada_val = d.get('fechahorallegada', 0)

            try:
                f_despacho_str = datetime.fromtimestamp(f_despacho_val / 1000.0).isoformat()
                f_llegada_str = datetime.fromtimestamp(f_llegada_val / 1000.0).isoformat() if f_llegada_val > 0 else ""
            except Exception:
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
    async def _despachar_una_unidad(accidente_id: str, unidad_id: int) -> Dict[str, Any]:
        iddespacho = int(time.time() * 1000) % 1000000000 + unidad_id
        ahora_ms = int(time.time() * 1000)

        payload_despacho = {
            "iddespacho": iddespacho,
            "idaccidente": accidente_id,
            "idunidademergencia": unidad_id,
            "activo": True,
            "fechahoradespacho": ahora_ms,
            "fechahorallegada": 0,
            "fecha_actualizacion": ahora_ms
        }

        kafka_repo = KafkaRepository()
        kafka_repo.enviar_mensaje(
            topic="despachos_topic",
            clave_primaria=iddespacho,
            datos_json=payload_despacho,
            operacion="INSERT"
        )

        unidades_info = {
            1: ("Alfa 1", "AMBULANCIA"),
            2: ("Alfa 2", "AMBULANCIA"),
            3: ("Rescate 1", "BOMBEROS"),
            4: ("Bomberos 4", "BOMBEROS"),
            5: ("ATM Movil 10", "TRANSITO"),
            6: ("ATM Movil 12", "TRANSITO"),
            7: ("Patrulla 105", "POLICIA"),
            8: ("Patrulla 109", "POLICIA")
        }
        nombre, tipo_u = unidades_info.get(unidad_id, (f"Unidad {unidad_id}", "OTROS"))

        payload_unidad = {
            "idunidademergencia": unidad_id,
            "unidademergencia": nombre,
            "tipounidademergencia": tipo_u,
            "estadounidad": "EN_CAMINO",
            "activo": True,
            "fecha_actualizacion": ahora_ms
        }
        kafka_repo.enviar_mensaje(
            topic="unidadesemergencia_topic",
            clave_primaria=unidad_id,
            datos_json=payload_unidad,
            operacion="INSERT"
        )

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
    async def despachar_unidades(accidente_id: str, unidades_ids: List[int]) -> List[Dict[str, Any]]:
        despachos = []
        for uid in unidades_ids:
            try:
                despacho = await DespachoService._despachar_una_unidad(accidente_id, uid)
                despachos.append(despacho)
            except Exception as e:
                logger.error(f"Error despachando unidad {uid} para accidente {accidente_id}: {e}")
        return despachos
