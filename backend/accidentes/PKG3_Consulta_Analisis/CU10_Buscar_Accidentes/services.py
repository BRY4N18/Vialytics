import logging
from datetime import datetime
from typing import Any, Dict, List

from accidentes.shared.repositories import PinotRepository
from accidentes.PKG1_Gestion_Accidentes.CU02_Visualizar_Mapa.repositories import (
    SeveridadRepository,
    CalleRepository,
    CiudadRepository,
)
from accidentes.PKG3_Consulta_Analisis.CU10_Buscar_Accidentes.repositories import (
    BusquedaCalleRepository,
    BusquedaCiudadRepository,
    VehiculoBusquedaRepository,
    ConductorAccidenteBusquedaRepository,
    EstadoIncidenteRepository,
    AccidenteBusquedaRepository,
)

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

        sev_rows = SeveridadRepository.get_all()
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
            search_escaped = PinotRepository.escape_sql_str(search.lower())
            search_escaped = search_escaped.replace("%", "\\%").replace("_", "\\_")
            search_clauses = [
                f"LOWER(descripcion) LIKE '%{search_escaped}%'",
                f"LOWER(idaccidente) LIKE '%{search_escaped}%'"
            ]

            calle_ids = BusquedaCalleRepository.find_by_search(search)
            if calle_ids:
                search_clauses.append(f"idcalle IN ({', '.join(map(str, calle_ids))})")

            ciudad_ids = BusquedaCiudadRepository.find_by_search(search)
            if ciudad_ids:
                search_clauses.append(f"idciudad IN ({', '.join(map(str, ciudad_ids))})")

            where_clauses.append(f"({' OR '.join(search_clauses)})")

        if matricula:
            veh_ids = VehiculoBusquedaRepository.find_by_search(matricula)
            if veh_ids:
                acc_ids = ConductorAccidenteBusquedaRepository.find_accidente_ids_by_vehiculos(veh_ids)
                if acc_ids:
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
                todos_estados = EstadoIncidenteRepository.get_all()
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

        total_records = AccidenteBusquedaRepository.count(where_str)

        columns = (
            "idaccidente, latitudinicio, longitudinicio, idseveridad, activo, "
            "numheridos, numfallecidos, numvehiculos, numvictimas, descripcion, "
            "idcalle, idciudad, fecha_actualizacion"
        )
        rows = AccidenteBusquedaRepository.find_paginated(columns, where_str, page_size, offset)

        resultados = []
        if rows:
            calle_ids = {row.get('idcalle') for row in rows if row.get('idcalle') is not None}
            ciudad_ids = {row.get('idciudad') for row in rows if row.get('idciudad') is not None}

            calles_map = CalleRepository.find_by_ids(list(calle_ids)) if calle_ids else {}
            ciudades_map = CiudadRepository.find_by_ids(list(ciudad_ids)) if ciudad_ids else {}

            acc_ids = [f"'{r['idaccidente']}'" for r in rows if r.get('idaccidente')]
            estado_map = {}
            if acc_ids:
                estado_rows = EstadoIncidenteRepository.find_by_accidente_ids(acc_ids)
                estados_catalogo = {
                    1: "ACTIVO", 2: "EN_ATENCION", 3: "EN_ATENCION",
                    4: "CONTROLADO", 5: "ARCHIVADO"
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
