from django.db import models
from .hecho import Accidente
from .vehiculos import Vehiculo


class Conductor(models.Model):
    idconductor = models.AutoField(primary_key=True)
    apellidos = models.CharField(max_length=100)
    nombres = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=20, unique=True)
    genero = models.CharField(max_length=1)
    tipolicencia = models.CharField(max_length=10)
    estadolicencia = models.CharField(max_length=20)
    ciudadresidencia = models.CharField(max_length=100)
    aniosexperiencia = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conductores'


class EstadoConductor(models.Model):
    idestadoconductor = models.AutoField(primary_key=True)
    estadosobriedad = models.BooleanField(default=True)
    nivelatencion = models.BooleanField(default=True)
    condicionfisica = models.BooleanField(default=True)
    usoseguridad = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'estadosconductores'


class ConductorAccidente(models.Model):
    idconductoraccidente = models.AutoField(primary_key=True)
    idaccidente = models.ForeignKey(Accidente, on_delete=models.CASCADE, db_column='idaccidente')
    idconductor = models.ForeignKey(Conductor, on_delete=models.PROTECT, db_column='idconductor')
    idestadoconductor = models.ForeignKey(
        EstadoConductor, on_delete=models.PROTECT, db_column='idestadoconductor'
    )
    idvehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, db_column='idvehiculo')
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conductoresaccidentes'


class Implicado(models.Model):
    TIPOS = [
        ('CONDUCTOR', 'Conductor'),
        ('PASAJERO', 'Pasajero'),
        ('PEATON', 'Peatón'),
        ('OTRO', 'Otro'),
    ]
    ESTADOS = [
        ('ILESO', 'Ileso'),
        ('HERIDO_LEVE', 'Herido Leve'),
        ('HERIDO_GRAVE', 'Herido Grave'),
        ('FALLECIDO', 'Fallecido'),
    ]
    idimplicado = models.AutoField(primary_key=True)
    idaccidente = models.ForeignKey(Accidente, on_delete=models.CASCADE, db_column='idaccidente')
    tipoimplicado = models.CharField(max_length=20, choices=TIPOS)
    genero = models.CharField(max_length=1)
    estadoimplicado = models.CharField(max_length=20, choices=ESTADOS)
    edad = models.IntegerField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'implicados'
