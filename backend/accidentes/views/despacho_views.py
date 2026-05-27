import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import async_to_sync

from accidentes.services import DespachoService
from accidentes.serializers import DespachoCrearSerializer, DespachoSerializer

logger = logging.getLogger(__name__)


class DespachoView(APIView):
    def get(self, request, accidente_id: str):
        try:
            # Ejecutar asíncrono sincrónicamente usando async_to_sync
            despachos = async_to_sync(DespachoService.obtener_despachos)(accidente_id)
            serializer = DespachoSerializer(despachos, many=True)
            return Response(serializer.data)
        except Exception as exc:
            logger.error('Error obteniendo despachos %s: %s', accidente_id, exc)
            return Response({'error': 'Error obteniendo despachos'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, accidente_id: str):
        serializer = DespachoCrearSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errores': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Ejecutar asíncrono sincrónicamente usando async_to_sync
            despachos = async_to_sync(DespachoService.despachar_unidades)(
                accidente_id=accidente_id,
                unidades_ids=serializer.validated_data['unidades_ids'],
            )
            return Response(DespachoSerializer(despachos, many=True).data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            logger.error('Error despachando %s: %s', accidente_id, exc)
            return Response({'error': 'Error al despachar'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
