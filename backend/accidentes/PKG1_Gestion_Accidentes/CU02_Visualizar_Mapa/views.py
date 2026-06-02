import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from accidentes.PKG1_Gestion_Accidentes.CU02_Visualizar_Mapa.services import MapaService

logger = logging.getLogger(__name__)


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
                'idpais': request.query_params.get('idpais', '') or None,
                'idestado': request.query_params.get('idestado', '') or None,
                'idcondado': request.query_params.get('idcondado', '') or None,
                'idciudad': request.query_params.get('idciudad', '') or None,
                'idcalle': request.query_params.get('idcalle', '') or None,
            }

            accidentes = MapaService.obtener_accidentes_mapa(filtros)
            return Response(accidentes)
        except Exception as exc:
            logger.error('Error obteniendo mapa: %s', exc)
            return Response({'error': 'Error obteniendo accidentes'}, status=500)
