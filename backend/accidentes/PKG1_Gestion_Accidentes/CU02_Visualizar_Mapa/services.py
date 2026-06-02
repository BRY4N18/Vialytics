import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from accidentes.shared.repositories import PinotRepository

logger = logging.getLogger(__name__)


class MapaService:
    @staticmethod
    def obtener_accidentes_mapa(filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        severidad_param = filtros.get('severidad')
        horas = filtros.get('horas')

        sev_rows = PinotRepository.execute_query(
            "SELECT idseveridad, severidad, descripcion FROM severidades WHERE activo = true LIMIT 10"
        )
        sev_map = {}
        sev_id_for_level = {}
        for s in sev_rows:
            sid = s.get('idseveridad')
            slevel = s.get('severidad', 0)
            sev_map[sid] = slevel
            sev_id_for_level[slevel] = sid

        idpais = filtros.get('idpais')
        idestado = filtros.get('idestado')
        idcondado = filtros.get('idcondado')
        idciudad = filtros.get('idciudad')
        idcalle = filtros.get('idcalle')

        idcalles_filter = None
        if idcalle:
            idcalles_filter = [int(idcalle)]
        elif idciudad:
            try:
                ciudad_rows = PinotRepository.execute_query(
                    f"SELECT idcalle FROM calles WHERE activo = true AND ciudad = '{idciudad}' LIMIT 5000"
                )
                idcalles_filter = [r['idcalle'] for r in ciudad_rows if r.get('idcalle') is not None]
            except Exception as e:
                logger.warning(f"Error resolving calles from ciudad: {e}")
        elif idcondado:
            try:
                ciudad_rows = PinotRepository.execute_query(
                    f"SELECT idciudad, ciudad FROM ciudades WHERE activo = true AND condado = '{idcondado}' LIMIT 2000"
                )
                ciudades_nombres = [r['ciudad'] for r in ciudad_rows if r.get('ciudad') is not None]
                if ciudades_nombres:
                    ci_str = ', '.join(f"'{c}'" for c in ciudades_nombres)
                    calle_rows = PinotRepository.execute_query(
                        f"SELECT idcalle FROM calles WHERE activo = true AND ciudad IN ({ci_str}) LIMIT 5000"
                    )
                    idcalles_filter = [r['idcalle'] for r in calle_rows if r.get('idcalle') is not None]
            except Exception as e:
                logger.warning(f"Error resolving calles from condado: {e}")
        elif idestado:
            try:
                condado_rows = PinotRepository.execute_query(
                    f"SELECT condado FROM condados WHERE activo = true AND estado = '{idestado}' LIMIT 2000"
                )
                condados = [r['condado'] for r in condado_rows if r.get('condado') is not None]
                if condados:
                    co_str = ', '.join(f"'{c}'" for c in condados)
                    ciudad_rows = PinotRepository.execute_query(
                        f"SELECT idciudad, ciudad FROM ciudades WHERE activo = true AND condado IN ({co_str}) LIMIT 2000"
                    )
                    ciudades_nombres = [r['ciudad'] for r in ciudad_rows if r.get('ciudad') is not None]
                    if ciudades_nombres:
                        ci_str = ', '.join(f"'{c}'" for c in ciudades_nombres)
                        calle_rows = PinotRepository.execute_query(
                            f"SELECT idcalle FROM calles WHERE activo = true AND ciudad IN ({ci_str}) LIMIT 5000"
                        )
                        idcalles_filter = [r['idcalle'] for r in calle_rows if r.get('idcalle') is not None]
            except Exception as e:
                logger.warning(f"Error resolving calles from estado: {e}")
        elif idpais:
            try:
                estado_rows = PinotRepository.execute_query(
                    f"SELECT estado FROM estados WHERE activo = true AND pais = '{idpais}' LIMIT 2000"
                )
                estados_list = [r['estado'] for r in estado_rows if r.get('estado') is not None]
                if estados_list:
                    es_str = ', '.join(f"'{e}'" for e in estados_list)
                    condado_rows = PinotRepository.execute_query(
                        f"SELECT condado FROM condados WHERE activo = true AND estado IN ({es_str}) LIMIT 2000"
                    )
                    condados = [r['condado'] for r in condado_rows if r.get('condado') is not None]
                    if condados:
                        co_str = ', '.join(f"'{c}'" for c in condados)
                        ciudad_rows = PinotRepository.execute_query(
                            f"SELECT idciudad, ciudad FROM ciudades WHERE activo = true AND condado IN ({co_str}) LIMIT 2000"
                        )
                        ciudades_nombres = [r['ciudad'] for r in ciudad_rows if r.get('ciudad') is not None]
                        if ciudades_nombres:
                            ci_str = ', '.join(f"'{c}'" for c in ciudades_nombres)
                            calle_rows = PinotRepository.execute_query(
                                f"SELECT idcalle FROM calles WHERE activo = true AND ciudad IN ({ci_str}) LIMIT 5000"
                            )
                            idcalles_filter = [r['idcalle'] for r in calle_rows if r.get('idcalle') is not None]
            except Exception as e:
                logger.warning(f"Error resolving calles from pais: {e}")

        query = (
            "SELECT idaccidente, latitudinicio, longitudinicio, idseveridad, activo, "
            "numheridos, numfallecidos, descripcion, idcalle, idciudad, fecha_actualizacion "
            "FROM accidentes WHERE activo = true"
        )

        if severidad_param and int(severidad_param) in sev_id_for_level:
            severidad_hash = sev_id_for_level[int(severidad_param)]
            query += f" AND idseveridad = {severidad_hash}"

        if idcalles_filter is not None:
            if idcalles_filter:
                query += f" AND idcalle IN ({', '.join(map(str, idcalles_filter))})"
            else:
                query += " AND 1 = 0"

        fecha_inicio = filtros.get('fecha_inicio')
        fecha_fin = filtros.get('fecha_fin')

        start_str = fecha_inicio
        end_str = fecha_fin

        if not start_str and filtros.get('solo_ultima_semana'):
            from datetime import timedelta
            start_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            end_str = datetime.now().strftime("%Y-%m-%d")

        if start_str or end_str:
            date_ids = []
            pinot_date_query = "SELECT idfecha FROM fechas WHERE activo = true"
            if start_str:
                pinot_date_query += f" AND fechacompleta >= '{start_str}'"
            if end_str:
                pinot_date_query += f" AND fechacompleta <= '{end_str}'"
            pinot_date_query += " LIMIT 5000"
            try:
                pinot_date_rows = PinotRepository.execute_query(pinot_date_query)
                for r in pinot_date_rows:
                    fid = r.get('idfecha')
                    if fid is not None:
                        date_ids.append(fid)
            except Exception as e:
                logger.warning(f"Error querying dates from Pinot: {e}")

            date_ids = list(set(date_ids))

            start_ms = 0
            end_ms = 0
            if start_str:
                start_ms = int(datetime.strptime(start_str, "%Y-%m-%d").timestamp() * 1000)
            if end_str:
                end_ms = int(datetime.strptime(end_str + " 23:59:59", "%Y-%m-%d %H:%M:%S").timestamp() * 1000)

            clauses = []
            if date_ids:
                clauses.append(f"idfecha IN ({', '.join(map(str, date_ids))})")

            legacy_clause = []
            legacy_clause.append("idfecha <= 1")
            if start_ms:
                legacy_clause.append(f"fecha_actualizacion >= {start_ms}")
            if end_ms:
                legacy_clause.append(f"fecha_actualizacion <= {end_ms}")
            legacy_clause_str = "(" + " AND ".join(legacy_clause) + ")"
            clauses.append(legacy_clause_str)

            query += f" AND ({' OR '.join(clauses)})"

        query += " LIMIT 500"

        rows = []
        try:
            rows = PinotRepository.execute_query(query)
        except Exception as e:
            logger.warning(f"Error consultando mapa en Pinot: {e}")

        if rows:
            calle_ids = {row.get('idcalle') for row in rows if row.get('idcalle') is not None}
            ciudad_ids = {row.get('idciudad') for row in rows if row.get('idciudad') is not None}

            calles_map = {}
            if calle_ids:
                try:
                    ids_str = ", ".join(str(cid) for cid in calle_ids)
                    calle_rows = PinotRepository.execute_query(
                        f"SELECT idcalle, calle FROM calles WHERE idcalle IN ({ids_str}) LIMIT 1000"
                    )
                    calles_map = {r['idcalle']: r.get('calle', '') for r in calle_rows}
                except Exception:
                    pass

            ciudades_map = {}
            if ciudad_ids:
                try:
                    ids_str = ", ".join(str(cid) for cid in ciudad_ids)
                    ciudad_rows = PinotRepository.execute_query(
                        f"SELECT idciudad, ciudad FROM ciudades WHERE idciudad IN ({ids_str}) LIMIT 1000"
                    )
                    ciudades_map = {r['idciudad']: r.get('ciudad', '') for r in ciudad_rows}
                except Exception:
                    pass

            resultados = []
            for row in rows:
                idaccidente = row.get('idaccidente')

                lat = float(row.get('latitudinicio')) if row.get('latitudinicio') is not None else 0.0
                lng = float(row.get('longitudinicio')) if row.get('longitudinicio') is not None else 0.0

                sev_id = row.get('idseveridad')
                sev = sev_map.get(sev_id, 1)

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

                idcalle = row.get('idcalle')
                idciudad = row.get('idciudad')

                calle_nombre = calles_map.get(idcalle, "Ubicación Registrada")
                ciudad_nombre = ciudades_map.get(idciudad, "Ubicación Registrada")

                public_mode = filtros.get('public', False)
                resultados.append({
                    "idaccidente": str(idaccidente),
                    "latitudinicio": lat,
                    "longitudinicio": lng,
                    "severidad_nivel": sev,
                    "estado_actual": "ACTIVO",
                    "numheridos": 0 if public_mode else int(row.get('numheridos', 0)),
                    "numfallecidos": 0 if public_mode else int(row.get('numfallecidos', 0)),
                    "fecha_actualizacion": fa_iso,
                    "descripcion": "" if public_mode else str(row.get('descripcion') or ''),
                    "calle_nombre": calle_nombre,
                    "ciudad_nombre": ciudad_nombre
                })
            return resultados

        return []
