import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from accidentes.shared.utils import uuid_to_pinot_id
from accidentes.PKG1_Gestion_Accidentes.CU02_Visualizar_Mapa.repositories import (
    CalleRepository,
    CiudadRepository,
    SeveridadRepository,
)
from accidentes.shared.catalogo_repositories import (
    ClimaCatalogoRepository,
    PeriodoDiaCatalogoRepository,
    ElementoFisicoCatalogoRepository,
    PaisCatalogoRepository,
    EstadoCatalogoRepository,
    CondadoCatalogoRepository,
    TipoReportadoCatalogoRepository,
)
from accidentes.PKG3_Consulta_Analisis.CU14_Solicitar_Expediente.repositories import (
    AccidenteExpedienteRepository,
    EstadoIncidenteExpedienteRepository,
    DespachoRepository,
    NotaExpedienteRepository,
    ConductorAccidenteExpedienteRepository,
    ConductorExpedienteRepository,
    VehiculoExpedienteRepository,
    EstadoConductorExpedienteRepository,
    EvidenciaFotoRepository,
)

logger = logging.getLogger(__name__)


class ExpedienteService:
    @staticmethod
    def _timestamp_to_iso(ts) -> str:
        if isinstance(ts, (int, float)) and ts > 0:
            return datetime.fromtimestamp(ts / 1000.0).isoformat()
        if isinstance(ts, str) and ts:
            try:
                return datetime.strptime(ts.split('.')[0], '%Y-%m-%d %H:%M:%S').isoformat()
            except (ValueError, TypeError):
                return ts
        return str(ts or "")

    @staticmethod
    def _build_dims_from_row(row: Dict[str, Any]) -> Dict[str, Any]:
        dim_ids = {
            'idestadoclima': row.get('idestadoclima'),
            'idperiododia': row.get('idperiododia'),
            'idelementofisico': row.get('idelementofisico'),
            'idpais': row.get('idpais'),
            'idestado': row.get('idestado'),
            'idcondado': row.get('idcondado'),
            'idtiporeportado': row.get('idtiporeportado'),
        }
        valid_ids = {k: v for k, v in dim_ids.items() if v is not None}
        if not valid_ids:
            return {}

        all_climas = ClimaCatalogoRepository.get_all()
        all_periodos = PeriodoDiaCatalogoRepository.get_all()
        all_elementos = ElementoFisicoCatalogoRepository.get_all()

        clima_map = {c['idestadoclima']: c for c in all_climas}
        periodo_map = {p['idperiododia']: p for p in all_periodos}
        elemento_map = {e['idelementofisico']: e for e in all_elementos}
        pais_map = {p['idpais']: p for p in PaisCatalogoRepository.get_all()}

        dims = {}

        c = clima_map.get(valid_ids.get('idestadoclima'))
        if c:
            dims.update({
                'condicion_clima': str(c.get('condicionclima', 'Despejado')),
                'temperatura_f': c.get('temperaturaf', 72.0),
                'humedad_porcentaje': c.get('humedadporcentaje', 50.0),
                'visibilidad_millas': c.get('visibilidadmillas', 10.0),
                'velocidad_viento_mph': c.get('velocidadvientomph', 0.0),
            })

        p = periodo_map.get(valid_ids.get('idperiododia'))
        if p:
            dims.update({
                'amaneceranochecer': str(p.get('amaneceranochecer', 'Day')),
                'crepusculocivil': str(p.get('crepusculocivil', 'Day')),
                'crepusculonautico': str(p.get('crepusculonautico', 'Day')),
                'crepusculoastronomico': str(p.get('crepusculoastronomico', 'Day')),
            })

        ef = elemento_map.get(valid_ids.get('idelementofisico'))
        if ef:
            dims.update({
                'cerca_cruce': bool(ef.get('cercacruce', False)),
                'cerca_semaforo': bool(ef.get('cercasemaforo', False)),
                'cerca_parada': bool(ef.get('cercaparada', False)),
                'cerca_estacion': bool(ef.get('cercaestacion', False)),
                'cerca_bache': bool(ef.get('cercabache', False)),
                'cerca_viatren': bool(ef.get('cercaviatren', False)),
            })

        pa = pais_map.get(valid_ids.get('idpais'))
        if pa:
            dims['pais_nombre'] = str(pa.get('pais', ''))

        if valid_ids.get('idestado'):
            estados = EstadoCatalogoRepository.get_all()
            est_map = {e['idestado']: e for e in estados}
            est = est_map.get(valid_ids['idestado'])
            if est:
                dims['estado_nombre'] = str(est.get('estado', ''))

        if valid_ids.get('idcondado'):
            condados = CondadoCatalogoRepository.get_all()
            cond_map = {c['idcondado']: c for c in condados}
            cond = cond_map.get(valid_ids['idcondado'])
            if cond:
                dims['condado_nombre'] = str(cond.get('condado', ''))

        if valid_ids.get('idtiporeportado'):
            tipos = TipoReportadoCatalogoRepository.get_all()
            tipo_map = {t['idtiporeportado']: t for t in tipos}
            tr = tipo_map.get(valid_ids['idtiporeportado'])
            if tr:
                dims['tiporeportado_descripcion'] = str(tr.get('tiporeportado', ''))

        dims.setdefault('condicion_clima', 'Despejado')
        dims.setdefault('temperatura_f', 72.0)
        dims.setdefault('humedad_porcentaje', 50.0)
        dims.setdefault('visibilidad_millas', 10.0)
        dims.setdefault('velocidad_viento_mph', 0.0)
        dims.setdefault('amaneceranochecer', 'Day')
        dims.setdefault('crepusculocivil', 'Day')
        dims.setdefault('crepusculonautico', 'Day')
        dims.setdefault('crepusculoastronomico', 'Day')
        dims.setdefault('cerca_cruce', False)
        dims.setdefault('cerca_semaforo', False)
        dims.setdefault('cerca_parada', False)
        dims.setdefault('cerca_estacion', False)
        dims.setdefault('cerca_bache', False)
        dims.setdefault('cerca_viatren', False)
        dims.setdefault('pais_nombre', '')
        dims.setdefault('estado_nombre', '')
        dims.setdefault('condado_nombre', '')
        dims.setdefault('tiporeportado_descripcion', '')

        return dims

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
            sev_rows = SeveridadRepository.get_all()
            for s in sev_rows:
                if s.get('idseveridad') == idseveridad:
                    severidad_nivel = s.get('severidad', 1)
                    severidad_desc = s.get('descripcion', 'Leve')
                    break

        fa_iso = ExpedienteService._timestamp_to_iso(row.get('fecha_actualizacion'))
        fhc_iso = ExpedienteService._timestamp_to_iso(row.get('fechahoraclima'))

        pinot_id_detalle = uuid_to_pinot_id(accidente_id)

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
            nfa_iso = ExpedienteService._timestamp_to_iso(n.get('fecha_actualizacion'))
            notas_list.append({
                "idnotaaccidentes": n.get('idnotaaccidentes'),
                "idaccidente": str(accidente_id),
                "nota": n.get('nota', ''),
                "tipo": n.get('tipo', False),
                "fecha_actualizacion": nfa_iso
            })

        vehiculos_detalles = ExpedienteService._obtener_vehiculos_desde_pinot(accidente_id)

        dims = ExpedienteService._build_dims_from_row(row)
        dims.update({
            'idpais_id': row.get('idpais'),
            'idestado_id': row.get('idestado'),
            'idcondado_id': row.get('idcondado'),
            'idciudad_id': idciudad,
            'idcalle_id': idcalle,
            'idtiporeportado_id': row.get('idtiporeportado'),
            'idseveridad_id': severidad_nivel,
            'idperiododia_id': row.get('idperiododia'),
            'idestadoclima_id': row.get('idestadoclima'),
            'idreferenciaestacion_id': row.get('idreferenciaestacion'),
            'idfecha_id': row.get('idfecha'),
            'idusuario_id': row.get('idusuario'),
            'idelementofisico_id': row.get('idelementofisico'),
            'vehiculos_detalles': vehiculos_detalles,
        })

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
        pinot_id = uuid_to_pinot_id(accidente_id)

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

            pinot_id = uuid_to_pinot_id(accidente_id)

            fotos = []
            foto_rows = EvidenciaFotoRepository.find_by_accidente(pinot_id)
            for r in foto_rows:
                fotos.append({
                    'url': str(r.get('urlevidenciafoto', '')),
                    'fecha': str(r.get('fechahora', ''))
                })

            clima = {}
            id_clima = detalle.get('idestadoclima_id')
            if id_clima:
                all_climas = ClimaCatalogoRepository.get_all()
                for c in all_climas:
                    if c.get('idestadoclima') == id_clima:
                        clima = {
                            'condicion': str(c.get('condicionclima', '')),
                            'temperatura_f': c.get('temperaturaf'),
                            'humedad': c.get('humedadporcentaje'),
                            'visibilidad_millas': c.get('visibilidadmillas'),
                            'velocidad_viento_mph': c.get('velocidadvientomph'),
                            'precipitacion_pulgadas': c.get('precipitacionpulgadas'),
                            'presion_pulgadas': c.get('presionpulgadas'),
                        }
                        break

            vehiculos = []
            veh_ids = ConductorAccidenteExpedienteRepository.find_vehiculo_ids_by_accidente(pinot_id)
            if veh_ids:
                vehiculos_map = VehiculoExpedienteRepository.find_by_ids(veh_ids)
                for veh_id in veh_ids:
                    v = vehiculos_map.get(veh_id)
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
