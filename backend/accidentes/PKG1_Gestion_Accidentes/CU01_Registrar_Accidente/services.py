import uuid
import time
import zlib
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from accidentes.shared.repositories import KafkaRepository, PinotRepository
from accidentes.PKG1_Gestion_Accidentes.CU06_Asignar_Severidad.services import SeveridadService

logger = logging.getLogger(__name__)


class AccidenteRegistroService:

    @staticmethod
    def _uuid_to_pinot_id(uuid_str: str) -> int:
        return zlib.crc32(uuid_str.encode('utf-8')) & 0x7FFFFFFF

    @staticmethod
    def _obtener_pinot_id_severidad(level: int) -> int:
        if abs(level) > 10:
            return level
        mapping = {
            1: -2082672713,
            2: 450215437,
            3: 1842515611,
            4: -206169288
        }
        return mapping.get(level, -2082672713)

    @staticmethod
    def _obtener_pinot_id_clima(condicion: str) -> int:
        if not condicion:
            return 1620546972
        try:
            cond_escaped = condicion.replace("'", "''")
            rows = PinotRepository.execute_query(
                f"SELECT idestadoclima FROM estadoclima WHERE condicionclima LIKE '%{cond_escaped}%' LIMIT 1"
            )
            if rows:
                return int(rows[0].get("idestadoclima"))
        except Exception:
            pass
        return 1620546972

    @staticmethod
    def _obtener_pinot_id_estacion(codigo: str) -> int:
        if not codigo:
            return 1
        try:
            rows = PinotRepository.execute_query(f"SELECT idreferenciaestacion FROM referenciaestacion WHERE codigoaeropuerto = '{codigo}' LIMIT 1")
            if rows:
                return int(rows[0].get("idreferenciaestacion"))
        except Exception:
            pass
        return 1

    @staticmethod
    def registrar_accidente(datos: Dict[str, Any]) -> Dict[str, Any]:
        idaccidente = str(uuid.uuid4())
        datos['idaccidente'] = idaccidente

        numheridos = int(datos.get('numheridos', 0))
        numfallecidos = int(datos.get('numfallecidos', 0))
        numvehiculos = int(datos.get('numvehiculos', 1))

        severidad = datos.get('idseveridad_id')
        if severidad is None or severidad == '' or int(severidad) == 0:
            severidad = SeveridadService.calcular(numheridos, numfallecidos, numvehiculos)
        else:
            severidad = int(severidad)
        datos['idseveridad_id'] = severidad

        clima_cond = datos.get('condicion_clima', '')
        apt = datos.get('codigoaeropuerto', '')

        pinot_id_pais = int(datos.get('idpais_id', 1))
        pinot_id_estado = int(datos.get('idestado_id', 1))
        pinot_id_condado = int(datos.get('idcondado_id', 1))
        pinot_id_ciudad = int(datos.get('idciudad_id', 1))
        pinot_id_calle = int(datos.get('idcalle_id', 1))
        pinot_id_severidad = AccidenteRegistroService._obtener_pinot_id_severidad(severidad)
        pinot_id_clima = AccidenteRegistroService._obtener_pinot_id_clima(clima_cond)
        pinot_id_estacion = AccidenteRegistroService._obtener_pinot_id_estacion(apt)
        pinot_tiporeportado = int(datos.get('idtiporeportado_id', 1))
        pinot_fecha = int(datos.get('idfecha_id', 1))
        pinot_periododia = int(datos.get('idperiododia_id', 1))
        pinot_elementofisico = int(datos.get('idelementofisico_id', 1))
        pinot_usuario = int(datos.get('idusuario_id', 1))

        ahora_ms = int(time.time() * 1000)
        horainicio = datetime.now().strftime("%H:%M:%S")
        pinot_id_accidente = AccidenteRegistroService._uuid_to_pinot_id(idaccidente)

        payload_accidente = {
            "idaccidente": idaccidente,
            "idseveridad": pinot_id_severidad,
            "idcalle": pinot_id_calle,
            "idciudad": pinot_id_ciudad,
            "idcondado": pinot_id_condado,
            "idestado": pinot_id_estado,
            "idpais": pinot_id_pais,
            "idperiododia": pinot_periododia,
            "idestadoclima": pinot_id_clima,
            "idusuario": pinot_usuario,
            "idelementofisico": pinot_elementofisico,
            "idtiporeportado": pinot_tiporeportado,
            "idreferenciaestacion": pinot_id_estacion,
            "idfecha": pinot_fecha,
            "horainicio": horainicio,
            "horafin": "",
            "descripcion": datos.get('descripcion', ''),
            "codigopostal": datos.get('codigopostal', ''),
            "activo": True,
            "duracionminutos": 0,
            "numvehiculos": numvehiculos,
            "numvictimas": numheridos + numfallecidos,
            "numheridos": numheridos,
            "numfallecidos": numfallecidos,
            "latitudinicio": float(datos.get('latitudinicio', -2.1894)),
            "longitudinicio": float(datos.get('longitudinicio', -79.8890)),
            "distanciamillas": 0.0,
            "fechahoraclima": ahora_ms,
            "fecha_actualizacion": ahora_ms
        }

        kafka_repo = KafkaRepository()

        kafka_repo.enviar_mensaje(
            topic="accidentes_topic",
            clave_primaria=idaccidente,
            datos_json=payload_accidente,
            operacion="INSERT"
        )

        base_id = int(time.time_ns())
        vehiculos_detalles = datos.get('vehiculos_detalles', [])
        for idx, v in enumerate(vehiculos_detalles):
            idvehiculo = (base_id + idx * 4 + 1) % 10000000000
            idconductor = (base_id + idx * 4 + 2) % 10000000000
            idestadoconductor = (base_id + idx * 4 + 3) % 10000000000
            idconductoraccidente = (base_id + idx * 4 + 4) % 10000000000

            payload_vehiculo = {
                "idvehiculo": idvehiculo,
                "tipovehiculo": v.get('tipovehiculo', 'Automóvil'),
                "modelovehiculo": v.get('modelovehiculo', 'Genérico'),
                "categoriausovehiculo": v.get('categoriausovehiculo', 'Particular'),
                "mercanciapeligrosa": bool(v.get('mercanciapeligrosa', False)),
                "ejes": int(v.get('ejes', 2)),
                "activo": True,
                "fecha_actualizacion": ahora_ms
            }
            kafka_repo.enviar_mensaje(topic="vehiculos_topic", clave_primaria=idvehiculo, datos_json=payload_vehiculo, operacion="INSERT")

            payload_conductor = {
                "idconductor": idconductor,
                "nombres": v.get('nombres', 'Nombre'),
                "apellidos": v.get('apellidos', 'Apellido'),
                "identificacion": v.get('identificacion', ''),
                "genero": v.get('genero', 'M'),
                "tipolicencia": v.get('tipolicencia', 'B'),
                "estadolicencia": v.get('estadolicencia', 'Vigente'),
                "ciudadresidencia": v.get('ciudadresidencia', 'Quito'),
                "aniosexperiencia": int(v.get('aniosexperiencia', 0)),
                "activo": True,
                "fecha_actualizacion": ahora_ms
            }
            kafka_repo.enviar_mensaje(topic="conductores_topic", clave_primaria=idconductor, datos_json=payload_conductor, operacion="INSERT")

            payload_estado = {
                "idestadoconductor": idestadoconductor,
                "estadosobriedad": bool(v.get('estadosobriedad', True)),
                "nivelatencion": bool(v.get('nivelatencion', True)),
                "condicionfisica": bool(v.get('condicionfisica', True)),
                "usoseguridad": bool(v.get('usoseguridad', True)),
                "activo": True,
                "fecha_actualizacion": ahora_ms
            }
            kafka_repo.enviar_mensaje(topic="estadosconductores_topic", clave_primaria=idestadoconductor, datos_json=payload_estado, operacion="INSERT")

            payload_link = {
                "idconductoraccidente": idconductoraccidente,
                "idaccidente": pinot_id_accidente,
                "idconductor": idconductor,
                "idestadoconductor": idestadoconductor,
                "idvehiculo": idvehiculo,
                "activo": True,
                "fecha_actualizacion": ahora_ms
            }
            kafka_repo.enviar_mensaje(topic="conductoresaccidentes_topic", clave_primaria=idconductoraccidente, datos_json=payload_link, operacion="INSERT")

        id_estado_rel = int(time.time() * 1000) % 1000000000
        payload_estado = {
            "idaccidentetipoestadoincidente": id_estado_rel,
            "idaccidente": pinot_id_accidente,
            "idtipoestadoincidente": 1,
            "activo": True,
            "fechahoramodificado": ahora_ms,
            "fecha_actualizacion": ahora_ms
        }
        kafka_repo.enviar_mensaje(
            topic="accidentestiposestadosincidentes_topic",
            clave_primaria=id_estado_rel,
            datos_json=payload_estado,
            operacion="INSERT"
        )

        nota_inicial = datos.get('nota_inicial')
        if nota_inicial:
            id_nota = int(time.time() * 1000) % 1000000000
            payload_nota = {
                "idnotaaccidentes": id_nota,
                "idaccidente": pinot_id_accidente,
                "idusuario": pinot_usuario,
                "nota": nota_inicial,
                "tipo": True,
                "activo": True,
                "fecha_actualizacion": ahora_ms
            }
            kafka_repo.enviar_mensaje(
                topic="notasaccidentes_topic",
                clave_primaria=id_nota,
                datos_json=payload_nota,
                operacion="INSERT"
            )

        return payload_accidente

    @staticmethod
    def actualizar_accidente(accidente_id: str, datos: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            existe = PinotRepository.execute_query(
                f"SELECT idaccidente FROM accidentes WHERE idaccidente = '{accidente_id}' LIMIT 1"
            )
            if not existe:
                return None
        except Exception:
            return None

        numheridos = int(datos.get('numheridos', 0))
        numfallecidos = int(datos.get('numfallecidos', 0))
        numvehiculos = int(datos.get('numvehiculos', 1))

        severidad = datos.get('idseveridad_id')
        if severidad is None or severidad == '' or int(severidad) == 0:
            severidad = SeveridadService.calcular(numheridos, numfallecidos, numvehiculos)
        else:
            severidad = int(severidad)

        clima_cond = datos.get('condicion_clima', '')
        apt = datos.get('codigoaeropuerto', '')

        pinot_id_pais = int(datos.get('idpais_id', 1))
        pinot_id_estado = int(datos.get('idestado_id', 1))
        pinot_id_condado = int(datos.get('idcondado_id', 1))
        pinot_id_ciudad = int(datos.get('idciudad_id', 1))
        pinot_id_calle = int(datos.get('idcalle_id', 1))
        pinot_id_severidad = AccidenteRegistroService._obtener_pinot_id_severidad(severidad)
        pinot_id_clima = AccidenteRegistroService._obtener_pinot_id_clima(clima_cond)
        pinot_id_estacion = AccidenteRegistroService._obtener_pinot_id_estacion(apt)
        pinot_tiporeportado = int(datos.get('idtiporeportado_id', 1))
        pinot_fecha = int(datos.get('idfecha_id', 1))
        pinot_periododia = int(datos.get('idperiododia_id', 1))
        pinot_elementofisico = int(datos.get('idelementofisico_id', 1))
        pinot_usuario = int(datos.get('idusuario_id', 1))

        ahora_ms = int(time.time() * 1000)
        pinot_id_accidente = AccidenteRegistroService._uuid_to_pinot_id(accidente_id)

        payload_accidente = {
            "idaccidente": accidente_id,
            "idseveridad": pinot_id_severidad,
            "idcalle": pinot_id_calle,
            "idciudad": pinot_id_ciudad,
            "idcondado": pinot_id_condado,
            "idestado": pinot_id_estado,
            "idpais": pinot_id_pais,
            "idperiododia": pinot_periododia,
            "idestadoclima": pinot_id_clima,
            "idusuario": pinot_usuario,
            "idelementofisico": pinot_elementofisico,
            "idtiporeportado": pinot_tiporeportado,
            "idreferenciaestacion": pinot_id_estacion,
            "idfecha": pinot_fecha,
            "horainicio": str(datos.get('horainicio', '')),
            "horafin": str(datos.get('horafin', '')),
            "descripcion": datos.get('descripcion', ''),
            "codigopostal": datos.get('codigopostal', ''),
            "activo": True,
            "duracionminutos": int(datos.get('duracionminutos', 0)),
            "numvehiculos": numvehiculos,
            "numvictimas": numheridos + numfallecidos,
            "numheridos": numheridos,
            "numfallecidos": numfallecidos,
            "latitudinicio": float(datos.get('latitudinicio', -2.1894)),
            "longitudinicio": float(datos.get('longitudinicio', -79.8890)),
            "distanciamillas": 0.0,
            "fechahoraclima": ahora_ms,
            "fecha_actualizacion": ahora_ms
        }

        kafka_repo = KafkaRepository()
        kafka_repo.enviar_mensaje(
            topic="accidentes_topic",
            clave_primaria=accidente_id,
            datos_json=payload_accidente,
            operacion="INSERT"
        )

        base_id = int(time.time_ns())
        vehiculos_detalles = datos.get('vehiculos_detalles', [])
        for idx, v in enumerate(vehiculos_detalles):
            idvehiculo = (base_id + idx * 4 + 1) % 10000000000
            idconductor = (base_id + idx * 4 + 2) % 10000000000
            idestadoconductor = (base_id + idx * 4 + 3) % 10000000000
            idconductoraccidente = (base_id + idx * 4 + 4) % 10000000000

            kafka_repo.enviar_mensaje(topic="vehiculos_topic", clave_primaria=idvehiculo, datos_json={
                "idvehiculo": idvehiculo, "tipovehiculo": v.get('tipovehiculo', 'Automóvil'),
                "modelovehiculo": v.get('modelovehiculo', 'Genérico'),
                "categoriausovehiculo": v.get('categoriausovehiculo', 'Particular'),
                "mercanciapeligrosa": bool(v.get('mercanciapeligrosa', False)),
                "ejes": int(v.get('ejes', 2)), "activo": True, "fecha_actualizacion": ahora_ms
            }, operacion="INSERT")

            kafka_repo.enviar_mensaje(topic="conductores_topic", clave_primaria=idconductor, datos_json={
                "idconductor": idconductor, "nombres": v.get('nombres', 'Nombre'),
                "apellidos": v.get('apellidos', 'Apellido'), "identificacion": v.get('identificacion', ''),
                "genero": v.get('genero', 'M'), "tipolicencia": v.get('tipolicencia', 'B'),
                "estadolicencia": v.get('estadolicencia', 'Vigente'),
                "ciudadresidencia": v.get('ciudadresidencia', 'Quito'),
                "aniosexperiencia": int(v.get('aniosexperiencia', 0)), "activo": True,
                "fecha_actualizacion": ahora_ms
            }, operacion="INSERT")

            kafka_repo.enviar_mensaje(topic="estadosconductores_topic", clave_primaria=idestadoconductor, datos_json={
                "idestadoconductor": idestadoconductor,
                "estadosobriedad": bool(v.get('estadosobriedad', True)),
                "nivelatencion": bool(v.get('nivelatencion', True)),
                "condicionfisica": bool(v.get('condicionfisica', True)),
                "usoseguridad": bool(v.get('usoseguridad', True)),
                "activo": True, "fecha_actualizacion": ahora_ms
            }, operacion="INSERT")

            kafka_repo.enviar_mensaje(topic="conductoresaccidentes_topic", clave_primaria=idconductoraccidente, datos_json={
                "idconductoraccidente": idconductoraccidente, "idaccidente": pinot_id_accidente,
                "idconductor": idconductor, "idestadoconductor": idestadoconductor,
                "idvehiculo": idvehiculo, "activo": True, "fecha_actualizacion": ahora_ms
            }, operacion="INSERT")

        return payload_accidente
