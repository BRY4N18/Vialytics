import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accidentes.shared.permissions import EsDespachadorOAdministrador, EsUnidadRespondiente
from accidentes.shared.utils import ok_response, validation_error_response, server_error_response, not_found_response
from accidentes.PKG2_Respuesta_Emergencias.CU07_Recibir_Despacho.services import RecibirDespachoService
from accidentes.PKG2_Respuesta_Emergencias.CU07_Recibir_Despacho.serializers import (
    DespachoPendienteSerializer,
    NotificacionSerializer,
    NotificacionAceptarSerializer,
)

logger = logging.getLogger(__name__)


class DespachoUnidadView(APIView):
    permission_classes = [IsAuthenticated, EsDespachadorOAdministrador | EsUnidadRespondiente]

    def get(self, request, unidad_id: int):
        try:
            solo_pendientes = request.query_params.get('pendientes', '').lower() == 'true'
            despachos = RecibirDespachoService.obtener_despachos(unidad_id, solo_pendientes)
            serializer = DespachoPendienteSerializer(despachos, many=True)
            return ok_response(serializer.data)
        except Exception as exc:
            logger.error('Error obteniendo despachos para unidad %s: %s', unidad_id, exc)
            return server_error_response('Error al obtener despachos')


class DespachoLLegadaView(APIView):
    permission_classes = [IsAuthenticated, EsDespachadorOAdministrador | EsUnidadRespondiente]

    def patch(self, request, despacho_id: int):
        try:
            RecibirDespachoService.marcar_llegada(despacho_id)
            return ok_response({"mensaje": "Llegada registrada exitosamente"})
        except ValueError as exc:
            return not_found_response(str(exc))
        except RuntimeError as exc:
            logger.error('Error marcando llegada despacho %s: %s', despacho_id, exc)
            return server_error_response('Error al marcar llegada')
        except Exception as exc:
            logger.error('Error inesperado marcando llegada %s: %s', despacho_id, exc)
            return server_error_response('Error interno')


class NotificacionListView(APIView):
    permission_classes = [IsAuthenticated, EsDespachadorOAdministrador | EsUnidadRespondiente]

    def get(self, request):
        try:
            notificaciones = RecibirDespachoService.obtener_notificaciones()
            serializer = NotificacionSerializer(notificaciones, many=True)
            return ok_response(serializer.data)
        except Exception as exc:
            logger.error('Error obteniendo notificaciones: %s', exc)
            return server_error_response('Error al obtener notificaciones')


class NotificacionAceptarView(APIView):
    permission_classes = [IsAuthenticated, EsDespachadorOAdministrador | EsUnidadRespondiente]

    def post(self, request, notificacion_id: int):
        serializer = NotificacionAceptarSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        try:
            resultado = RecibirDespachoService.aceptar_notificacion(
                notificacion_id, serializer.validated_data['idunidademergencia']
            )
            return ok_response(resultado)
        except ValueError as exc:
            return not_found_response(str(exc))
        except RuntimeError as exc:
            logger.error('Error aceptando notificacion %s: %s', notificacion_id, exc)
            return server_error_response(str(exc))
        except Exception as exc:
            logger.error('Error inesperado aceptando notificacion %s: %s', notificacion_id, exc)
            return server_error_response('Error interno')
