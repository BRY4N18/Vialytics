from rest_framework import serializers


class SeveridadSerializer(serializers.Serializer):
    idseveridad = serializers.IntegerField()
    severidad = serializers.IntegerField()
    descripcion = serializers.CharField()


class TipoReportadoSerializer(serializers.Serializer):
    idtiporeportado = serializers.IntegerField()
    tiporeportado = serializers.CharField()


class PaisSerializer(serializers.Serializer):
    idpais = serializers.IntegerField()
    pais = serializers.CharField()


class EstadoSerializer(serializers.Serializer):
    idestado = serializers.IntegerField()
    estado = serializers.CharField()
    pais = serializers.CharField()


class CondadoSerializer(serializers.Serializer):
    idcondado = serializers.IntegerField()
    condado = serializers.CharField()
    estado = serializers.CharField()


class CiudadSerializer(serializers.Serializer):
    idciudad = serializers.IntegerField()
    ciudad = serializers.CharField()
    condado = serializers.CharField()


class CalleSerializer(serializers.Serializer):
    idcalle = serializers.IntegerField()
    calle = serializers.CharField()
    ciudad = serializers.CharField()


class ClimaSerializer(serializers.Serializer):
    idestadoclima = serializers.IntegerField()
    condicionclima = serializers.CharField()
    direccionviento = serializers.CharField()
    temperaturaf = serializers.FloatField()
    sensaciontermicaf = serializers.FloatField()
    humedadporcentaje = serializers.FloatField()
    presionpulgadas = serializers.FloatField()
    visibilidadmillas = serializers.FloatField()
    velocidadvientomph = serializers.FloatField()
    precipitacionpulgadas = serializers.FloatField()


class ElementoFisicoSerializer(serializers.Serializer):
    idelementofisico = serializers.IntegerField()
    cercacruce = serializers.BooleanField()
    cercasemaforo = serializers.BooleanField()
    cercaparada = serializers.BooleanField()
    cercaestacion = serializers.BooleanField()
    cercabache = serializers.BooleanField()
    cercaviatren = serializers.BooleanField()


class PeriodoDiaSerializer(serializers.Serializer):
    idperiododia = serializers.IntegerField()
    amaneceranochecer = serializers.CharField()
    crepusculocivil = serializers.CharField()
    crepusculonautico = serializers.CharField()
    crepusculoastronomico = serializers.CharField()
