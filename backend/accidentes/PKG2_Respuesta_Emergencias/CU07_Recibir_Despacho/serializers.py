from rest_framework import serializers


class AccidenteInfoSerializer(serializers.Serializer):
    idaccidente = serializers.CharField()
    latitudinicio = serializers.FloatField(required=False)
    longitudinicio = serializers.FloatField(required=False)
    numheridos = serializers.IntegerField(required=False, default=0)
    numfallecidos = serializers.IntegerField(required=False, default=0)
    descripcion = serializers.CharField(required=False, allow_blank=True, default='')
    severidad_nivel = serializers.IntegerField(required=False)
    estado_actual = serializers.CharField(required=False, allow_blank=True, default='')
    calle_nombre = serializers.CharField(required=False, allow_blank=True, default='')
    ciudad_nombre = serializers.CharField(required=False, allow_blank=True, default='')


class DespachoPendienteSerializer(serializers.Serializer):
    iddespacho = serializers.IntegerField()
    idaccidente = serializers.CharField()
    idunidademergencia = serializers.IntegerField()
    unidad_nombre = serializers.CharField(required=False, allow_blank=True, default='')
    tipo_unidad = serializers.CharField(required=False, allow_blank=True, default='')
    fechahoradespacho = serializers.CharField(required=False, allow_blank=True, default='')
    fechahoraconfirmacion = serializers.CharField(required=False, allow_blank=True, default='', allow_null=True)
    fechahorallegada = serializers.CharField(required=False, allow_blank=True, default='', allow_null=True)
    accidente = AccidenteInfoSerializer(required=False)


class DespachoConfirmacionSerializer(serializers.Serializer):
    nota = serializers.CharField(required=False, allow_blank=True, default='')
