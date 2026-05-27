import uuid
from django.db import models
from .dimensiones import (
    Severidad, TipoReportado, Calle, Ciudad, Condado,
    EstadoGeografico, Pais, PeriodoDia, EstadoClima,
    ElementoFisico, ReferenciaEstacion, Fecha, Usuario,
)


class AccidenteManager(models.Manager):
    def activos(self):
        return self.get_queryset().filter(activo=True).select_related(
            'idseveridad', 'idcalle', 'idciudad', 'idtiporeportado'
        )

    def con_detalle_completo(self):
        return self.activos().prefetch_related(
            'accidentetipoestadoincidente_set__idtipoestadoincidente',
            'despacho_set__idunidademergencia',
            'notaaccidente_set',
        )


class Accidente(models.Model):
    idaccidente = models.CharField(
        max_length=36, primary_key=True, default=uuid.uuid4, editable=False
    )
    idseveridad = models.ForeignKey(Severidad, on_delete=models.PROTECT, db_column='idseveridad')
    idcalle = models.ForeignKey(Calle, on_delete=models.PROTECT, db_column='idcalle')
    idciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, db_column='idciudad')
    idcondado = models.ForeignKey(
        Condado, on_delete=models.PROTECT, db_column='idcondado', null=True, blank=True
    )
    idestado = models.ForeignKey(
        EstadoGeografico, on_delete=models.PROTECT, db_column='idestado', null=True, blank=True
    )
    idpais = models.ForeignKey(
        Pais, on_delete=models.PROTECT, db_column='idpais', null=True, blank=True
    )
    idperiododia = models.ForeignKey(
        PeriodoDia, on_delete=models.PROTECT, db_column='idperiododia', null=True, blank=True
    )
    idestadoclima = models.ForeignKey(
        EstadoClima, on_delete=models.PROTECT, db_column='idestadoclima', null=True, blank=True
    )
    idusuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='idusuario')
    idelementofisico = models.ForeignKey(
        ElementoFisico, on_delete=models.PROTECT, db_column='idelementofisico', null=True, blank=True
    )
    idtiporeportado = models.ForeignKey(
        TipoReportado, on_delete=models.PROTECT, db_column='idtiporeportado'
    )
    idreferenciaestacion = models.ForeignKey(
        ReferenciaEstacion, on_delete=models.SET_NULL, null=True, blank=True,
        db_column='idreferenciaestacion'
    )
    idfecha = models.ForeignKey(
        Fecha, on_delete=models.SET_NULL, null=True, blank=True, db_column='idfecha'
    )
    horainicio = models.TimeField()
    horafin = models.TimeField(null=True, blank=True)
    descripcion = models.TextField()
    codigopostal = models.CharField(max_length=10, blank=True)
    activo = models.BooleanField(default=True)
    duracionminutos = models.IntegerField(null=True, blank=True)
    numvehiculos = models.PositiveIntegerField(default=1)
    numvictimas = models.PositiveIntegerField(default=0)
    numheridos = models.PositiveIntegerField(default=0)
    numfallecidos = models.PositiveIntegerField(default=0)
    latitudinicio = models.DecimalField(max_digits=12, decimal_places=8)
    longitudinicio = models.DecimalField(max_digits=12, decimal_places=8)
    distanciamillas = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    fechahoraclima = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    objects = AccidenteManager()

    class Meta:
        db_table = 'accidentes'
        ordering = ['-fecha_actualizacion']
        indexes = [
            models.Index(fields=['activo', 'fecha_actualizacion']),
            models.Index(fields=['latitudinicio', 'longitudinicio']),
        ]

    def __str__(self):
        return f'Accidente {str(self.idaccidente)[:8]}'
