import uuid
import time
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from accidentes.shared.utils import uuid_to_pinot_id
from accidentes.PKG1_Gestion_Accidentes.CU06_Asignar_Severidad.services import SeveridadService
from accidentes.PKG1_Gestion_Accidentes.CU01_Registrar_Accidente.repositories import (
    ClimaRepository,
    EstacionRepository,
    AccidenteReadRepository,
    AccidenteWriteRepository,
    VehiculoRepository,
    ConductorRepository,
    EstadoConductorRepository,
    ConductorAccidenteRepository,
    AccidenteEstadoRepository,
    NotaRepository,
)

logger = logging.getLogger(__name__)


class AccidenteRegistroService:

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

        pinot_id_pais = int(datos.get('idpais_id', 1))
        pinot_id_estado = int(datos.get('idestado_id', 1))
        pinot_id_condado = int(datos.get('idcondado_id', 1))
        pinot_id_ciudad = int(datos.get('idciudad_id', 1))
        pinot_id_calle = int(datos.get('idcalle_id', 1))
        pinot_id_severidad = AccidenteRegistroService._obtener_pinot_id_severidad(severidad)
        pinot_id_clima = ClimaRepository.find_id_by_condicion(datos.get('condicion_clima', ''))
        pinot_id_estacion = EstacionRepository.find_id_by_codigo(datos.get('codigoaeropuerto', ''))
        pinot_tiporeportado = int(datos.get('idtiporeportado_id', 1))
        pinot_fecha = int(datos.get('idfecha_id', 1))
        pinot_periododia = int(datos.get('idperiododia_id', 1))
        pinot_elementofisico = int(datos.get('idelementofisico_id', 1))
        pinot_usuario = int(datos.get('idusuario_id', 1))

        ahora_ms = int(time.time() * 1000)
        horainicio = datetime.now().strftime("%H:%M:%S")
        pinot_id_accidente = uuid_to_pinot_id(idaccidente)

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
        }
        AccidenteWriteRepository.create(payload_accidente)

        vehiculos_detalles = datos.get('vehiculos_detalles', [])
        for idx, v in enumerate(vehiculos_detalles):
            idvehiculo = uuid.uuid4().int % 10000000000
            idconductor = uuid.uuid4().int % 10000000000
            idestadoconductor = uuid.uuid4().int % 10000000000
            idconductoraccidente = uuid.uuid4().int % 10000000000

            VehiculoRepository.create({
                "idvehiculo": idvehiculo,
                "tipovehiculo": v.get('tipovehiculo', 'Automóvil'),
                "modelovehiculo": v.get('modelovehiculo', 'Genérico'),
                "categoriausovehiculo": v.get('categoriausovehiculo', 'Particular'),
                "mercanciapeligrosa": bool(v.get('mercanciapeligrosa', False)),
                "ejes": int(v.get('ejes', 2)),
                "activo": True,
            })
            ConductorRepository.create({
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
            })
            EstadoConductorRepository.create({
                "idestadoconductor": idestadoconductor,
                "estadosobriedad": bool(v.get('estadosobriedad', True)),
                "nivelatencion": bool(v.get('nivelatencion', True)),
                "condicionfisica": bool(v.get('condicionfisica', True)),
                "usoseguridad": bool(v.get('usoseguridad', True)),
                "activo": True,
            })
            ConductorAccidenteRepository.create({
                "idconductoraccidente": idconductoraccidente,
                "idaccidente": pinot_id_accidente,
                "idconductor": idconductor,
                "idestadoconductor": idestadoconductor,
                "idvehiculo": idvehiculo,
                "activo": True,
            })

        id_estado_rel = int(time.time() * 1000) % 1000000000
        AccidenteEstadoRepository.create({
            "idaccidentetipoestadoincidente": id_estado_rel,
            "idaccidente": pinot_id_accidente,
            "idtipoestadoincidente": 1,
            "activo": True,
            "fechahoramodificado": ahora_ms,
        })

        nota_inicial = datos.get('nota_inicial')
        if nota_inicial:
            id_nota = int(time.time() * 1000) % 1000000000
            NotaRepository.create({
                "idnotaaccidentes": id_nota,
                "idaccidente": pinot_id_accidente,
                "idusuario": pinot_usuario,
                "nota": nota_inicial,
                "tipo": True,
                "activo": True,
            })

        return payload_accidente

    @staticmethod
    def actualizar_accidente(accidente_id: str, datos: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not AccidenteReadRepository.exists_by_id(accidente_id):
            return None

        numheridos = int(datos.get('numheridos', 0))
        numfallecidos = int(datos.get('numfallecidos', 0))
        numvehiculos = int(datos.get('numvehiculos', 1))

        severidad = datos.get('idseveridad_id')
        if severidad is None or severidad == '' or int(severidad) == 0:
            severidad = SeveridadService.calcular(numheridos, numfallecidos, numvehiculos)
        else:
            severidad = int(severidad)

        pinot_id_pais = int(datos.get('idpais_id', 1))
        pinot_id_estado = int(datos.get('idestado_id', 1))
        pinot_id_condado = int(datos.get('idcondado_id', 1))
        pinot_id_ciudad = int(datos.get('idciudad_id', 1))
        pinot_id_calle = int(datos.get('idcalle_id', 1))
        pinot_id_severidad = AccidenteRegistroService._obtener_pinot_id_severidad(severidad)
        pinot_id_clima = ClimaRepository.find_id_by_condicion(datos.get('condicion_clima', ''))
        pinot_id_estacion = EstacionRepository.find_id_by_codigo(datos.get('codigoaeropuerto', ''))
        pinot_tiporeportado = int(datos.get('idtiporeportado_id', 1))
        pinot_fecha = int(datos.get('idfecha_id', 1))
        pinot_periododia = int(datos.get('idperiododia_id', 1))
        pinot_elementofisico = int(datos.get('idelementofisico_id', 1))
        pinot_usuario = int(datos.get('idusuario_id', 1))

        ahora_ms = int(time.time() * 1000)
        pinot_id_accidente = uuid_to_pinot_id(accidente_id)

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
        }

        AccidenteWriteRepository.update(accidente_id, payload_accidente)

        vehiculos_detalles = datos.get('vehiculos_detalles', [])
        for idx, v in enumerate(vehiculos_detalles):
            idvehiculo = uuid.uuid4().int % 10000000000
            idconductor = uuid.uuid4().int % 10000000000
            idestadoconductor = uuid.uuid4().int % 10000000000
            idconductoraccidente = uuid.uuid4().int % 10000000000

            VehiculoRepository.create({
                "idvehiculo": idvehiculo,
                "tipovehiculo": v.get('tipovehiculo', 'Automóvil'),
                "modelovehiculo": v.get('modelovehiculo', 'Genérico'),
                "categoriausovehiculo": v.get('categoriausovehiculo', 'Particular'),
                "mercanciapeligrosa": bool(v.get('mercanciapeligrosa', False)),
                "ejes": int(v.get('ejes', 2)),
                "activo": True,
            })
            ConductorRepository.create({
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
            })
            EstadoConductorRepository.create({
                "idestadoconductor": idestadoconductor,
                "estadosobriedad": bool(v.get('estadosobriedad', True)),
                "nivelatencion": bool(v.get('nivelatencion', True)),
                "condicionfisica": bool(v.get('condicionfisica', True)),
                "usoseguridad": bool(v.get('usoseguridad', True)),
                "activo": True,
            })
            ConductorAccidenteRepository.create({
                "idconductoraccidente": idconductoraccidente,
                "idaccidente": pinot_id_accidente,
                "idconductor": idconductor,
                "idestadoconductor": idestadoconductor,
                "idvehiculo": idvehiculo,
                "activo": True,
            })

        return payload_accidente
