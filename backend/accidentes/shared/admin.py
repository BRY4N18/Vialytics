from django.contrib import admin
from accidentes.shared.models import (
    Accidente, Severidad, TipoReportado, TipoEstadoIncidente, Calle, Ciudad,
    Condado, EstadoGeografico, Pais, PeriodoDia, EstadoClima, ElementoFisico,
    ReferenciaEstacion, Fecha, UnidadEmergencia, Usuario, AccidenteTipoEstadoIncidente,
    Despacho, NotaAccidente, EvidenciaFoto, Conductor, EstadoConductor,
    ConductorAccidente, Implicado, Vehiculo,
)


@admin.register(Accidente)
class AccidenteAdmin(admin.ModelAdmin):
    list_display = ['idaccidente', 'idcalle', 'idciudad', 'idseveridad', 'numheridos', 'activo', 'fecha_actualizacion']
    list_filter = ['activo', 'idseveridad']
    search_fields = ['idaccidente', 'descripcion']


for modelo in [
    Severidad, TipoReportado, TipoEstadoIncidente, Calle, Ciudad, Condado,
    EstadoGeografico, Pais, PeriodoDia, EstadoClima, ElementoFisico,
    ReferenciaEstacion, Fecha, UnidadEmergencia, Usuario, AccidenteTipoEstadoIncidente,
    Despacho, NotaAccidente, EvidenciaFoto, Conductor, EstadoConductor,
    ConductorAccidente, Implicado, Vehiculo,
]:
    try:
        admin.site.register(modelo)
    except admin.sites.AlreadyRegistered:
        pass
