import logging
from typing import Any, Dict, List

from accidentes.shared.repositories import PinotRepository

logger = logging.getLogger(__name__)


class DashboardKpiRepository:

    @staticmethod
    def get_kpis() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT count(*) as total, avg(distanciamillas) as avg_dist, "
            "count(distinct(idcalle)) as unique_calles, "
            "sum(CASE WHEN idseveridad = -206169288 THEN 1 ELSE 0 END) as critical "
            "FROM accidentes"
        )


class DashboardTrendRepository:

    @staticmethod
    def get_monthly_trend() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT YEAR(fechahoraclima) as y, MONTH(fechahoraclima) as m, "
            "count(*) as count "
            "FROM accidentes WHERE YEAR(fechahoraclima) >= 2019 "
            "GROUP BY 1, 2 ORDER BY 1, 2",
            use_multistage=True
        )


class DashboardSeveridadRepository:

    @staticmethod
    def get_severity_distribution() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT s.descripcion as name, count(*) as count "
            "FROM accidentes a "
            "JOIN severidades s ON a.idseveridad = s.idseveridad "
            "GROUP BY 1 ORDER BY 2 DESC",
            use_multistage=True
        )


class DashboardEstadosRepository:

    @staticmethod
    def get_top_states() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT e.estado as state, count(*) as count "
            "FROM accidentes a "
            "JOIN estados e ON a.idestado = e.idestado "
            "GROUP BY 1 ORDER BY 2 DESC LIMIT 10",
            use_multistage=True
        )


class DashboardHorarioRepository:

    @staticmethod
    def get_hourly_distribution() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT SUBSTR(horainicio, 1, 2) as hour, count(*) as count "
            "FROM accidentes GROUP BY 1 ORDER BY 1 LIMIT 24"
        )


class DashboardClimaRepository:

    @staticmethod
    def get_weather_distribution() -> List[Dict[str, Any]]:
        return PinotRepository.execute_query(
            "SELECT c.condicionclima as weather, count(*) as count "
            "FROM accidentes a "
            "JOIN estadoclima c ON a.idestadoclima = c.idestadoclima "
            "GROUP BY 1 ORDER BY 2 DESC LIMIT 7",
            use_multistage=True
        )

