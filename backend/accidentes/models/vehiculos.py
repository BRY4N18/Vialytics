from django.db import models


class Vehiculo(models.Model):
    idvehiculo = models.AutoField(primary_key=True)
    tipovehiculo = models.CharField(max_length=50)
    modelovehiculo = models.CharField(max_length=100)
    categoriausovehiculo = models.CharField(max_length=50)
    mercanciapeligrosa = models.BooleanField(default=False)
    ejes = models.IntegerField(default=2)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehiculos'
