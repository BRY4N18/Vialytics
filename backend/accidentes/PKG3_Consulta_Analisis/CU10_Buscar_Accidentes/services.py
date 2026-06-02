import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from accidentes.shared.repositories import PinotRepository

logger = logging.getLogger(__name__)


class BusquedaService:
    @staticmethod
    def obtener_accidentes_paginados(filtros: Dict[str, Any]) -> Dict[str, Any]:
        page = int(filtros.get('page', 1))
        page_size = int(filtros.get('page_size', 8))
        offset = (page - 1) * page_size

        search = filtros.get('search', '').strip()
        severidad_param = filtros.get('severidad')
        estado_param = filtros.get('estado', '')
        solo_activos = filtros.get('solo_activos', False)
        ciudad_id = filtros.get('ciudad_id')
        min_heridos = filtros.get('min_heridos')
        max_heridos = filtros.get('max_heridos')
        min_fallecidos = filtros.get('min_fallecidos')
        max_fallecidos = filtros.get('max_fallecidos')
        fecha_desde = filtros.get('fecha_desde', '')
        fecha_hasta = filtros.get('fecha_hasta', '')
        matricula = filtros.get('matricula', '').strip()

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

        where_clauses = ["activo = true"]

        if severidad_param and int(severidad_param) in sev_id_for_level:
            sev_hash = sev_id_for_level[int(severidad_param)]
            where_clauses.append(f"idseveridad = {sev_hash}")

        if ciudad_id is not None:
            where_clauses.append(f"idciudad = {ciudad_id}")

        if min_heridos is not None:
            where_clauses.append(f"numheridos >= {min_heridos}")
        if max_heridos is not None:
            where_clauses.append(f"numheridos <= {max_heridos}")

        if min_fallecidos is not None:
            where_clauses.append(f"numfallecidos >= {min_fallecidos}")
        if max_fallecidos is not None:
            where_clauses.append(f"numfallecidos <= {max_fallecidos}")

        if fecha_desde:
            try:
                fd = datetime.strptime(fecha_desde, '%Y-%m-%d')
                fd_ms = int(fd.timestamp() * 1000)
                where_clauses.append(f"fecha_actualizacion >= {fd_ms}")
            except (ValueError, OSError):
                pass

        if fecha_hasta:
            try:
                fh = datetime.strptime(fecha_hasta, '%Y-%m-%d')
                fh_ms = int(fh.timestamp() * 1000) + 86399999
                where_clauses.append(f"fecha_actualizacion <= {fh_ms}")
            except (ValueError, OSError):
                pass

        if search:
            search_escaped = search.replace("'", "''")
            clauses = [
                f"LOWER(descripcion) LIKE '%{search_escaped.lower()}%'",
                f"LOWER(idaccidente) LIKE '%{search_escaped.lower()}%'"
            ]

            calle_rows = PinotRepository.execute_query(
                f"SELECT idcalle FROM calles WHERE LOWER(calle) LIKE '%{search_escaped.lower()}%' LIMIT 100"
            )
            if calle_rows:
                calle_ids = [str(r['idcalle']) for r in calle_rows]
                clauses.append(f"idcalle IN ({', '.join(calle_ids)})")

            ciudad_rows = PinotRepository.execute_query(
                f"SELECT idciudad FROM ciudades WHERE LOWER(ciudad) LIKE '%{search_escaped.lower()}%' LIMIT 100"
            )
            if ciudad_rows:
                ciudad_ids = [str(r['idciudad']) for r in ciudad_rows]
                clauses.append(f"idciudad IN ({', '.join(ciudad_ids)})")

            where_clauses.append(f"({' OR '.join(clauses)})")

        if matricula:
            search_escaped = matricula.replace("'", "''")
            veh_rows = PinotRepository.execute_query(
                f"SELECT idvehiculo FROM vehiculos WHERE "
                f"LOWER(modelovehiculo) LIKE '%{search_escaped.lower()}%' "
                f"OR LOWER(tipovehiculo) LIKE '%{search_escaped.lower()}%' "
                f"LIMIT 500"
            )
            if veh_rows:
                veh_ids = [str(r['idvehiculo']) for r in veh_rows]
                ca_rows = PinotRepository.execute_query(
                    f"SELECT DISTINCT idaccidente FROM conductoresaccidentes "
                    f"WHERE idvehiculo IN ({', '.join(veh_ids)}) LIMIT 500"
                )
                if ca_rows:
                    acc_ids = [f"'{r['idaccidente']}'" for r in ca_rows]
                    where_clauses.append(f"idaccidente IN ({', '.join(acc_ids)})")

        if estado_param or solo_activos:
            estado_ids = []
            if estado_param == 'ACTIVO':
                estado_ids = [1]
            elif estado_param == 'EN_ATENCION':
                estado_ids = [2, 3]
            elif estado_param == 'CONTROLADO':
                estado_ids = [4]
            elif estado_param == 'ARCHIVADO':
                estado_ids = [5]

            if solo_activos:
                estado_ids = [1, 2, 3]

            if estado_ids:
                todos_estados = PinotRepository.execute_query(
                    f"SELECT idaccidente, idtipoestadoincidente, fechahoramodificado "
                    f"FROM accidentestiposestadosincidentes "
                    f"WHERE activo = true LIMIT 100000"
                )
                if todos_estados:
                    ultimo_estado_por_accidente = {}
                    for r in todos_estados:
                        aid = r.get('idaccidente')
                        eid = r.get('idtipoestadoincidente')
                        fhm = r.get('fechahoramodificado', 0)
                        if aid and eid:
                            prev = ultimo_estado_por_accidente.get(aid)
                            if prev is None or fhm > prev['fecha']:
                                ultimo_estado_por_accidente[aid] = {'id': eid, 'fecha': fhm}
                    acc_ids = set()
                    for aid, info in ultimo_estado_por_accidente.items():
                        if info['id'] in estado_ids:
                            acc_ids.add(f"'{aid}'")
                    if acc_ids:
                        where_clauses.append(f"idaccidente IN ({', '.join(acc_ids)})")
                    else:
                        where_clauses.append("idaccidente = 'NONE'")
                else:
                    where_clauses.append("idaccidente = 'NONE'")

        where_str = " AND ".join(where_clauses)

        count_query = f"SELECT count(*) FROM accidentes WHERE {where_str}"
        total_records = 0
        try:
            count_res = PinotRepository.execute_query(count_query)
            if count_res:
                total_records = int(count_res[0].get('count(*)', 0))
        except Exception as e:
            logger.warning(f"Error al contar en Pinot: {e}")

        query = (
            f"SELECT idaccidente, latitudinicio, longitudinicio, idseveridad, activo, "
            f"numheridos, numfallecidos, numvehiculos, numvictimas, descripcion, idcalle, idciudad, fecha_actualizacion "
            f"FROM accidentes WHERE {where_str} "
            f"ORDER BY fecha_actualizacion DESC "
            f"LIMIT {page_size} OFFSET {offset}"
        )

        rows = []
        try:
            rows = PinotRepository.execute_query(query)
        except Exception as e:
            logger.error(f"Error consultando listado paginado en Pinot: {e}")

        resultados = []
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

            acc_ids = [f"'{r['idaccidente']}'" for r in rows if r.get('idaccidente')]
            estado_map = {}
            if acc_ids:
                estado_rows = PinotRepository.execute_query(
                    f"SELECT idaccidente, idtipoestadoincidente, fechahoramodificado "
                    f"FROM accidentestiposestadosincidentes "
                    f"WHERE idaccidente IN ({', '.join(acc_ids)}) AND activo = true LIMIT 500"
                )
                estados_catalogo = {
                    1: "ACTIVO",
                    2: "EN_ATENCION",
                    3: "EN_ATENCION",
                    4: "CONTROLADO",
                    5: "ARCHIVADO"
                }
                latest_estado = {}
                for r in estado_rows:
                    aid = r.get('idaccidente')
                    eid = r.get('idtipoestadoincidente')
                    fhm = r.get('fechahoramodificado', 0)
                    if aid and eid:
                        if aid not in latest_estado or fhm > latest_estado[aid]['fecha']:
                            latest_estado[aid] = {'id': eid, 'fecha': fhm}
                for aid, info in latest_estado.items():
                    estado_map[aid] = estados_catalogo.get(info['id'], "ACTIVO")

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
                estado_actual = estado_map.get(idaccidente, "ACTIVO")

                resultados.append({
                    "idaccidente": str(idaccidente),
                    "latitudinicio": lat,
                    "longitudinicio": lng,
                    "severidad_nivel": sev,
                    "estado_actual": estado_actual,
                    "numheridos": int(row.get('numheridos', 0)),
                    "numfallecidos": int(row.get('numfallecidos', 0)),
                    "numvehiculos": int(row.get('numvehiculos', 0)),
                    "fecha_actualizacion": fa_iso,
                    "descripcion": str(row.get('descripcion') or ''),
                    "calle_nombre": calle_nombre,
                    "ciudad_nombre": ciudad_nombre
                })

        return {
            "total_records": total_records,
            "page": page,
            "page_size": page_size,
            "results": resultados
        }
