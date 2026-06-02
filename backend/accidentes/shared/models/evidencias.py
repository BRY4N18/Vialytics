from django.db import models
from accidentes.shared.models.hecho import Accidente


class EvidenciaFoto(models.Model):
    idevidenciafoto = models.AutoField(primary_key=True)
    idaccidente = models.ForeignKey(Accidente, on_delete=models.CASCADE, db_column='idaccidente')
    urlevidenciafoto = models.URLField(max_length=500)
    fechahora = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'evidenciasfotos'
