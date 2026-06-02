import logging
from rest_framework.views import APIView
from rest_framework.response import Response

from accidentes.PKG1_Gestion_Accidentes.CU20_Dashboard_KPIs.services import DashboardService

logger = logging.getLogger(__name__)


class AccidenteDashboardView(APIView):
    def get(self, request):
        try:
            stats = DashboardService.obtener_dashboard_stats()
            return Response(stats)
        except Exception as exc:
            logger.error('Error obteniendo estadisticas de dashboard: %s', exc)
            return Response({'error': 'Error interno al obtener estadisticas'}, status=500)
