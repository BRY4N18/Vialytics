import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accidentes.shared.permissions import EsDespachadorOAdministrador
from accidentes.shared.utils import ok_response, validation_error_response, server_error_response
from accidentes.PKG2_Respuesta_Emergencias.CU22_Gestionar_Unidades_Emergencia.services import UnidadEmergenciaGestionService
from accidentes.PKG2_Respuesta_Emergencias.CU22_Gestionar_Unidades_Emergencia.serializers import (
    UnidadEmergenciaCrearSerializer,
    UnidadEmergenciaActualizarSerializer,
    UnidadEmergenciaActivarSerializer,
    UnidadEmergenciaSerializer,
)

logger = logging.getLogger(__name__)


class UnidadEmergenciaListCreateView(APIView):
    permission_classes = [IsAuthenticated, EsDespachadorOAdministrador]

    def get(self, request):
        tipo = request.query_params.get('tipo')
        estado = request.query_params.get('estado')
        activo_param = request.query_params.get('activo')
        search = request.query_params.get('search')
        activo = None
        if activo_param is not None:
            activo = activo_param.lower() == 'true'
        unidades = UnidadEmergenciaGestionService.listar_unidades(
            tipo=tipo, estado=estado, activo=activo, search=search
        )
        return ok_response(UnidadEmergenciaSerializer(unidades, many=True).data)

    def post(self, request):
        serializer = UnidadEmergenciaCrearSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        try:
            unidad = UnidadEmergenciaGestionService.crear_unidad(
                serializer.validated_data['unidademergencia'],
                serializer.validated_data['tipounidad_id'],
            )
            return ok_response(UnidadEmergenciaSerializer(unidad).data)
        except ValueError as exc:
            return validation_error_response(str(exc))
        except RuntimeError as exc:
            logger.error('Error creando unidad: %s', exc)
            return server_error_response(str(exc))
        except Exception as exc:
            logger.error('Error inesperado creando unidad: %s', exc)
            return server_error_response('Error interno')


class UnidadEmergenciaDetailView(APIView):
    permission_classes = [IsAuthenticated, EsDespachadorOAdministrador]

    def put(self, request, unidad_id):
        serializer = UnidadEmergenciaActualizarSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        try:
            unidad = UnidadEmergenciaGestionService.actualizar_unidad(
                unidad_id,
                serializer.validated_data['unidademergencia'],
                serializer.validated_data['tipounidad_id'],
            )
            return ok_response(UnidadEmergenciaSerializer(unidad).data)
        except ValueError as exc:
            return validation_error_response(str(exc))
        except RuntimeError as exc:
            logger.error('Error actualizando unidad: %s', exc)
            return server_error_response(str(exc))
        except Exception as exc:
            logger.error('Error inesperado actualizando unidad: %s', exc)
            return server_error_response('Error interno')


class UnidadEmergenciaActivarView(APIView):
    permission_classes = [IsAuthenticated, EsDespachadorOAdministrador]

    def patch(self, request, unidad_id):
        serializer = UnidadEmergenciaActivarSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        try:
            unidad = UnidadEmergenciaGestionService.toggle_activo(
                unidad_id,
                serializer.validated_data['activo'],
            )
            return ok_response(UnidadEmergenciaSerializer(unidad).data)
        except ValueError as exc:
            return validation_error_response(str(exc))
        except RuntimeError as exc:
            logger.error('Error toggling activo unidad: %s', exc)
            return server_error_response(str(exc))
        except Exception as exc:
            logger.error('Error inesperado toggling activo unidad: %s', exc)
            return server_error_response('Error interno')
