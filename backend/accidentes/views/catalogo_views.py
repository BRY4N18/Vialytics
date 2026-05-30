import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from accidentes.repositories import PinotRepository
from accidentes.serializers import (
    SeveridadSerializer, TipoReportadoSerializer, TipoEstadoIncidenteSerializer,
    PaisSerializer, EstadoSerializer, CondadoSerializer, CiudadSerializer,
    CalleSerializer, ClimaSerializer, ElementoFisicoSerializer, PeriodoDiaSerializer
)

logger = logging.getLogger(__name__)

# --- FALLBACK SEED DATA ---
SEED_PAISES = [
    {"idpais": 1954003872, "pais": "US"},
    {"idpais": 1, "pais": "EC"}
]

SEED_ESTADOS = [
    {"idestado": 1833795888, "estado": "TX", "pais": "US"},
    {"idestado": 2, "estado": "AL", "pais": "US"},
    {"idestado": 1976532096, "estado": "MN", "pais": "US"},
    {"idestado": 983353925, "estado": "VA", "pais": "US"},
    {"idestado": 1729918071, "estado": "GA", "pais": "US"},
    {"idestado": 6, "estado": "SC", "pais": "US"},
    {"idestado": 7, "estado": "GY", "pais": "EC"},
    {"idestado": 1, "estado": "PI", "pais": "EC"}
]

SEED_CONDADOS = [
    {"idcondado": 1788116726, "condado": "Tarrant", "estado": "TX"},
    {"idcondado": 2, "condado": "Harris", "estado": "TX"},
    {"idcondado": 3, "condado": "Baldwin", "estado": "AL"},
    {"idcondado": 4, "condado": "Chilton", "estado": "AL"},
    {"idcondado": -1854046373, "condado": "St. Louis", "estado": "MN"},
    {"idcondado": -1305131593, "condado": "Chesapeake", "estado": "VA"},
    {"idcondado": 1446873394, "condado": "DeKalb", "estado": "GA"},
    {"idcondado": 8, "condado": "Dorchester", "estado": "SC"},
    {"idcondado": 9, "condado": "Spartanburg", "estado": "SC"},
    {"idcondado": 10, "condado": "Guayas", "estado": "GY"},
    {"idcondado": 1, "condado": "Quito D.M.", "estado": "PI"}
]

SEED_CIUDADES = [
    {"idciudad": -1483930363, "ciudad": "Fort Worth", "condado": "Tarrant"},
    {"idciudad": 2, "ciudad": "Houston", "condado": "Harris"},
    {"idciudad": 3, "ciudad": "Daphne", "condado": "Baldwin"},
    {"idciudad": 4, "ciudad": "Clanton", "condado": "Chilton"},
    {"idciudad": -514066125, "ciudad": "Floodwood", "condado": "St. Louis"},
    {"idciudad": -7720717, "ciudad": "Chesapeake", "condado": "Chesapeake"},
    {"idciudad": 216885066, "ciudad": "Stone Mountain", "condado": "DeKalb"},
    {"idciudad": 8, "ciudad": "Ridgeville", "condado": "Dorchester"},
    {"idciudad": 9, "ciudad": "Spartanburg", "condado": "Spartanburg"},
    {"idciudad": 10, "ciudad": "Guayaquil", "condado": "Guayas"},
    {"idciudad": 1, "ciudad": "Quito", "condado": "Quito D.M."}
]

SEED_CALLES = [
    {"idcalle": 665123162, "calle": "I-35W S", "ciudad": "Fort Worth"},
    {"idcalle": 2, "calle": "El Dorado Blvd", "ciudad": "Houston"},
    {"idcalle": 3, "calle": "I-10 W", "ciudad": "Daphne"},
    {"idcalle": 4, "calle": "7th St N", "ciudad": "Clanton"},
    {"idcalle": 1914374434, "calle": "Highway 2", "ciudad": "Floodwood"},
    {"idcalle": 1261476550, "calle": "I-64 E", "ciudad": "Chesapeake"},
    {"idcalle": 1336244665, "calle": "Stone Mountain Fwy", "ciudad": "Stone Mountain"},
    {"idcalle": 8, "calle": "Campbell Thickett Rd", "ciudad": "Ridgeville"},
    {"idcalle": 9, "calle": "W Main St", "ciudad": "Spartanburg"},
    {"idcalle": 10, "calle": "Av. Francisco de Orellana", "ciudad": "Guayaquil"},
    {"idcalle": 1, "calle": "Av. Amazonas", "ciudad": "Quito"},
    {"idcalle": 2, "calle": "Av. De los Shyris", "ciudad": "Quito"},
    {"idcalle": 3, "calle": "Av. 10 de Agosto", "ciudad": "Quito"}
]

SEED_CLIMAS = [
    {
        "idestadoclima": 1, "condicionclima": "Fair / Despejado", "direccionviento": "CALM",
        "temperaturaf": 72.0, "sensaciontermicaf": 72.0, "humedadporcentaje": 50.0,
        "presionpulgadas": 30.1, "visibilidadmillas": 10.0, "velocidadvientomph": 0.0, "precipitacionpulgadas": 0.0
    },
    {
        "idestadoclima": 2, "condicionclima": "Cloudy / Nublado", "direccionviento": "NW",
        "temperaturaf": 60.0, "sensaciontermicaf": 58.0, "humedadporcentaje": 65.0,
        "presionpulgadas": 29.9, "visibilidadmillas": 10.0, "velocidadvientomph": 8.0, "precipitacionpulgadas": 0.0
    },
    {
        "idestadoclima": 3, "condicionclima": "Light Rain / Lluvia Ligera", "direccionviento": "SW",
        "temperaturaf": 55.0, "sensaciontermicaf": 53.0, "humedadporcentaje": 88.0,
        "presionpulgadas": 29.7, "visibilidadmillas": 4.0, "velocidadvientomph": 10.0, "precipitacionpulgadas": 0.05
    },
    {
        "idestadoclima": 4, "condicionclima": "Heavy Thunderstorm / Tormenta", "direccionviento": "VAR",
        "temperaturaf": 68.0, "sensaciontermicaf": 68.0, "humedadporcentaje": 95.0,
        "presionpulgadas": 29.5, "visibilidadmillas": 2.0, "velocidadvientomph": 18.0, "precipitacionpulgadas": 0.45
    }
]

SEED_ELEMENTOS = [
    {
        "idelementofisico": 1, "cercacruce": True, "cercasemaforo": True, "cercaparada": False,
        "cercaestacion": False, "cercabache": False, "cercaviatren": False
    },
    {
        "idelementofisico": 2, "cercacruce": False, "cercasemaforo": False, "cercaparada": True,
        "cercaestacion": True, "cercabache": False, "cercaviatren": False
    },
    {
        "idelementofisico": 3, "cercacruce": False, "cercasemaforo": False, "cercaparada": False,
        "cercaestacion": False, "cercabache": True, "cercaviatren": True
    },
    {
        "idelementofisico": 4, "cercacruce": False, "cercasemaforo": False, "cercaparada": False,
        "cercaestacion": False, "cercabache": False, "cercaviatren": False
    }
]

SEED_PERIODOS = [
    {"idperiododia": 1, "amaneceranochecer": "Day", "crepusculocivil": "Day", "crepusculonautico": "Day", "crepusculoastronomico": "Day"},
    {"idperiododia": 2, "amaneceranochecer": "Night", "crepusculocivil": "Night", "crepusculonautico": "Night", "crepusculoastronomico": "Night"}
]

SEED_TIPOS_ESTADOS = [
    {"idtipoestadoincidente": 1, "tipoestadoincidente": "ACTIVO"},
    {"idtipoestadoincidente": 2, "tipoestadoincidente": "EN_ATENCION"},
    {"idtipoestadoincidente": 3, "tipoestadoincidente": "EN_TRASLADO"},
    {"idtipoestadoincidente": 4, "tipoestadoincidente": "CONTROLADO"},
    {"idtipoestadoincidente": 5, "tipoestadoincidente": "ARCHIVADO"}
]


class SeveridadListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            data = PinotRepository.execute_query("SELECT idseveridad, severidad, descripcion FROM severidades WHERE activo = true LIMIT 10")
            # Filtrar 'Sin severidad' (severidad 0) para el registro regular
            data = [d for d in data if d.get("severidad") != 0]
            data.sort(key=lambda x: x.get("severidad", 0))
        except Exception as exc:
            logger.warning(f"Error querying severidades from Pinot: {exc}")
            data = []
        
        if not data:
            data = [
                {"idseveridad": 1, "severidad": 1, "descripcion": "Leve (Daños materiales mínimos)"},
                {"idseveridad": 2, "severidad": 2, "descripcion": "Moderada (Lesiones leves, un carril obstruido)"},
                {"idseveridad": 3, "severidad": 3, "descripcion": "Grave (Heridos graves, obstrucción total)"},
                {"idseveridad": 4, "severidad": 4, "descripcion": "Crítica (Fallecidos, rescate activo)"}
            ]

        serializer = SeveridadSerializer(data, many=True)
        return Response(serializer.data)


class TipoReportadoListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        data = []
        try:
            # Query from primary database (Apache Pinot)
            query = "SELECT idtiporeportado, tiporeportado FROM tiposreportados WHERE activo = true LIMIT 50"
            rows = PinotRepository.execute_query(query)
            data = [
                {
                    "idtiporeportado": int(r["idtiporeportado"]),
                    "tiporeportado": r["tiporeportado"]
                } for r in rows if r.get("tiporeportado") != "N/A"
            ]
        except Exception as exc:
            logger.warning(f"Error querying report types from Pinot: {exc}")

        # Fallback ONLY if Pinot is empty/fails
        if not data:
            data = [
                {"idtiporeportado": 1, "tiporeportado": "Llamada de emergencia 911"},
                {"idtiporeportado": 2, "tiporeportado": "Camara de seguridad/ transito"}
            ]

        # Ensure order by ID
        data.sort(key=lambda x: x["idtiporeportado"])
        serializer = TipoReportadoSerializer(data, many=True)
        return Response(serializer.data)


class TipoEstadoListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        data = []
        try:
            # Query from primary database (Apache Pinot)
            query = "SELECT idtipoestadoincidente, tipoestadoincidente FROM tiposestadosincidentes WHERE activo = true LIMIT 100"
            rows = PinotRepository.execute_query(query)
            # Exclude fallback "N/A" state if present
            data = [
                {
                    "idtipoestadoincidente": int(r["idtipoestadoincidente"]),
                    "tipoestadoincidente": r["tipoestadoincidente"]
                } for r in rows if r.get("tipoestadoincidente") != "N/A"
            ]
        except Exception as exc:
            logger.warning(f"Error querying state catalog from Pinot: {exc}")
            
        # Fallback to seed data only if Pinot returned empty or failed
        if not data:
            data = SEED_TIPOS_ESTADOS

        # Ensure order by ID
        data.sort(key=lambda x: x["idtipoestadoincidente"])
        serializer = TipoEstadoIncidenteSerializer(data, many=True)
        return Response(serializer.data)


class PaisListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            data = PinotRepository.execute_query("SELECT idpais, pais FROM paises WHERE activo = true LIMIT 100")
            data = [d for d in data if d.get("pais") != "N/A"]
        except Exception as exc:
            logger.warning(f"Error quering paises from Pinot: {exc}")
            data = []
        
        if not data:
            data = SEED_PAISES

        serializer = PaisSerializer(data, many=True)
        return Response(serializer.data)


class EstadoListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        pais_param = request.query_params.get("pais")
        try:
            if pais_param:
                sql = f"SELECT idestado, estado, pais FROM estados WHERE activo = true AND pais = '{pais_param}' LIMIT 100"
            else:
                sql = "SELECT idestado, estado, pais FROM estados WHERE activo = true LIMIT 100"
            data = PinotRepository.execute_query(sql)
            data = [d for d in data if d.get("estado") != "N/A"]
        except Exception as exc:
            logger.warning(f"Error querying estados from Pinot: {exc}")
            data = []
        
        if not data:
            if pais_param:
                data = [e for e in SEED_ESTADOS if e["pais"].upper() == pais_param.upper()]
            else:
                data = SEED_ESTADOS

        serializer = EstadoSerializer(data, many=True)
        return Response(serializer.data)


class CondadoListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        estado_param = request.query_params.get("estado")
        try:
            if estado_param:
                sql = f"SELECT idcondado, condado, estado FROM condados WHERE activo = true AND estado = '{estado_param}' LIMIT 200"
            else:
                sql = "SELECT idcondado, condado, estado FROM condados WHERE activo = true LIMIT 200"
            data = PinotRepository.execute_query(sql)
            data = [d for d in data if d.get("condado") != "N/A"]
        except Exception as exc:
            logger.warning(f"Error querying condados from Pinot: {exc}")
            data = []
        
        if not data:
            if estado_param:
                data = [c for c in SEED_CONDADOS if c["estado"].upper() == estado_param.upper()]
            else:
                data = SEED_CONDADOS

        serializer = CondadoSerializer(data, many=True)
        return Response(serializer.data)


class CiudadListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        condado_param = request.query_params.get("condado")
        try:
            if condado_param:
                sql = f"SELECT idciudad, ciudad, condado FROM ciudades WHERE activo = true AND condado = '{condado_param}' LIMIT 500"
            else:
                sql = "SELECT idciudad, ciudad, condado FROM ciudades WHERE activo = true LIMIT 500"
            data = PinotRepository.execute_query(sql)
            data = [d for d in data if d.get("ciudad") != "N/A"]
        except Exception as exc:
            logger.warning(f"Error querying ciudades from Pinot: {exc}")
            data = []
        
        if not data:
            if condado_param:
                data = [c for c in SEED_CIUDADES if c["condado"].upper() == condado_param.upper()]
            else:
                data = SEED_CIUDADES

        serializer = CiudadSerializer(data, many=True)
        return Response(serializer.data)


class CalleListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        ciudad_param = request.query_params.get("ciudad")
        try:
            if ciudad_param:
                sql = f"SELECT idcalle, calle, ciudad FROM calles WHERE activo = true AND ciudad = '{ciudad_param}' LIMIT 1000"
            else:
                sql = "SELECT idcalle, calle, ciudad FROM calles WHERE activo = true LIMIT 1000"
            data = PinotRepository.execute_query(sql)
            data = [d for d in data if d.get("calle") != "N/A"]
        except Exception as exc:
            logger.warning(f"Error querying calles from Pinot: {exc}")
            data = []
        
        if not data:
            if ciudad_param:
                data = [c for c in SEED_CALLES if c["ciudad"].upper() == ciudad_param.upper()]
            else:
                data = SEED_CALLES

        serializer = CalleSerializer(data, many=True)
        return Response(serializer.data)


class ClimaListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            data = PinotRepository.execute_query("SELECT idestadoclima, condicionclima, direccionviento, temperaturaf, sensaciontermicaf, humedadporcentaje, presionpulgadas, visibilidadmillas, velocidadvientomph, precipitacionpulgadas FROM estadoclima WHERE activo = true LIMIT 100")
            data = [d for d in data if d.get("condicionclima") != "N/A"]
        except Exception as exc:
            logger.warning(f"Error querying clima from Pinot: {exc}")
            data = []
        
        if not data:
            data = SEED_CLIMAS

        serializer = ClimaSerializer(data, many=True)
        return Response(serializer.data)


class ElementoFisicoListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            data = PinotRepository.execute_query("SELECT idelementofisico, cercacruce, cercasemaforo, cercaparada, cercaestacion, cercabache, cercaviatren FROM elementosfisicos WHERE activo = true LIMIT 100")
        except Exception as exc:
            logger.warning(f"Error querying elementos fisicos from Pinot: {exc}")
            data = []
        
        if not data:
            data = SEED_ELEMENTOS

        serializer = ElementoFisicoSerializer(data, many=True)
        return Response(serializer.data)


class PeriodoDiaListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            data = PinotRepository.execute_query("SELECT idperiododia, amaneceranochecer, crepusculocivil, crepusculonautico, crepusculoastronomico FROM periodosdias WHERE activo = true LIMIT 100")
        except Exception as exc:
            logger.warning(f"Error querying periodos dias from Pinot: {exc}")
            data = []
        
        if not data:
            data = SEED_PERIODOS

        serializer = PeriodoDiaSerializer(data, many=True)
        return Response(serializer.data)
