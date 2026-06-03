import logging
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accidentes.shared.permissions import EsOperadorOAdministrador
from accidentes.shared.utils import ok_response, validation_error_response, not_found_response, server_error_response
from accidentes.PKG1_Gestion_Accidentes.CU01_Registrar_Accidente.services import AccidenteRegistroService
from accidentes.PKG1_Gestion_Accidentes.CU01_Registrar_Accidente.serializers import (
    AccidenteRegistroSerializer,
)

logger = logging.getLogger(__name__)


class AccidenteRegistroView(APIView):
    permission_classes = [IsAuthenticated, EsOperadorOAdministrador]

    def post(self, request):
        serializer = AccidenteRegistroSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        try:
            accidente = AccidenteRegistroService.registrar_accidente(serializer.validated_data)
            return ok_response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            logger.error('Error registrando accidente: %s', exc)
            return server_error_response('Error interno al registrar')


class AccidenteDetalleView(APIView):
    permission_classes = [IsAuthenticated, EsOperadorOAdministrador]

    def put(self, request, accidente_id: str):
        serializer = AccidenteRegistroSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        try:
            accidente = AccidenteRegistroService.actualizar_accidente(accidente_id, serializer.validated_data)
            if not accidente:
                return not_found_response()
            return ok_response(accidente)
        except Exception as exc:
            logger.error('Error actualizando accidente %s: %s', accidente_id, exc)
            return server_error_response('Error interno al actualizar')
