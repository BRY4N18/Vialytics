import logging
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from accidentes.shared.utils import ok_response, server_error_response
from accidentes.PKG1_Gestion_Accidentes.CU20_Dashboard_KPIs.services import DashboardService

logger = logging.getLogger(__name__)


class EstadisticasPublicasView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            stats = DashboardService.obtener_dashboard_stats()
            return ok_response(stats)
        except Exception as exc:
            logger.error('Error obteniendo estadísticas públicas: %s', exc)
            return server_error_response('Error interno al obtener estadísticas')
