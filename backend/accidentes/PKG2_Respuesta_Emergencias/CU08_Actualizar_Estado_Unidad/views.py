import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import async_to_sync

from accidentes.PKG2_Respuesta_Emergencias.CU08_Actualizar_Estado_Unidad.services import UnidadEmergenciaService
from accidentes.PKG2_Respuesta_Emergencias.CU08_Actualizar_Estado_Unidad.serializers import UnidadEmergenciaSerializer, UnidadEstadoUpdateSerializer

logger = logging.getLogger(__name__)


class UnidadesEmergenciaView(APIView):
    def get(self, request):
        tipo = request.query_params.get('tipo')
        unidades = async_to_sync(UnidadEmergenciaService.obtener_unidades)(tipo)
        return Response(UnidadEmergenciaSerializer(unidades, many=True).data)


class UnidadEstadoView(APIView):
    def patch(self, request, unidad_id: int):
        serializer = UnidadEstadoUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errores': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            unidad = async_to_sync(UnidadEmergenciaService.actualizar_estado)(
                unidad_id, serializer.validated_data['estadounidad']
            )
            return Response(UnidadEmergenciaSerializer(unidad).data)
        except Exception as exc:
            logger.error('Error actualizando unidad %s: %s', unidad_id, exc)
            return Response({'error': 'Error interno'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
