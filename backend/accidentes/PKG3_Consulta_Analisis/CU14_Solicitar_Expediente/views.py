import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accidentes.PKG3_Consulta_Analisis.CU14_Solicitar_Expediente.services import ExpedienteService

logger = logging.getLogger(__name__)


class AccidenteDetalleView(APIView):
    def get(self, request, accidente_id: str):
        try:
            accidente = ExpedienteService.obtener_detalle(accidente_id)
            if not accidente:
                return Response({'error': 'No encontrado', 'codigo': 'NO_ENCONTRADO'}, status=status.HTTP_404_NOT_FOUND)
            return Response(accidente)
        except Exception as exc:
            logger.error('Error detalle %s: %s', accidente_id, exc)
            return Response({'error': 'Error interno'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccidenteExpedienteView(APIView):
    def get(self, request, accidente_id: str):
        try:
            expediente = ExpedienteService.obtener_expediente_completo(accidente_id)
            if not expediente:
                return Response({'error': 'No encontrado', 'codigo': 'NO_ENCONTRADO'}, status=status.HTTP_404_NOT_FOUND)
            return Response(expediente)
        except Exception as exc:
            logger.error('Error obteniendo expediente %s: %s', accidente_id, exc)
            return Response({'error': 'Error interno al obtener expediente'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
