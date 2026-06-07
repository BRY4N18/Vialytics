import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accidentes.shared.permissions import EsDespachadorOAdministrador, EsUnidadEmergencia
from accidentes.shared.utils import ok_response, validation_error_response, server_error_response, not_found_response
from accidentes.PKG2_Respuesta_Emergencias.CU09_Gestionar_Retiro_Vehicular.services import GestionarRetiroService
from accidentes.PKG2_Respuesta_Emergencias.CU09_Gestionar_Retiro_Vehicular.serializers import (
    RetiroSolicitarSerializer,
    RetiroAceptarSerializer,
    RetiroFinalizarSerializer,
    RetiroSerializer,
)

logger = logging.getLogger(__name__)


class RetiroSolicitarView(APIView):
    permission_classes = [IsAuthenticated, EsDespachadorOAdministrador]

    def post(self, request):
        serializer = RetiroSolicitarSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        try:
            resultado = GestionarRetiroService.solicitar_retiro(
                serializer.validated_data['idaccidente'],
                serializer.validated_data['idunidademergencia'],
                serializer.validated_data.get('descripcion', ''),
            )
            return ok_response(resultado)
        except RuntimeError as exc:
            logger.error('Error solicitando retiro: %s', exc)
            return server_error_response(str(exc))
        except Exception as exc:
            logger.error('Error inesperado solicitando retiro: %s', exc)
            return server_error_response('Error interno')


class RetiroAceptarView(APIView):
    permission_classes = [IsAuthenticated, EsUnidadEmergencia]

    def patch(self, request, retiro_id: int):
        serializer = RetiroAceptarSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        try:
            resultado = GestionarRetiroService.aceptar_retiro(
                retiro_id, serializer.validated_data.get('nota', '')
            )
            return ok_response(resultado)
        except ValueError as exc:
            return not_found_response(str(exc))
        except RuntimeError as exc:
            logger.error('Error aceptando retiro %s: %s', retiro_id, exc)
            return server_error_response(str(exc))
        except Exception as exc:
            logger.error('Error inesperado aceptando retiro %s: %s', retiro_id, exc)
            return server_error_response('Error interno')


class RetiroFinalizarView(APIView):
    permission_classes = [IsAuthenticated, EsUnidadEmergencia]

    def post(self, request, retiro_id: int):
        serializer = RetiroFinalizarSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors)
        try:
            resultado = GestionarRetiroService.finalizar_retiro(
                retiro_id,
                serializer.validated_data['nota_informe'],
                serializer.validated_data.get('urls_fotos', []),
            )
            return ok_response(resultado)
        except ValueError as exc:
            return not_found_response(str(exc))
        except RuntimeError as exc:
            logger.error('Error finalizando retiro %s: %s', retiro_id, exc)
            return server_error_response(str(exc))
        except Exception as exc:
            logger.error('Error inesperado finalizando retiro %s: %s', retiro_id, exc)
            return server_error_response('Error interno')


class RetiroListView(APIView):
    permission_classes = [IsAuthenticated, EsDespachadorOAdministrador | EsUnidadEmergencia]

    def get(self, request):
        try:
            unidad_id = request.query_params.get('unidad_id')
            if unidad_id:
                retiros = GestionarRetiroService.obtener_retiros_por_unidad(int(unidad_id))
            else:
                retiros = GestionarRetiroService.obtener_retiros_pendientes()
            serializer = RetiroSerializer(retiros, many=True)
            return ok_response(serializer.data)
        except Exception as exc:
            logger.error('Error obteniendo retiros: %s', exc)
            return server_error_response('Error al obtener retiros')
