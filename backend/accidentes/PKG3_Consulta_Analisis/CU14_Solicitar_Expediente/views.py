import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accidentes.shared.permissions import EsOperadorOAnalistaOAdministrador
from accidentes.shared.utils import ok_response, not_found_response, server_error_response
from accidentes.PKG3_Consulta_Analisis.CU14_Solicitar_Expediente.services import ExpedienteService

logger = logging.getLogger(__name__)


class AccidenteDetalleView(APIView):
    permission_classes = [IsAuthenticated, EsOperadorOAnalistaOAdministrador]

    def get(self, request, accidente_id: str):
        try:
            accidente = ExpedienteService.obtener_detalle(accidente_id)
            if not accidente:
                return not_found_response()
            return ok_response(accidente)
        except Exception as exc:
            logger.error('Error detalle %s: %s', accidente_id, exc)
            return server_error_response('Error interno')


class AccidenteExpedienteView(APIView):
    permission_classes = [IsAuthenticated, EsOperadorOAnalistaOAdministrador]

    def get(self, request, accidente_id: str):
        try:
            expediente = ExpedienteService.obtener_expediente_completo(accidente_id)
            if not expediente:
                return not_found_response()
            return ok_response(expediente)
        except Exception as exc:
            logger.error('Error obteniendo expediente %s: %s', accidente_id, exc)
            return server_error_response('Error interno al obtener expediente')
