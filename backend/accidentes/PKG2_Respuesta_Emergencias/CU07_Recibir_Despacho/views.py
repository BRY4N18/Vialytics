import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accidentes.shared.permissions import EsUnidadRespondiente
from accidentes.shared.utils import ok_response, validation_error_response, server_error_response, not_found_response
from accidentes.PKG2_Respuesta_Emergencias.CU07_Recibir_Despacho.services import RecibirDespachoService
from accidentes.PKG2_Respuesta_Emergencias.CU07_Recibir_Despacho.serializers import (
    DespachoPendienteSerializer,
    DespachoConfirmacionSerializer,
)

logger = logging.getLogger(__name__)


class DespachoUnidadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, unidad_id: int):
        try:
            solo_pendientes = request.query_params.get('pendientes', '').lower() == 'true'
            despachos = RecibirDespachoService.obtener_despachos(unidad_id, solo_pendientes)
            serializer = DespachoPendienteSerializer(despachos, many=True)
            return ok_response(serializer.data)
        except Exception as exc:
            logger.error('Error obteniendo despachos para unidad %s: %s', unidad_id, exc)
            return server_error_response('Error al obtener despachos')


class DespachoConfirmarView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, despacho_id: int):
        try:
            RecibirDespachoService.confirmar_despacho(despacho_id)
            return ok_response({"mensaje": "Despacho confirmado exitosamente"})
        except ValueError as exc:
            return not_found_response(str(exc))
        except RuntimeError as exc:
            logger.error('Error confirmando despacho %s: %s', despacho_id, exc)
            return server_error_response('Error al confirmar despacho')
        except Exception as exc:
            logger.error('Error inesperado confirmando despacho %s: %s', despacho_id, exc)
            return server_error_response('Error interno')


class DespachoLLegadaView(APIView):
    permission_classes = [IsAuthenticated]

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
