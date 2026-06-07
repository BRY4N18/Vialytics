from django.urls import path
from accidentes.PKG1_Gestion_Accidentes.CU01_Registrar_Accidente.views import AccidenteRegistroView
from accidentes.PKG1_Gestion_Accidentes.CU02_Visualizar_Mapa.views import AccidenteMapaView
from accidentes.PKG1_Gestion_Accidentes.CU03_Actualizar_Estado.views import AccidenteEstadoView
from accidentes.PKG1_Gestion_Accidentes.CU04_Despachar_Emergencias.views import DespachoView
from accidentes.PKG2_Respuesta_Emergencias.CU07_Recibir_Despacho.views import DespachoUnidadView, DespachoLLegadaView, NotificacionListView, NotificacionAceptarView
from accidentes.PKG2_Respuesta_Emergencias.CU08_Actualizar_Estado_Unidad.views import UnidadEstadoView
from accidentes.PKG2_Respuesta_Emergencias.CU22_Gestionar_Unidades_Emergencia.views import (
    UnidadEmergenciaListCreateView, UnidadEmergenciaDetailView, UnidadEmergenciaActivarView
)
from accidentes.PKG2_Respuesta_Emergencias.CU09_Gestionar_Retiro_Vehicular.views import RetiroSolicitarView, RetiroAceptarView, RetiroFinalizarView, RetiroListView
from accidentes.PKG3_Consulta_Analisis.CU10_Buscar_Accidentes.views import AccidenteBusquedaView
from accidentes.PKG3_Consulta_Analisis.CU14_Solicitar_Expediente.views import AccidenteDetalleView, AccidenteExpedienteView
from accidentes.PKG1_Gestion_Accidentes.CU20_Dashboard_KPIs.views import AccidenteDashboardView
from accidentes.PKG5_Administracion.CU21_Iniciar_Sesion.views import LoginView, VerifyTokenView, RefreshTokenView
from accidentes.PKG4_Portal_Externo.CU15_Consultar_Mapa_Publico.views import MapaPublicoView
from accidentes.PKG4_Portal_Externo.CU16_Consultar_Estadisticas.views import EstadisticasPublicasView
from accidentes.shared.catalogo_views import (
    SeveridadListView, TipoReportadoListView, TipoEstadoListView,
    PaisListView, EstadoListView, CondadoListView, CiudadListView,
    CalleListView, ClimaListView, ElementoFisicoListView, PeriodoDiaListView,
    EstadoUnidadListView, TipoUnidadListView,
)

urlpatterns = [
    # Autenticación
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='auth-refresh'),
    path('auth/verify/', VerifyTokenView.as_view(), name='auth-verify'),
    # Portal público (PKG-4)
    path('public/mapa/', MapaPublicoView.as_view(), name='public-mapa'),
    path('public/estadisticas/', EstadisticasPublicasView.as_view(), name='public-estadisticas'),
    # Gestión de Accidentes (PKG-1)
    path('accidentes/dashboard/', AccidenteDashboardView.as_view(), name='accidente-dashboard'),
    path('accidentes/', AccidenteRegistroView.as_view(), name='accidente-registro'),
    path('accidentes/buscar/', AccidenteBusquedaView.as_view(), name='accidente-busqueda'),
    path('accidentes/mapa/', AccidenteMapaView.as_view(), name='accidente-mapa'),
    path('accidentes/<str:accidente_id>/', AccidenteDetalleView.as_view(), name='accidente-detalle'),
    path('accidentes/<str:accidente_id>/estado/', AccidenteEstadoView.as_view(), name='accidente-estado'),
    path('accidentes/<str:accidente_id>/despachos/', DespachoView.as_view(), name='accidente-despacho'),
    path('accidentes/<str:accidente_id>/expediente/', AccidenteExpedienteView.as_view(), name='accidente-expediente'),
    # Respuesta a Emergencias (PKG-2)
    path('unidades/', UnidadEmergenciaListCreateView.as_view(), name='unidades-lista'),
    path('unidades/<int:unidad_id>/', UnidadEmergenciaDetailView.as_view(), name='unidad-detalle'),
    path('unidades/<int:unidad_id>/estado/', UnidadEstadoView.as_view(), name='unidad-estado'),
    path('unidades/<int:unidad_id>/activar/', UnidadEmergenciaActivarView.as_view(), name='unidad-activar'),
    path('despachos/unidad/<int:unidad_id>/', DespachoUnidadView.as_view(), name='despacho-unidad'),
    path('despachos/<int:despacho_id>/llegada/', DespachoLLegadaView.as_view(), name='despacho-llegada'),
    path('notificaciones/', NotificacionListView.as_view(), name='notificaciones-lista'),
    path('notificaciones/<int:notificacion_id>/aceptar/', NotificacionAceptarView.as_view(), name='notificacion-aceptar'),
    path('retiros/', RetiroListView.as_view(), name='retiros-lista'),
    path('retiros/solicitar/', RetiroSolicitarView.as_view(), name='retiro-solicitar'),
    path('retiros/<int:retiro_id>/aceptar/', RetiroAceptarView.as_view(), name='retiro-aceptar'),
    path('retiros/<int:retiro_id>/finalizar/', RetiroFinalizarView.as_view(), name='retiro-finalizar'),
    # Catálogos (Shared)
    path('tipos-reportado/', TipoReportadoListView.as_view(), name='tipos-reportado'),
    path('severidades/', SeveridadListView.as_view(), name='severidades'),
    path('tipos-estado/', TipoEstadoListView.as_view(), name='tipos-estado'),
    path('paises/', PaisListView.as_view(), name='paises'),
    path('estados/', EstadoListView.as_view(), name='estados'),
    path('condados/', CondadoListView.as_view(), name='condados'),
    path('ciudades/', CiudadListView.as_view(), name='ciudades'),
    path('calles/', CalleListView.as_view(), name='calles'),
    path('climas/', ClimaListView.as_view(), name='climas'),
    path('elementos-fisicos/', ElementoFisicoListView.as_view(), name='elementos-fisicos'),
    path('periodos-dias/', PeriodoDiaListView.as_view(), name='periodos-dias'),
    path('estados-unidad/', EstadoUnidadListView.as_view(), name='estados-unidad'),
    path('tipos-unidad/', TipoUnidadListView.as_view(), name='tipos-unidad'),
]
