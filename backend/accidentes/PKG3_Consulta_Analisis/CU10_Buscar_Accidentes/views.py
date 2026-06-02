import logging
from rest_framework.views import APIView
from rest_framework.response import Response

from accidentes.PKG3_Consulta_Analisis.CU10_Buscar_Accidentes.services import BusquedaService

logger = logging.getLogger(__name__)


class AccidenteBusquedaView(APIView):
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

            datos_paginados = BusquedaService.obtener_accidentes_paginados(filtros)
            return Response(datos_paginados)
        except Exception as exc:
            logger.error('Error en listado de accidentes paginados: %s', exc)
            return Response({'error': 'Error interno al obtener listado'}, status=500)
