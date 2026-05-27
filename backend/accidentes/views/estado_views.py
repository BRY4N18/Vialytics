import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import async_to_sync

from accidentes.services import AccidenteService
from accidentes.serializers import ActualizarEstadoSerializer

logger = logging.getLogger(__name__)


class AccidenteEstadoView(APIView):
    def patch(self, request, accidente_id: str):
        serializer = ActualizarEstadoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errores': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Ejecutar asíncrono sincrónicamente usando async_to_sync
            resultado = async_to_sync(AccidenteService.actualizar_estado)(
                accidente_id=accidente_id,
                nuevo_estado_id=serializer.validated_data['idtipoestadoincidente_id'],
                nota=serializer.validated_data.get('nota'),
                idusuario_id=1,
            )
            return Response(resultado)
        except Exception as exc:
            logger.error('Error actualizando estado %s: %s', accidente_id, exc)
            return Response({'error': 'Error actualizando estado'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
