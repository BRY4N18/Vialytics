import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from accidentes.PKG1_Gestion_Accidentes.CU02_Visualizar_Mapa.repositories import (
    SeveridadRepository,
    CalleRepository,
    CiudadRepository,
    CondadoRepository,
    EstadoGeograficoRepository,
    FechaRepository,
    AccidenteMapaRepository,
)

logger = logging.getLogger(__name__)


class MapaService:
    @staticmethod
    def obtener_accidentes_mapa(filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        severidad_param = filtros.get('severidad')

        sev_rows = SeveridadRepository.get_all()
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
            idcalles_filter = CalleRepository.find_by_ciudad(str(idciudad))
        elif idcondado:
            ciudad_rows = CiudadRepository.find_by_condado(str(idcondado))
            ciudades_nombres = [r['ciudad'] for r in ciudad_rows if r.get('ciudad') is not None]
            if ciudades_nombres:
                idcalles_filter = CalleRepository.find_by_ciudades(ciudades_nombres)
        elif idestado:
            condados = CondadoRepository.find_by_estado(str(idestado))
            if condados:
                ciudad_rows = CiudadRepository.find_by_condados(condados)
                ciudades_nombres = [r['ciudad'] for r in ciudad_rows if r.get('ciudad') is not None]
                if ciudades_nombres:
                    idcalles_filter = CalleRepository.find_by_ciudades(ciudades_nombres)
        elif idpais:
            estados_list = EstadoGeograficoRepository.find_by_pais(str(idpais))
            if estados_list:
                condados = CondadoRepository.find_by_estados(estados_list)
                if condados:
                    ciudad_rows = CiudadRepository.find_by_condados(condados)
                    ciudades_nombres = [r['ciudad'] for r in ciudad_rows if r.get('ciudad') is not None]
                    if ciudades_nombres:
                        idcalles_filter = CalleRepository.find_by_ciudades(ciudades_nombres)

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
            start_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            end_str = datetime.now().strftime("%Y-%m-%d")

        if start_str or end_str:
            date_ids = FechaRepository.find_by_date_range(start_str, end_str)

            start_ms = 0
            end_ms = 0
            if start_str:
                start_ms = int(datetime.strptime(start_str, "%Y-%m-%d").timestamp() * 1000)
            if end_str:
                end_ms = int(datetime.strptime(end_str + " 23:59:59", "%Y-%m-%d %H:%M:%S").timestamp() * 1000)

            clauses = []
            if date_ids:
                clauses.append(f"idfecha IN ({', '.join(map(str, date_ids))})")

            legacy_clause = ["idfecha <= 1"]
            if start_ms:
                legacy_clause.append(f"fecha_actualizacion >= {start_ms}")
            if end_ms:
                legacy_clause.append(f"fecha_actualizacion <= {end_ms}")
            clauses.append("(" + " AND ".join(legacy_clause) + ")")

            query += f" AND ({' OR '.join(clauses)})"

        query += " LIMIT 500"

        rows = AccidenteMapaRepository.find_all(query)

        if rows:
            calle_ids = {row.get('idcalle') for row in rows if row.get('idcalle') is not None}
            ciudad_ids = {row.get('idciudad') for row in rows if row.get('idciudad') is not None}

            calles_map = CalleRepository.find_by_ids(list(calle_ids)) if calle_ids else {}
            ciudades_map = CiudadRepository.find_by_ids(list(ciudad_ids)) if ciudad_ids else {}

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
