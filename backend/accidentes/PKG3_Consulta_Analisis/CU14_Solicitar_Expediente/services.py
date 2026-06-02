import zlib
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from accidentes.shared.repositories import PinotRepository

logger = logging.getLogger(__name__)


class ExpedienteService:
    @staticmethod
    def _uuid_to_pinot_id(uuid_str: str) -> int:
        return zlib.crc32(uuid_str.encode('utf-8')) & 0x7FFFFFFF

    @staticmethod
    def obtener_detalle(accidente_id: str) -> Optional[Dict[str, Any]]:
        pinot_query = (
            f"SELECT idaccidente, latitudinicio, longitudinicio, idseveridad, activo, "
            f"numheridos, numfallecidos, numvehiculos, numvictimas, descripcion, "
            f"horainicio, horafin, codigopostal, duracionminutos, fechahoraclima, "
            f"idcalle, idciudad, idpais, idestado, idcondado, "
            f"idperiododia, idestadoclima, idelementofisico, "
            f"idtiporeportado, idreferenciaestacion, idfecha, idusuario, "
            f"fecha_actualizacion "
            f"FROM accidentes WHERE idaccidente = '{accidente_id}' LIMIT 1"
        )

        rows = []
        try:
            rows = PinotRepository.execute_query(pinot_query)
        except Exception as e:
            logger.warning(f"Error consultando detalle en Pinot: {e}")
            return None

        if not rows:
            return None

        row = rows[0]

        idcalle = row.get('idcalle')
        idciudad = row.get('idciudad')
        idseveridad = row.get('idseveridad')

        calle_nombre = "Ubicación Registrada"
        if idcalle is not None:
            try:
                calle_rows = PinotRepository.execute_query(
                    f"SELECT calle FROM calles WHERE idcalle = {idcalle} LIMIT 1"
                )
                if calle_rows:
                    calle_nombre = calle_rows[0].get('calle', calle_nombre)
            except Exception:
                pass

        ciudad_nombre = "Ubicación Registrada"
        if idciudad is not None:
            try:
                ciudad_rows = PinotRepository.execute_query(
                    f"SELECT ciudad FROM ciudades WHERE idciudad = {idciudad} LIMIT 1"
                )
                if ciudad_rows:
                    ciudad_nombre = ciudad_rows[0].get('ciudad', ciudad_nombre)
            except Exception:
                pass

        severidad_desc = "Leve"
        severidad_nivel = 1
        if idseveridad is not None:
            try:
                sev_rows = PinotRepository.execute_query(
                    f"SELECT severidad, descripcion FROM severidades WHERE idseveridad = {idseveridad} LIMIT 1"
                )
                if sev_rows:
                    severidad_nivel = sev_rows[0].get('severidad', 1)
                    severidad_desc = sev_rows[0].get('descripcion', 'Leve')
            except Exception:
                pass

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
        try:
            estado_rows = PinotRepository.execute_query(
                f"SELECT idtipoestadoincidente FROM accidentestiposestadosincidentes "
                f"WHERE idaccidente = {pinot_id_detalle} AND activo = true ORDER BY fechahoramodificado DESC LIMIT 1"
            )
            if estado_rows:
                eid = estado_rows[0].get('idtipoestadoincidente')
                estado_map = {1: "ACTIVO", 2: "EN_ATENCION", 3: "EN_ATENCION", 4: "CONTROLADO", 5: "ARCHIVADO"}
                estado_actual = estado_map.get(eid, "ACTIVO")
        except Exception:
            pass

        despachos_list = []
        try:
            desp_rows = PinotRepository.execute_query(
                f"SELECT iddespacho, idunidademergencia, fechahoradespacho, fechahoraconfirmacion, fechahorallegada "
                f"FROM despachos WHERE idaccidente = {pinot_id_detalle} LIMIT 20"
            )
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
        except Exception:
            pass

        notas_list = []
        try:
            nota_rows = PinotRepository.execute_query(
                f"SELECT idnotaaccidentes, nota, tipo, fecha_actualizacion FROM notasaccidentes "
                f"WHERE idaccidente = {pinot_id_detalle} LIMIT 50"
            )
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
        except Exception:
            pass

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
            try:
                cr = PinotRepository.execute_query(
                    f"SELECT condicionclima, temperaturaf, humedadporcentaje, visibilidadmillas, velocidadvientomph "
                    f"FROM estadoclima WHERE idestadoclima = {idestadoclima} LIMIT 1"
                )
                if cr:
                    r = cr[0]
                    clima_data = {
                        'condicion_clima': str(r.get('condicionclima', 'Despejado')),
                        'temperatura_f': r.get('temperaturaf', 72.0),
                        'humedad_porcentaje': r.get('humedadporcentaje', 50.0),
                        'visibilidad_millas': r.get('visibilidadmillas', 10.0),
                        'velocidad_viento_mph': r.get('velocidadvientomph', 0.0),
                    }
            except Exception:
                pass

        periodo_data = {
            'amaneceranochecer': 'Day', 'crepusculocivil': 'Day',
            'crepusculonautico': 'Day', 'crepusculoastronomico': 'Day',
        }
        if idperiododia:
            try:
                pr = PinotRepository.execute_query(
                    f"SELECT amaneceranochecer, crepusculocivil, crepusculonautico, crepusculoastronomico "
                    f"FROM periododia WHERE idperiododia = {idperiododia} LIMIT 1"
                )
                if pr:
                    r = pr[0]
                    periodo_data = {
                        'amaneceranochecer': str(r.get('amaneceranochecer', 'Day')),
                        'crepusculocivil': str(r.get('crepusculocivil', 'Day')),
                        'crepusculonautico': str(r.get('crepusculonautico', 'Day')),
                        'crepusculoastronomico': str(r.get('crepusculoastronomico', 'Day')),
                    }
            except Exception:
                pass

        elemento_data = {
            'cerca_cruce': False, 'cerca_semaforo': False,
            'cerca_parada': False, 'cerca_estacion': False,
            'cerca_bache': False, 'cerca_viatren': False,
        }
        if idelementofisico:
            try:
                er = PinotRepository.execute_query(
                    f"SELECT cerca_cruce, cerca_semaforo, cerca_parada, cerca_estacion, "
                    f"cerca_bache, cerca_viatren "
                    f"FROM elementofisico WHERE idelementofisico = {idelementofisico} LIMIT 1"
                )
                if er:
                    r = er[0]
                    elemento_data = {
                        'cerca_cruce': bool(r.get('cerca_cruce', False)),
                        'cerca_semaforo': bool(r.get('cerca_semaforo', False)),
                        'cerca_parada': bool(r.get('cerca_parada', False)),
                        'cerca_estacion': bool(r.get('cerca_estacion', False)),
                        'cerca_bache': bool(r.get('cerca_bache', False)),
                        'cerca_viatren': bool(r.get('cerca_viatren', False)),
                    }
            except Exception:
                pass

        estacion_data = {
            'codigoaeropuerto': 'KJFK', 'zonahoraria': 'US/Eastern',
        }
        if idreferenciaestacion:
            try:
                ar = PinotRepository.execute_query(
                    f"SELECT codigoaeropuerto, zonahoraria "
                    f"FROM referenciaestacion WHERE idreferenciaestacion = {idreferenciaestacion} LIMIT 1"
                )
                if ar:
                    r = ar[0]
                    estacion_data = {
                        'codigoaeropuerto': str(r.get('codigoaeropuerto', 'KJFK')),
                        'zonahoraria': str(r.get('zonahoraria', 'US/Eastern')),
                    }
            except Exception:
                pass

        pais_nombre = ''
        if idpais:
            try:
                pr = PinotRepository.execute_query(
                    f"SELECT pais FROM paises WHERE idpais = {idpais} LIMIT 1"
                )
                if pr:
                    pais_nombre = str(pr[0].get('pais', ''))
            except Exception:
                pass

        estado_nombre = ''
        if idestado:
            try:
                sr = PinotRepository.execute_query(
                    f"SELECT estado FROM estados WHERE idestado = {idestado} LIMIT 1"
                )
                if sr:
                    estado_nombre = str(sr[0].get('estado', ''))
            except Exception:
                pass

        condado_nombre = ''
        if idcondado:
            try:
                cr = PinotRepository.execute_query(
                    f"SELECT condado FROM condados WHERE idcondado = {idcondado} LIMIT 1"
                )
                if cr:
                    condado_nombre = str(cr[0].get('condado', ''))
            except Exception:
                pass

        tiporeportado_desc = ''
        if idtiporeportado:
            try:
                tr = PinotRepository.execute_query(
                    f"SELECT descripcion FROM tiporeportado WHERE idtiporeportado = {idtiporeportado} LIMIT 1"
                )
                if tr:
                    tiporeportado_desc = str(tr[0].get('descripcion', ''))
            except Exception:
                pass

        dims = {
            **clima_data,
            **periodo_data,
            **elemento_data,
            **estacion_data,
            'pais_nombre': pais_nombre,
            'estado_nombre': estado_nombre,
            'condado_nombre': condado_nombre,
            'tiporeportado_descripcion': tiporeportado_desc,
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
        try:
            ca_rows = PinotRepository.execute_query(
                f"SELECT idconductor, idvehiculo, idestadoconductor "
                f"FROM conductoresaccidentes WHERE idaccidente = {pinot_id} AND activo = true LIMIT 50"
            )
        except Exception:
            return []
        if not ca_rows:
            return []

        c_ids = list({r['idconductor'] for r in ca_rows if r.get('idconductor')})
        v_ids = list({r['idvehiculo'] for r in ca_rows if r.get('idvehiculo')})
        ec_ids = list({r['idestadoconductor'] for r in ca_rows if r.get('idestadoconductor')})

        conductores_map = {}
        if c_ids:
            ids_str = ", ".join(str(x) for x in c_ids)
            try:
                for r in PinotRepository.execute_query(f"SELECT idconductor, nombres, apellidos, identificacion, genero, tipolicencia, estadolicencia, ciudadresidencia, aniosexperiencia FROM conductores WHERE idconductor IN ({ids_str}) LIMIT 50"):
                    conductores_map[r['idconductor']] = r
            except Exception:
                pass

        vehiculos_map = {}
        if v_ids:
            ids_str = ", ".join(str(x) for x in v_ids)
            try:
                for r in PinotRepository.execute_query(f"SELECT idvehiculo, tipovehiculo, modelovehiculo, categoriausovehiculo, mercanciapeligrosa, ejes FROM vehiculos WHERE idvehiculo IN ({ids_str}) LIMIT 50"):
                    vehiculos_map[r['idvehiculo']] = r
            except Exception:
                pass

        estados_map = {}
        if ec_ids:
            ids_str = ", ".join(str(x) for x in ec_ids)
            try:
                for r in PinotRepository.execute_query(f"SELECT idestadoconductor, estadosobriedad, nivelatencion, condicionfisica, usoseguridad FROM estadosconductores WHERE idestadoconductor IN ({ids_str}) LIMIT 50"):
                    estados_map[r['idestadoconductor']] = r
            except Exception:
                pass

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
            try:
                foto_rows = PinotRepository.execute_query(
                    f"SELECT urlevidenciafoto, fechahora FROM evidenciasfotos "
                    f"WHERE idaccidente = {pinot_id} AND activo = true LIMIT 50"
                )
                for r in foto_rows:
                    fotos.append({
                        'url': str(r.get('urlevidenciafoto', '')),
                        'fecha': str(r.get('fechahora', ''))
                    })
            except Exception:
                pass

            clima = {}
            if detalle.get('idestadoclima'):
                try:
                    id_clima = detalle.get('idestadoclima')
                    clima_rows = PinotRepository.execute_query(
                        f"SELECT * FROM estadoclima WHERE idestadoclima = {id_clima} LIMIT 1"
                    )
                    if clima_rows:
                        r = clima_rows[0]
                        clima = {
                            'condicion': str(r.get('condicionclima', '')),
                            'temperatura_f': r.get('temperaturaf'),
                            'humedad': r.get('humedadporcentaje'),
                            'visibilidad_millas': r.get('visibilidadmillas'),
                            'velocidad_viento_mph': r.get('velocidadvientomph'),
                            'precipitacion_pulgadas': r.get('precipitacionpulgadas'),
                            'presion_pulgadas': r.get('presionpulgadas'),
                        }
                except Exception:
                    pass

            vehiculos = []
            try:
                ca_rows = PinotRepository.execute_query(
                    f"SELECT idvehiculo FROM conductoresaccidentes "
                    f"WHERE idaccidente = {pinot_id} AND activo = true LIMIT 20"
                )
                for ca in ca_rows:
                    veh_id = ca.get('idvehiculo')
                    if veh_id:
                        veh_rows = PinotRepository.execute_query(
                            f"SELECT * FROM vehiculos WHERE idvehiculo = {veh_id} LIMIT 1"
                        )
                        if veh_rows:
                            v = veh_rows[0]
                            vehiculos.append({
                                'tipo': str(v.get('tipovehiculo', '')),
                                'modelo': str(v.get('modelovehiculo', '')),
                                'categoria_uso': str(v.get('categoriausovehiculo', '')),
                                'ejes': v.get('ejes', 0),
                            })
            except Exception:
                pass

            return {
                'accidente': detalle,
                'evidencias': {'fotos': fotos},
                'clima': clima,
                'vehiculos': vehiculos,
            }
        except Exception as exc:
            logger.error('Error building expediente for %s: %s', accidente_id, exc)
            return None
