import zlib
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from accidentes.PKG1_Gestion_Accidentes.CU02_Visualizar_Mapa.repositories import (
    CalleRepository,
    CiudadRepository,
)
from accidentes.PKG3_Consulta_Analisis.CU14_Solicitar_Expediente.repositories import (
    AccidenteExpedienteRepository,
    SeveridadExpedienteRepository,
    EstadoIncidenteExpedienteRepository,
    DespachoRepository,
    NotaExpedienteRepository,
    ConductorAccidenteExpedienteRepository,
    ConductorExpedienteRepository,
    VehiculoExpedienteRepository,
    EstadoConductorExpedienteRepository,
    ClimaExpedienteRepository,
    PeriodoDiaExpedienteRepository,
    ElementoFisicoExpedienteRepository,
    EstacionExpedienteRepository,
    PaisExpedienteRepository,
    EstadoGeograficoExpedienteRepository,
    CondadoExpedienteRepository,
    TipoReportadoExpedienteRepository,
    EvidenciaFotoRepository,
)

logger = logging.getLogger(__name__)


class ExpedienteService:
    @staticmethod
    def _uuid_to_pinot_id(uuid_str: str) -> int:
        return zlib.crc32(uuid_str.encode('utf-8')) & 0x7FFFFFFF

    @staticmethod
    def obtener_detalle(accidente_id: str) -> Optional[Dict[str, Any]]:
        rows = AccidenteExpedienteRepository.find_by_id(accidente_id)
        if not rows:
            return None

        row = rows[0]

        idcalle = row.get('idcalle')
        idciudad = row.get('idciudad')
        idseveridad = row.get('idseveridad')

        calle_nombre = "Ubicación Registrada"
        if idcalle is not None:
            calles_map = CalleRepository.find_by_ids([idcalle])
            calle_nombre = calles_map.get(idcalle, calle_nombre)

        ciudad_nombre = "Ubicación Registrada"
        if idciudad is not None:
            ciudades_map = CiudadRepository.find_by_ids([idciudad])
            ciudad_nombre = ciudades_map.get(idciudad, ciudad_nombre)

        severidad_desc = "Leve"
        severidad_nivel = 1
        if idseveridad is not None:
            sev = SeveridadExpedienteRepository.find_by_id(idseveridad)
            if sev:
                severidad_nivel = sev.get('severidad', 1)
                severidad_desc = sev.get('descripcion', 'Leve')

        fa = row.get('fecha_actualizacion')
        if isinstance(fa, (int, float)):
            fa_iso = datetime.fromtimestamp(fa / 1000.0).isoformat()
        elif isinstance(fa, str) and fa:
            try:
                fa_dt = datetime.strptime(fa.split('.')[0], '%Y-%m-%d %H:%M:%S')
                fa_iso = fa_dt.isoformat()
            except (ValueError, TypeError):
                fa_iso = fa
        else:
            fa_iso = str(fa or "")

        fhc = row.get('fechahoraclima')
        if isinstance(fhc, (int, float)) and fhc > 0:
            fhc_iso = datetime.fromtimestamp(fhc / 1000.0).isoformat()
        elif isinstance(fhc, str) and fhc:
            try:
                fhc_dt = datetime.strptime(fhc.split('.')[0], '%Y-%m-%d %H:%M:%S')
                fhc_iso = fhc_dt.isoformat()
            except (ValueError, TypeError):
                fhc_iso = fhc
        else:
            fhc_iso = str(fhc or "")

        pinot_id_detalle = ExpedienteService._uuid_to_pinot_id(accidente_id)

        estado_actual = "ACTIVO"
        eid = EstadoIncidenteExpedienteRepository.find_latest_by_accidente(pinot_id_detalle)
        if eid:
            estado_map = {1: "ACTIVO", 2: "EN_ATENCION", 3: "EN_ATENCION", 4: "CONTROLADO", 5: "ARCHIVADO"}
            estado_actual = estado_map.get(eid, "ACTIVO")

        despachos_list = []
        desp_rows = DespachoRepository.find_by_accidente(pinot_id_detalle)
        for d in desp_rows:
            despachos_list.append({
                "iddespacho": d.get('iddespacho'),
                "idaccidente": str(accidente_id),
                "idunidademergencia": d.get('idunidademergencia'),
                "unidad_nombre": "",
                "tipo_unidad": "",
                "fechahoradespacho": str(d.get('fechahoradespacho') or ''),
                "fechahoraconfirmacion": str(d.get('fechahoraconfirmacion') or ''),
                "fechahorallegada": str(d.get('fechahorallegada') or '')
            })

        notas_list = []
        nota_rows = NotaExpedienteRepository.find_by_accidente(pinot_id_detalle)
        for n in nota_rows:
            nfa = n.get('fecha_actualizacion')
            if isinstance(nfa, (int, float)):
                nfa_iso = datetime.fromtimestamp(nfa / 1000.0).isoformat()
            else:
                nfa_iso = str(nfa or '')
            notas_list.append({
                "idnotaaccidentes": n.get('idnotaaccidentes'),
                "idaccidente": str(accidente_id),
                "nota": n.get('nota', ''),
                "tipo": n.get('tipo', False),
                "fecha_actualizacion": nfa_iso
            })

        vehiculos_detalles = ExpedienteService._obtener_vehiculos_desde_pinot(accidente_id)

        idestadoclima = row.get('idestadoclima')
        idperiododia = row.get('idperiododia')
        idelementofisico = row.get('idelementofisico')
        idreferenciaestacion = row.get('idreferenciaestacion')
        idpais = row.get('idpais')
        idestado = row.get('idestado')
        idcondado = row.get('idcondado')
        idtiporeportado = row.get('idtiporeportado')

        clima_data = {
            'condicion_clima': 'Despejado', 'temperatura_f': 72.0,
            'humedad_porcentaje': 50.0, 'visibilidad_millas': 10.0,
            'velocidad_viento_mph': 0.0,
        }
        if idestadoclima:
            r = ClimaExpedienteRepository.find_by_id(idestadoclima)
            if r:
                clima_data = {
                    'condicion_clima': str(r.get('condicionclima', 'Despejado')),
                    'temperatura_f': r.get('temperaturaf', 72.0),
                    'humedad_porcentaje': r.get('humedadporcentaje', 50.0),
                    'visibilidad_millas': r.get('visibilidadmillas', 10.0),
                    'velocidad_viento_mph': r.get('velocidadvientomph', 0.0),
                }

        periodo_data = {
            'amaneceranochecer': 'Day', 'crepusculocivil': 'Day',
            'crepusculonautico': 'Day', 'crepusculoastronomico': 'Day',
        }
        if idperiododia:
            r = PeriodoDiaExpedienteRepository.find_by_id(idperiododia)
            if r:
                periodo_data = {
                    'amaneceranochecer': str(r.get('amaneceranochecer', 'Day')),
                    'crepusculocivil': str(r.get('crepusculocivil', 'Day')),
                    'crepusculonautico': str(r.get('crepusculonautico', 'Day')),
                    'crepusculoastronomico': str(r.get('crepusculoastronomico', 'Day')),
                }

        elemento_data = {
            'cerca_cruce': False, 'cerca_semaforo': False,
            'cerca_parada': False, 'cerca_estacion': False,
            'cerca_bache': False, 'cerca_viatren': False,
        }
        if idelementofisico:
            r = ElementoFisicoExpedienteRepository.find_by_id(idelementofisico)
            if r:
                elemento_data = {
                    'cerca_cruce': bool(r.get('cercacruce', False)),
                    'cerca_semaforo': bool(r.get('cercasemaforo', False)),
                    'cerca_parada': bool(r.get('cercaparada', False)),
                    'cerca_estacion': bool(r.get('cercaestacion', False)),
                    'cerca_bache': bool(r.get('cercabache', False)),
                    'cerca_viatren': bool(r.get('cercaviatren', False)),
                }

        estacion_data = {
            'codigoaeropuerto': 'KJFK', 'zonahoraria': 'US/Eastern',
        }
        if idreferenciaestacion:
            r = EstacionExpedienteRepository.find_by_id(idreferenciaestacion)
            if r:
                estacion_data = {
                    'codigoaeropuerto': str(r.get('codigoaeropuerto', 'KJFK')),
                    'zonahoraria': str(r.get('zonahoraria', 'US/Eastern')),
                }

        pais_nombre = PaisExpedienteRepository.find_by_id(idpais) if idpais else ''
        estado_nombre = EstadoGeograficoExpedienteRepository.find_by_id(idestado) if idestado else ''
        condado_nombre = CondadoExpedienteRepository.find_by_id(idcondado) if idcondado else ''
        tiporeportado_desc = TipoReportadoExpedienteRepository.find_by_id(idtiporeportado) if idtiporeportado else ''

        dims = {
            **clima_data,
            **periodo_data,
            **elemento_data,
            **estacion_data,
            'pais_nombre': pais_nombre or '',
            'estado_nombre': estado_nombre or '',
            'condado_nombre': condado_nombre or '',
            'tiporeportado_descripcion': tiporeportado_desc or '',
            'idpais_id': idpais,
            'idestado_id': idestado,
            'idcondado_id': idcondado,
            'idciudad_id': idciudad,
            'idcalle_id': idcalle,
            'idtiporeportado_id': idtiporeportado,
            'idseveridad_id': severidad_nivel,
            'idperiododia_id': idperiododia,
            'idestadoclima_id': idestadoclima,
            'idreferenciaestacion_id': idreferenciaestacion,
            'idfecha_id': row.get('idfecha'),
            'idusuario_id': row.get('idusuario'),
            'idelementofisico_id': idelementofisico,
            'vehiculos_detalles': vehiculos_detalles,
        }

        return {
            "idaccidente": str(row.get('idaccidente')),
            "latitudinicio": float(row.get('latitudinicio', 0.0)),
            "longitudinicio": float(row.get('longitudinicio', 0.0)),
            "numvehiculos": int(row.get('numvehiculos', 1)),
            "numheridos": int(row.get('numheridos', 0)),
            "numfallecidos": int(row.get('numfallecidos', 0)),
            "numvictimas": int(row.get('numvictimas', 0)),
            "descripcion": str(row.get('descripcion') or ''),
            "horainicio": str(row.get('horainicio') or ''),
            "horafin": str(row.get('horafin') or ''),
            "codigopostal": str(row.get('codigopostal') or ''),
            "activo": bool(row.get('activo', True)),
            "duracionminutos": int(row.get('duracionminutos', 0)),
            "fecha_actualizacion": fa_iso,
            "fechahoraclima": fhc_iso,
            "estado_actual": estado_actual,
            "calle_nombre": calle_nombre,
            "ciudad_nombre": ciudad_nombre,
            "severidad_nivel": severidad_nivel,
            "severidad_descripcion": severidad_desc,
            "despachos": despachos_list,
            "notas": notas_list,
            **dims,
        }

    @staticmethod
    def _obtener_vehiculos_desde_pinot(accidente_id: str) -> list:
        pinot_id = ExpedienteService._uuid_to_pinot_id(accidente_id)

        ca_rows = ConductorAccidenteExpedienteRepository.find_by_accidente(pinot_id)
        if not ca_rows:
            return []

        c_ids = list({r['idconductor'] for r in ca_rows if r.get('idconductor')})
        v_ids = list({r['idvehiculo'] for r in ca_rows if r.get('idvehiculo')})
        ec_ids = list({r['idestadoconductor'] for r in ca_rows if r.get('idestadoconductor')})

        conductores_map = ConductorExpedienteRepository.find_by_ids(c_ids) if c_ids else {}
        vehiculos_map = VehiculoExpedienteRepository.find_by_ids(v_ids) if v_ids else {}
        estados_map = EstadoConductorExpedienteRepository.find_by_ids(ec_ids) if ec_ids else {}

        resultado = []
        for ca in ca_rows:
            c = conductores_map.get(ca.get('idconductor'), {})
            v = vehiculos_map.get(ca.get('idvehiculo'), {})
            ec = estados_map.get(ca.get('idestadoconductor'), {})
            resultado.append({
                "tipovehiculo": v.get('tipovehiculo', 'Automóvil'),
                "modelovehiculo": v.get('modelovehiculo', 'Genérico'),
                "categoriausovehiculo": v.get('categoriausovehiculo', 'Particular'),
                "mercanciapeligrosa": bool(v.get('mercanciapeligrosa', False)),
                "ejes": int(v.get('ejes', 2)) if v.get('ejes') else 2,
                "nombres": c.get('nombres', 'Nombre'),
                "apellidos": c.get('apellidos', 'Apellido'),
                "identificacion": c.get('identificacion', ''),
                "genero": c.get('genero', 'M'),
                "tipolicencia": c.get('tipolicencia', 'B'),
                "estadolicencia": c.get('estadolicencia', 'Vigente'),
                "ciudadresidencia": c.get('ciudadresidencia', 'Quito'),
                "aniosexperiencia": int(c.get('aniosexperiencia', 0)),
                "estadosobriedad": bool(ec.get('estadosobriedad', True)),
                "nivelatencion": bool(ec.get('nivelatencion', True)),
                "condicionfisica": bool(ec.get('condicionfisica', True)),
                "usoseguridad": bool(ec.get('usoseguridad', True)),
            })
        return resultado

    @staticmethod
    def obtener_expediente_completo(accidente_id: str) -> Optional[Dict[str, Any]]:
        try:
            detalle = ExpedienteService.obtener_detalle(accidente_id)
            if not detalle:
                return None

            pinot_id = ExpedienteService._uuid_to_pinot_id(accidente_id)

            fotos = []
            foto_rows = EvidenciaFotoRepository.find_by_accidente(pinot_id)
            for r in foto_rows:
                fotos.append({
                    'url': str(r.get('urlevidenciafoto', '')),
                    'fecha': str(r.get('fechahora', ''))
                })

            clima = {}
            if detalle.get('idestadoclima'):
                r = ClimaExpedienteRepository.find_full_by_id(detalle['idestadoclima'])
                if r:
                    clima = {
                        'condicion': str(r.get('condicionclima', '')),
                        'temperatura_f': r.get('temperaturaf'),
                        'humedad': r.get('humedadporcentaje'),
                        'visibilidad_millas': r.get('visibilidadmillas'),
                        'velocidad_viento_mph': r.get('velocidadvientomph'),
                        'precipitacion_pulgadas': r.get('precipitacionpulgadas'),
                        'presion_pulgadas': r.get('presionpulgadas'),
                    }

            vehiculos = []
            veh_ids = ConductorAccidenteExpedienteRepository.find_vehiculo_ids_by_accidente(pinot_id)
            for veh_id in veh_ids:
                v = VehiculoExpedienteRepository.find_by_id(veh_id)
                if v:
                    vehiculos.append({
                        'tipo': str(v.get('tipovehiculo', '')),
                        'modelo': str(v.get('modelovehiculo', '')),
                        'categoria_uso': str(v.get('categoriausovehiculo', '')),
                        'ejes': v.get('ejes', 0),
                    })

            return {
                'accidente': detalle,
                'evidencias': {'fotos': fotos},
                'clima': clima,
                'vehiculos': vehiculos,
            }
        except Exception as exc:
            logger.error('Error building expediente for %s: %s', accidente_id, exc)
            return None
