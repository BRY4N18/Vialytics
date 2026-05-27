import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)
PINOT_BROKER_URL = 'http://localhost:8099/query/sql'


class PinotQueryService:
    @staticmethod
    async def ejecutar_query(sql: str) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(PINOT_BROKER_URL, json={'sql': sql})
                response.raise_for_status()
                data = response.json()
                result_table = data.get('resultTable', {})
                column_names = result_table.get('dataSchema', {}).get('columnNames', [])
                rows = result_table.get('rows', [])
                return [
                    {col: row[i] for i, col in enumerate(column_names)}
                    for row in rows
                ]
        except httpx.ConnectError:
            logger.warning('Pinot Broker no disponible en %s', PINOT_BROKER_URL)
            return []
        except Exception as exc:
            logger.error('Error consultando Pinot: %s', exc)
            return []

    @staticmethod
    async def obtener_accidentes_mapa(
        excluir_estados: Optional[List[str]] = None,
        severidad: Optional[int] = None,
        horas: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        condiciones = ['activo = true']
        if excluir_estados:
            estados_str = ', '.join(f"'{e}'" for e in excluir_estados)
            condiciones.append(f"estado_actual NOT IN ({estados_str})")
        if severidad:
            condiciones.append(f'severidad_nivel = {severidad}')
        if horas:
            condiciones.append(f"fechaActualizacion > ago('PT{horas}H')")
        where_clause = ' AND '.join(condiciones)
        sql = (
            f"SELECT idaccidente, latitudinicio, longitudinicio, severidad_nivel, "
            f"estado_actual, numheridos, numfallecidos, fechaActualizacion, descripcion, "
            f"calle_nombre, ciudad_nombre "
            f"FROM accidentes "
            f"WHERE {where_clause} "
            f"ORDER BY fechaActualizacion DESC LIMIT 500"
        )
        return await PinotQueryService.ejecutar_query(sql)
