from django.urls import path
from .views.accidente_views import AccidenteRegistroView, AccidenteMapaView, AccidenteDetalleView, AccidenteDashboardView, AccidenteExpedienteView
from .views.estado_views import AccidenteEstadoView
from .views.despacho_views import DespachoView
from .views.unidad_views import UnidadesEmergenciaView, UnidadEstadoView
from .views.catalogo_views import (
    SeveridadListView, TipoReportadoListView, TipoEstadoListView,
    PaisListView, EstadoListView, CondadoListView, CiudadListView,
    CalleListView, ClimaListView, ElementoFisicoListView, PeriodoDiaListView
)
from .views.auth_views import LoginView, VerifyTokenView, RefreshTokenView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='auth-refresh'),
    path('auth/verify/', VerifyTokenView.as_view(), name='auth-verify'),
    path('accidentes/dashboard/', AccidenteDashboardView.as_view(), name='accidente-dashboard'),
    path('accidentes/', AccidenteRegistroView.as_view(), name='accidente-registro'),
    path('accidentes/mapa/', AccidenteMapaView.as_view(), name='accidente-mapa'),
    path('accidentes/<str:accidente_id>/', AccidenteDetalleView.as_view(), name='accidente-detalle'),
    path('accidentes/<str:accidente_id>/estado/', AccidenteEstadoView.as_view(), name='accidente-estado'),
    path('accidentes/<str:accidente_id>/despachos/', DespachoView.as_view(), name='accidente-despacho'),
    path('accidentes/<str:accidente_id>/expediente/', AccidenteExpedienteView.as_view(), name='accidente-expediente'),
    path('unidades/', UnidadesEmergenciaView.as_view(), name='unidades-lista'),
    path('unidades/<int:unidad_id>/estado/', UnidadEstadoView.as_view(), name='unidad-estado'),
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
]
