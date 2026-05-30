import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from asgiref.sync import async_to_sync

from accidentes.services import AccidenteService
from accidentes.serializers import (
    AccidenteRegistroSerializer, AccidenteDetalleSerializer
)

logger = logging.getLogger(__name__)


class AccidenteRegistroView(APIView):
    def post(self, request):
        serializer = AccidenteRegistroSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errores': serializer.errors, 'codigo': 'VALIDACION_FALLIDA'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            accidente = AccidenteService.registrar_accidente(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            logger.error('Error registrando accidente: %s', exc)
            return Response({'error': 'Error interno al registrar', 'codigo': 'ERROR_INTERNO'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 8))
            search = request.query_params.get('search', '')
            severidad_param = request.query_params.get('severidad')
            estado = request.query_params.get('estado', '')
            solo_activos = request.query_params.get('solo_activos', 'false') == 'true'

            severidad = int(severidad_param) if severidad_param and severidad_param.isdigit() else None

            ciudad_id_param = request.query_params.get('ciudad_id')
            ciudad_id = int(ciudad_id_param) if ciudad_id_param and ciudad_id_param.isdigit() else None

            min_heridos = request.query_params.get('min_heridos')
            max_heridos = request.query_params.get('max_heridos')
            min_fallecidos = request.query_params.get('min_fallecidos')
            max_fallecidos = request.query_params.get('max_fallecidos')
            fecha_desde = request.query_params.get('fecha_desde', '')
            fecha_hasta = request.query_params.get('fecha_hasta', '')
            matricula = request.query_params.get('matricula', '')

            filtros = {
                'page': page,
                'page_size': page_size,
                'search': search,
                'severidad': severidad,
                'estado': estado,
                'solo_activos': solo_activos,
                'ciudad_id': ciudad_id,
                'min_heridos': int(min_heridos) if min_heridos and min_heridos.isdigit() else None,
                'max_heridos': int(max_heridos) if max_heridos and max_heridos.isdigit() else None,
                'min_fallecidos': int(min_fallecidos) if min_fallecidos and min_fallecidos.isdigit() else None,
                'max_fallecidos': int(max_fallecidos) if max_fallecidos and max_fallecidos.isdigit() else None,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'matricula': matricula,
            }

            datos_paginados = AccidenteService.obtener_accidentes_paginados(filtros)
            return Response(datos_paginados)
        except Exception as exc:
            logger.error('Error en listado de accidentes paginados: %s', exc)
            return Response({'error': 'Error interno al obtener listado'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccidenteMapaView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            severidad_param = request.query_params.get('severidad')
            horas_param = request.query_params.get('horas')
            solo_ultima_semana = request.query_params.get('solo_ultima_semana', 'false').lower() == 'true'
            fecha_inicio = request.query_params.get('fecha_inicio', '')
            fecha_fin = request.query_params.get('fecha_fin', '')
            
            severidad = int(severidad_param) if severidad_param and severidad_param.isdigit() else None
            horas = int(horas_param) if horas_param and horas_param.isdigit() else None
            
            filtros = {
                'severidad': severidad,
                'horas': horas,
                'excluir_estados': ['Despejado', 'Archivado'] if request.query_params.get('solo_activos', 'true') == 'true' else [],
                'solo_ultima_semana': solo_ultima_semana,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'public': request.query_params.get('public', 'false').lower() == 'true',
                # Filtros de ubicaciÃ³n
                'idpais': request.query_params.get('idpais', '') or None,
                'idestado': request.query_params.get('idestado', '') or None,
                'idcondado': request.query_params.get('idcondado', '') or None,
                'idciudad': request.query_params.get('idciudad', '') or None,
                'idcalle': request.query_params.get('idcalle', '') or None,
            }
            
            accidentes = AccidenteService.obtener_accidentes_mapa(filtros)
            return Response(accidentes)
        except Exception as exc:
            logger.error('Error obteniendo mapa: %s', exc)
            return Response({'error': 'Error obteniendo accidentes'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccidenteDetalleView(APIView):
    def get(self, request, accidente_id: str):
        try:
            accidente = AccidenteService.obtener_detalle(accidente_id)
            if not accidente:
                return Response({'error': 'No encontrado', 'codigo': 'NO_ENCONTRADO'}, status=status.HTTP_404_NOT_FOUND)
            return Response(accidente)
        except Exception as exc:
            logger.error('Error detalle %s: %s', accidente_id, exc)
            return Response({'error': 'Error interno'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, accidente_id: str):
        serializer = AccidenteRegistroSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errores': serializer.errors, 'codigo': 'VALIDACION_FALLIDA'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            accidente = AccidenteService.actualizar_accidente(accidente_id, serializer.validated_data)
            if not accidente:
                return Response({'error': 'No encontrado', 'codigo': 'NO_ENCONTRADO'}, status=status.HTTP_404_NOT_FOUND)
            return Response(accidente, status=status.HTTP_200_OK)
        except Exception as exc:
            logger.error('Error actualizando accidente %s: %s', accidente_id, exc)
            return Response({'error': 'Error interno al actualizar'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccidenteDashboardView(APIView):
    def get(self, request):
        try:
            stats = AccidenteService.obtener_dashboard_stats()
            return Response(stats)
        except Exception as exc:
            logger.error('Error obteniendo estadisticas de dashboard: %s', exc)
            return Response({'error': 'Error interno al obtener estadisticas'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccidenteExpedienteView(APIView):
    def get(self, request, accidente_id: str):
        try:
            expediente = AccidenteService.obtener_expediente_completo(accidente_id)
            if not expediente:
                return Response({'error': 'No encontrado', 'codigo': 'NO_ENCONTRADO'}, status=status.HTTP_404_NOT_FOUND)
            return Response(expediente)
        except Exception as exc:
            logger.error('Error obteniendo expediente %s: %s', accidente_id, exc)
            return Response({'error': 'Error interno al obtener expediente'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

