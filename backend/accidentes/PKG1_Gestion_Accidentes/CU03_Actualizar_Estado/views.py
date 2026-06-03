import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accidentes.shared.permissions import EsOperadorOAdministrador
from accidentes.shared.utils import ok_response, validation_error_response, server_error_response
from accidentes.PKG1_Gestion_Accidentes.CU03_Actualizar_Estado.serializers import ActualizarEstadoSerializer
from accidentes.PKG1_Gestion_Accidentes.CU03_Actualizar_Estado.services import EstadoService

logger = logging.getLogger(__name__)


class AccidenteEstadoView(APIView):
    permission_classes = [IsAuthenticated, EsOperadorOAdministrador]

    def patch(self, request, accidente_id: str):
        serializer = ActualizarEstadoSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        try:
            resultado = EstadoService.actualizar_estado(
                accidente_id=accidente_id,
                nuevo_estado_id=serializer.validated_data['idtipoestadoincidente_id'],
                nota=serializer.validated_data.get('nota'),
                idusuario_id=1,
            )
            return ok_response(resultado)
        except Exception as exc:
            logger.error('Error actualizando estado %s: %s', accidente_id, exc)
            return server_error_response('Error actualizando estado')
