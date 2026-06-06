import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from accidentes.PKG2_Respuesta_Emergencias.CU07_Recibir_Despacho.repositories import (
    DespachoUnidadReadRepository,
    DespachoUnidadWriteRepository,
    AccidenteInfoReadRepository,
    AccidenteVehiculoReadRepository,
    NotificacionReadRepository,
    NotificacionWriteRepository,
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
                "fechahorallegada": ts_to_str(f_llegada_val),
                "accidente": {},
                "vehiculos": [],
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
                        "severidad_nivel": info.get("idseveridad"),
                        "estado_actual": "Pendiente",
                        "calle_nombre": "",
                        "ciudad_nombre": "",
                    }
                try:
                    pinot_id = int(accidente_id)
                except (ValueError, TypeError):
                    pinot_id = 0
                vehiculos = AccidenteVehiculoReadRepository.find_by_accidente(pinot_id)
                despacho["vehiculos"] = [
                    {
                        "tipovehiculo": v.get("tipovehiculo", ""),
                        "modelovehiculo": v.get("modelovehiculo", ""),
                        "mercanciapeligrosa": v.get("mercanciapeligrosa", False),
                    }
                    for v in vehiculos
                ]

            resultado.append(despacho)

        return resultado

    @staticmethod
    def marcar_llegada(iddespacho: int) -> bool:
        ahora_ms = int(time.time() * 1000)
        payload = {
            "iddespacho": int(iddespacho),
            "fechahorallegada": ahora_ms,
            "fecha_actualizacion": ahora_ms,
        }
        try:
            from accidentes.shared.repositories import KafkaRepository
            kafka = KafkaRepository()
            return kafka.enviar_mensaje(
                topic="despachos_topic",
                clave_primaria=int(iddespacho),
                datos_json=payload,
                operacion="AUDIT_INSERT",
            )
        except Exception as e:
            logger.error("Error marcando llegada despacho %s: %s", iddespacho, e)
            return False

    @staticmethod
    def obtener_notificaciones() -> List[Dict[str, Any]]:
        filas = NotificacionReadRepository.find_activas()

        def ts_to_str(ts):
            try:
                if ts and int(ts) > 0:
                    return datetime.fromtimestamp(int(ts) / 1000.0).isoformat()
            except Exception:
                pass
            return ''

        resultado = []
        for n in filas:
            accidente_id = str(n.get('idaccidente', ''))

            notif = {
                "idnotificaciondespacho": int(n.get('idnotificaciondespacho', 0)),
                "idaccidente": accidente_id,
                "numheridos": n.get("numheridos", 0),
                "numvehiculos": n.get("numvehiculos", 0),
                "tipos_necesarios": [],
                "fecha_actualizacion": ts_to_str(n.get('fecha_actualizacion')),
                "accidente": {},
                "vehiculos": [],
            }

            if accidente_id:
                info = AccidenteInfoReadRepository.find_by_id(accidente_id)
                if info:
                    notif["accidente"] = {
                        "idaccidente": info.get("idaccidente", accidente_id),
                        "latitudinicio": info.get("latitudinicio"),
                        "longitudinicio": info.get("longitudinicio"),
                        "numheridos": info.get("numheridos", 0),
                        "numfallecidos": info.get("numfallecidos", 0),
                        "descripcion": info.get("descripcion", ""),
                        "severidad_nivel": info.get("idseveridad"),
                        "estado_actual": "Pendiente",
                        "calle_nombre": "",
                        "ciudad_nombre": "",
                    }
                try:
                    pinot_id = int(accidente_id)
                except (ValueError, TypeError):
                    pinot_id = 0
                vehiculos = AccidenteVehiculoReadRepository.find_by_accidente(pinot_id)
                notif["vehiculos"] = [
                    {
                        "tipovehiculo": v.get("tipovehiculo", ""),
                        "modelovehiculo": v.get("modelovehiculo", ""),
                        "mercanciapeligrosa": v.get("mercanciapeligrosa", False),
                    }
                    for v in vehiculos
                ]

            resultado.append(notif)

        return resultado

    @staticmethod
    def aceptar_notificacion(notificacion_id: int, unidad_id: int) -> Dict[str, Any]:
        notif = NotificacionReadRepository.find_by_id(notificacion_id)
        if not notif:
            raise ValueError(f"Notificación {notificacion_id} no encontrada o ya inactiva")

        accidente_id = str(notif.get('idaccidente', ''))
        ahora_ms = int(time.time() * 1000)

        despacho_payload = {
            "iddespacho": int(ahora_ms % 10000000),
            "idaccidente": int(accidente_id) if accidente_id else 0,
            "idunidademergencia": int(unidad_id),
            "fechahoradespacho": ahora_ms,
            "activo": True,
            "fecha_actualizacion": ahora_ms,
        }

        exito_despacho = DespachoUnidadWriteRepository.create(despacho_payload)
        if not exito_despacho:
            logger.error("Error creando despacho desde notificacion %s", notificacion_id)
            raise RuntimeError("Error al crear el despacho")

        nombre_unidad, tipo_u = UNIDADES_INFO.get(unidad_id, (f"Unidad {unidad_id}", "OTROS"))

        def ts_to_str(ts):
            try:
                if ts and int(ts) > 0:
                    return datetime.fromtimestamp(int(ts) / 1000.0).isoformat()
            except Exception:
                pass
            return ''

        return {
            "iddespacho": despacho_payload["iddespacho"],
            "idaccidente": accidente_id,
            "idunidademergencia": unidad_id,
            "unidad_nombre": nombre_unidad,
            "tipo_unidad": tipo_u,
            "fechahoradespacho": ts_to_str(ahora_ms),
            "mensaje": "Despacho creado exitosamente",
        }
