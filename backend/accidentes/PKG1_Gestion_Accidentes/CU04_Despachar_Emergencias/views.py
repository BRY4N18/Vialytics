import logging
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accidentes.shared.permissions import EsDespachadorOAdministrador
from accidentes.shared.utils import ok_response, validation_error_response, server_error_response
from accidentes.PKG1_Gestion_Accidentes.CU04_Despachar_Emergencias.services import DespachoService
from accidentes.PKG1_Gestion_Accidentes.CU04_Despachar_Emergencias.serializers import DespachoCrearSerializer, DespachoSerializer

logger = logging.getLogger(__name__)


class DespachoView(APIView):
    permission_classes = [IsAuthenticated, EsDespachadorOAdministrador]

    def get(self, request, accidente_id: str):
        try:
            despachos = DespachoService.obtener_despachos(accidente_id)
            serializer = DespachoSerializer(despachos, many=True)
            return ok_response(serializer.data)
        except Exception as exc:
            logger.error('Error obteniendo despachos %s: %s', accidente_id, exc)
            return server_error_response('Error obteniendo despachos')

    def post(self, request, accidente_id: str):
        serializer = DespachoCrearSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        try:
            despachos = DespachoService.despachar_unidades(
                accidente_id=accidente_id,
                unidades_ids=serializer.validated_data['unidades_ids'],
            )
            return ok_response(DespachoSerializer(despachos, many=True).data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            logger.error('Error despachando %s: %s', accidente_id, exc)
            return server_error_response('Error al despachar')
