from django.db import models
from accidentes.shared.models.hecho import Accidente
from accidentes.shared.models.dimensiones import TipoEstadoIncidente, UnidadEmergencia, Usuario


class AccidenteTipoEstadoIncidente(models.Model):
    idaccidentetipoestadoincidente = models.AutoField(primary_key=True)
    idaccidente = models.ForeignKey(Accidente, on_delete=models.CASCADE, db_column='idaccidente')
    idtipoestadoincidente = models.ForeignKey(
        TipoEstadoIncidente, on_delete=models.PROTECT, db_column='idtipoestadoincidente'
    )
    fechahoramodificado = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'accidentestiposestadosincidentes'
        ordering = ['-fechahoramodificado']


class Despacho(models.Model):
    iddespacho = models.AutoField(primary_key=True)
    idaccidente = models.ForeignKey(Accidente, on_delete=models.CASCADE, db_column='idaccidente')
    idunidademergencia = models.ForeignKey(
        UnidadEmergencia, on_delete=models.PROTECT, db_column='idunidademergencia'
    )
    fechahoradespacho = models.DateTimeField(auto_now_add=True)
    fechahoraconfirmacion = models.DateTimeField(null=True, blank=True)
    fechahorallegada = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'despachos'


class NotaAccidente(models.Model):
    idnotaaccidentes = models.AutoField(primary_key=True)
    idaccidente = models.ForeignKey(Accidente, on_delete=models.CASCADE, db_column='idaccidente')
    idusuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='idusuario')
    nota = models.TextField()
    tipo = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'notasaccidentes'
        ordering = ['-fecha_actualizacion']
