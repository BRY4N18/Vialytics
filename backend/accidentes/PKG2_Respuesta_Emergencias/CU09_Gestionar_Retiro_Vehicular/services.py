import time
import logging
from datetime import datetime
from typing import List, Dict, Any

from accidentes.PKG2_Respuesta_Emergencias.CU09_Gestionar_Retiro_Vehicular.repositories import (
    RetiroReadRepository,
    RetiroWriteRepository,
    EvidenciaFotoWriteRepository,
)
from accidentes.shared.catalogo_repositories import UnidadEmergenciaCatalogoRepository

logger = logging.getLogger(__name__)

UNIDADES_INFO = UnidadEmergenciaCatalogoRepository.get_info_map()


class GestionarRetiroService:

    @staticmethod
    def solicitar_retiro(accidente_id: int, unidad_id: int, descripcion: str = '') -> Dict[str, Any]:
        ahora_ms = int(time.time() * 1000)

        ids_despacho = int(ahora_ms % 10000000)

        payload = {
            "iddespacho": ids_despacho,
            "idaccidente": int(accidente_id),
            "idunidademergencia": int(unidad_id),
            "fechahoradespacho": ahora_ms,
            "activo": True,
            "fecha_actualizacion": ahora_ms,
        }

        exito = RetiroWriteRepository.create(payload)
        if not exito:
            logger.error("Error creando retiro para accidente %s, unidad %s", accidente_id, unidad_id)
            raise RuntimeError("Error al solicitar el retiro vehicular")

        nombre_unidad, tipo_u = UNIDADES_INFO.get(unidad_id, (f"Unidad {unidad_id}", "OTROS"))

        def ts_to_str(ts):
            try:
                if ts and int(ts) > 0:
                    return datetime.fromtimestamp(int(ts) / 1000.0).isoformat()
            except Exception:
                pass
            return ''

        return {
            "iddespacho": ids_despacho,
            "idaccidente": accidente_id,
            "idunidademergencia": unidad_id,
            "unidad_nombre": nombre_unidad,
            "tipo_unidad": tipo_u,
            "fechahoradespacho": ts_to_str(ahora_ms),
            "descripcion": descripcion,
            "mensaje": "Retiro vehicular solicitado exitosamente",
        }

    @staticmethod
    def aceptar_retiro(retiro_id: int, nota: str = '') -> Dict[str, Any]:
        retiro = RetiroReadRepository.find_by_id(retiro_id)
        if not retiro:
            raise ValueError(f"Retiro {retiro_id} no encontrado")

        ahora_ms = int(time.time() * 1000)
        payload = {
            "iddespacho": int(retiro_id),
            "fecha_actualizacion": ahora_ms,
        }
        try:
            from accidentes.shared.repositories import KafkaRepository
            kafka = KafkaRepository()
            exito = kafka.enviar_mensaje(
                topic="despachos_topic",
                clave_primaria=int(retiro_id),
                datos_json=payload,
                operacion="AUDIT_INSERT",
            )
            if not exito:
                raise RuntimeError("Error al aceptar el retiro")
        except Exception as e:
            logger.error("Error aceptando retiro %s: %s", retiro_id, e)
            raise RuntimeError("Error al aceptar el retiro")

        return {
            "iddespacho": retiro_id,
            "mensaje": "Retiro aceptado exitosamente",
            "nota": nota,
        }

    @staticmethod
    def obtener_retiros_por_unidad(unidad_id: int) -> List[Dict[str, Any]]:
        filas = RetiroReadRepository.find_by_unidad(unidad_id)
        resultado = []
        for r in filas:
            def ts_to_str(ts):
                try:
                    if ts and int(ts) > 0:
                        return datetime.fromtimestamp(int(ts) / 1000.0).isoformat()
                except Exception:
                    pass
                return ''
            resultado.append({
                "iddespacho": int(r.get('iddespacho', 0)),
                "idaccidente": int(r.get('idaccidente', 0)),
                "idunidademergencia": int(r.get('idunidademergencia', 0)),
                "fechahoradespacho": ts_to_str(r.get('fechahoradespacho')),
                "fechahorallegada": ts_to_str(r.get('fechahorallegada')),
                "activo": r.get('activo', False),
            })
        return resultado

    @staticmethod
    def obtener_retiros_pendientes() -> List[Dict[str, Any]]:
        filas = RetiroReadRepository.find_pendientes()
        resultado = []
        for r in filas:
            def ts_to_str(ts):
                try:
                    if ts and int(ts) > 0:
                        return datetime.fromtimestamp(int(ts) / 1000.0).isoformat()
                except Exception:
                    pass
                return ''
            resultado.append({
                "iddespacho": int(r.get('iddespacho', 0)),
                "idaccidente": int(r.get('idaccidente', 0)),
                "idunidademergencia": int(r.get('idunidademergencia', 0)),
                "fechahoradespacho": ts_to_str(r.get('fechahoradespacho')),
                "fechahorallegada": ts_to_str(r.get('fechahorallegada')),
                "activo": r.get('activo', False),
            })
        return resultado

    @staticmethod
    def finalizar_retiro(retiro_id: int, nota_informe: str, urls_fotos: List[str]) -> Dict[str, Any]:
        retiro = RetiroReadRepository.find_by_id(retiro_id)
        if not retiro:
            raise ValueError(f"Retiro {retiro_id} no encontrado")

        ahora_ms = int(time.time() * 1000)
        accidente_id = int(retiro.get('idaccidente', 0))

        payload_llegada = {
            "iddespacho": int(retiro_id),
            "fechahorallegada": ahora_ms,
            "fecha_actualizacion": ahora_ms,
        }
        try:
            from accidentes.shared.repositories import KafkaRepository
            kafka = KafkaRepository()
            exito = kafka.enviar_mensaje(
                topic="despachos_topic",
                clave_primaria=int(retiro_id),
                datos_json=payload_llegada,
                operacion="AUDIT_INSERT",
            )
            if not exito:
                raise RuntimeError("Error al finalizar el retiro")
        except Exception as e:
            logger.error("Error finalizando retiro %s: %s", retiro_id, e)
            raise RuntimeError("Error al finalizar el retiro")

        fotos_subidas = 0
        for url in urls_fotos:
            foto_payload = {
                "idevidenciafoto": int(ahora_ms % 10000000 + fotos_subidas),
                "idaccidente": accidente_id,
                "urlevidenciafoto": url,
                "fechahora": ahora_ms,
                "activo": True,
                "fecha_actualizacion": ahora_ms,
            }
            if EvidenciaFotoWriteRepository.create(foto_payload):
                fotos_subidas += 1

        def ts_to_str(ts):
            try:
                if ts and int(ts) > 0:
                    return datetime.fromtimestamp(int(ts) / 1000.0).isoformat()
            except Exception:
                pass
            return ''

        return {
            "iddespacho": retiro_id,
            "idaccidente": accidente_id,
            "fechahorallegada": ts_to_str(ahora_ms),
            "nota_informe": nota_informe,
            "fotos_subidas": fotos_subidas,
            "mensaje": "Retiro finalizado exitosamente",
        }
