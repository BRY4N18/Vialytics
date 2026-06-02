import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from accidentes.PKG1_Gestion_Accidentes.CU20_Dashboard_KPIs.services import DashboardService

logger = logging.getLogger(__name__)


class EstadisticasPublicasView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            stats = DashboardService.obtener_dashboard_stats()
            return Response(stats)
        except Exception as exc:
            logger.error('Error obteniendo estadísticas públicas: %s', exc)
            return Response({'error': 'Error interno al obtener estadísticas'}, status=500)
