import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accidentes.shared.permissions import EsDespachadorOAdministrador
from accidentes.shared.utils import ok_response, validation_error_response, server_error_response
from accidentes.PKG2_Respuesta_Emergencias.CU08_Actualizar_Estado_Unidad.services import UnidadEmergenciaService
from accidentes.PKG2_Respuesta_Emergencias.CU08_Actualizar_Estado_Unidad.serializers import UnidadEmergenciaSerializer, UnidadEstadoUpdateSerializer

logger = logging.getLogger(__name__)


class UnidadesEmergenciaView(APIView):
    permission_classes = [IsAuthenticated, EsDespachadorOAdministrador]

    def get(self, request):
        tipo = request.query_params.get('tipo')
        unidades = UnidadEmergenciaService.obtener_unidades(tipo)
        return ok_response(UnidadEmergenciaSerializer(unidades, many=True).data)


class UnidadEstadoView(APIView):
    permission_classes = [IsAuthenticated, EsDespachadorOAdministrador]

    def patch(self, request, unidad_id: int):
        serializer = UnidadEstadoUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        try:
            unidad = UnidadEmergenciaService.actualizar_estado(
                unidad_id, serializer.validated_data['estadounidad']
            )
            return ok_response(UnidadEmergenciaSerializer(unidad).data)
        except Exception as exc:
            logger.error('Error actualizando unidad %s: %s', unidad_id, exc)
            return server_error_response('Error interno')
