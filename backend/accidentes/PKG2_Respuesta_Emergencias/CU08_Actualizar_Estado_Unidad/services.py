import time
import logging
from typing import List, Optional, Dict, Any

from accidentes.shared.repositories import KafkaRepository, PinotRepository

logger = logging.getLogger(__name__)


class UnidadEmergenciaService:

    CATALOGO_UNIDADES = [
        {"idunidademergencia": 1, "unidademergencia": "Alfa 1", "tipounidademergencia": "AMBULANCIA", "estadounidad": "EN_BASE", "activo": True},
        {"idunidademergencia": 2, "unidademergencia": "Alfa 2", "tipounidademergencia": "AMBULANCIA", "estadounidad": "EN_BASE", "activo": True},
        {"idunidademergencia": 3, "unidademergencia": "Rescate 1", "tipounidademergencia": "BOMBEROS", "estadounidad": "EN_BASE", "activo": True},
        {"idunidademergencia": 4, "unidademergencia": "Bomberos 4", "tipounidademergencia": "BOMBEROS", "estadounidad": "EN_BASE", "activo": True},
        {"idunidademergencia": 5, "unidademergencia": "ATM Movil 10", "tipounidademergencia": "TRANSITO", "estadounidad": "EN_BASE", "activo": True},
        {"idunidademergencia": 6, "unidademergencia": "ATM Movil 12", "tipounidademergencia": "TRANSITO", "estadounidad": "EN_BASE", "activo": True},
        {"idunidademergencia": 7, "unidademergencia": "Patrulla 105", "tipounidademergencia": "POLICIA", "estadounidad": "EN_BASE", "activo": True},
        {"idunidademergencia": 8, "unidademergencia": "Patrulla 109", "tipounidademergencia": "POLICIA", "estadounidad": "EN_BASE", "activo": True},
    ]

    @staticmethod
    async def obtener_unidades(tipo: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = "SELECT idunidademergencia, estadounidad, fecha_actualizacion FROM unidadesemergencia"

        ultimo_estado_map = {}
        try:
            filas = PinotRepository.execute_query(sql)
            filas_ordenadas = sorted(filas, key=lambda x: x.get('fecha_actualizacion', 0))
            for fila in filas_ordenadas:
                uid = int(fila.get('idunidademergencia', 0))
                est = str(fila.get('estadounidad', 'EN_BASE'))
                if uid > 0:
                    ultimo_estado_map[uid] = est
        except Exception as e:
            logger.warning(f"Error consultando estados de unidades en Pinot: {e}")

        resultado = []
        for uni in UnidadEmergenciaService.CATALOGO_UNIDADES:
            uid = uni["idunidademergencia"]

            uni_copia = uni.copy()
            if uid in ultimo_estado_map:
                uni_copia["estadounidad"] = ultimo_estado_map[uid]

            if tipo and uni_copia["tipounidademergencia"] != tipo:
                continue

            resultado.append(uni_copia)

        return resultado

    @staticmethod
    async def actualizar_estado(unidad_id: int, nuevo_estado: str) -> Dict[str, Any]:
        unidad_encontrada = None
        for uni in UnidadEmergenciaService.CATALOGO_UNIDADES:
            if uni["idunidademergencia"] == int(unidad_id):
                unidad_encontrada = uni
                break

        if not unidad_encontrada:
            raise ValueError(f"Unidad con ID {unidad_id} no encontrada en el catálogo.")

        ahora_ms = int(time.time() * 1000)
        payload = {
            "idunidademergencia": int(unidad_id),
            "unidademergencia": unidad_encontrada["unidademergencia"],
            "tipounidademergencia": unidad_encontrada["tipounidademergencia"],
            "estadounidad": nuevo_estado,
            "activo": True,
            "fecha_actualizacion": ahora_ms
        }

        kafka_repo = KafkaRepository()
        kafka_repo.enviar_mensaje(
            topic="unidadesemergencia_topic",
            clave_primaria=int(unidad_id),
            datos_json=payload,
            operacion="INSERT"
        )

        return payload
