import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accidentes.PKG1_Gestion_Accidentes.CU01_Registrar_Accidente.services import AccidenteRegistroService
from accidentes.PKG1_Gestion_Accidentes.CU01_Registrar_Accidente.serializers import (
    AccidenteRegistroSerializer, AccidenteDetalleSerializer
)

logger = logging.getLogger(__name__)


class AccidenteRegistroView(APIView):
    def post(self, request):
        serializer = AccidenteRegistroSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errores': serializer.errors, 'codigo': 'VALIDACION_FALLIDA'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            accidente = AccidenteRegistroService.registrar_accidente(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            logger.error('Error registrando accidente: %s', exc)
            return Response({'error': 'Error interno al registrar', 'codigo': 'ERROR_INTERNO'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccidenteDetalleView(APIView):
    def put(self, request, accidente_id: str):
        serializer = AccidenteRegistroSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errores': serializer.errors, 'codigo': 'VALIDACION_FALLIDA'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            accidente = AccidenteRegistroService.actualizar_accidente(accidente_id, serializer.validated_data)
            if not accidente:
                return Response({'error': 'No encontrado', 'codigo': 'NO_ENCONTRADO'}, status=status.HTTP_404_NOT_FOUND)
            return Response(accidente, status=status.HTTP_200_OK)
        except Exception as exc:
            logger.error('Error actualizando accidente %s: %s', accidente_id, exc)
            return Response({'error': 'Error interno al actualizar'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
