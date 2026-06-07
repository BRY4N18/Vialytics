from rest_framework import serializers


class AccidenteInfoSerializer(serializers.Serializer):
    idaccidente = serializers.CharField(required=False, allow_blank=True, default='')
    latitudinicio = serializers.FloatField(required=False)
    longitudinicio = serializers.FloatField(required=False)
    numheridos = serializers.IntegerField(required=False, default=0)
    numfallecidos = serializers.IntegerField(required=False, default=0)
    descripcion = serializers.CharField(required=False, allow_blank=True, default='')
    severidad_nivel = serializers.IntegerField(required=False)
    estado_actual = serializers.CharField(required=False, allow_blank=True, default='')
    calle_nombre = serializers.CharField(required=False, allow_blank=True, default='')
    ciudad_nombre = serializers.CharField(required=False, allow_blank=True, default='')


class VehiculoSerializer(serializers.Serializer):
    tipovehiculo = serializers.CharField(required=False, allow_blank=True, default='')
    modelovehiculo = serializers.CharField(required=False, allow_blank=True, default='')
    mercanciapeligrosa = serializers.BooleanField(required=False, default=False)


class DespachoPendienteSerializer(serializers.Serializer):
    iddespacho = serializers.IntegerField()
    idaccidente = serializers.CharField()
    idunidademergencia = serializers.IntegerField()
    unidad_nombre = serializers.CharField(required=False, allow_blank=True, default='')
    tipo_unidad = serializers.CharField(required=False, allow_blank=True, default='')
    fechahoradespacho = serializers.CharField(required=False, allow_blank=True, default='')
    fechahorallegada = serializers.CharField(required=False, allow_blank=True, default='', allow_null=True)
    accidente = AccidenteInfoSerializer(required=False)
    vehiculos = VehiculoSerializer(many=True, required=False, default=[])


class NotificacionSerializer(serializers.Serializer):
    idnotificaciondespacho = serializers.IntegerField()
    idaccidente = serializers.CharField()
    numheridos = serializers.IntegerField(required=False, default=0)
    numvehiculos = serializers.IntegerField(required=False, default=0)
    tipos_necesarios = serializers.ListField(child=serializers.CharField(), required=False, default=[])
    fecha_actualizacion = serializers.CharField(required=False, allow_blank=True, default='')
    accidente = AccidenteInfoSerializer(required=False)
    vehiculos = VehiculoSerializer(many=True, required=False, default=[])


class NotificacionAceptarSerializer(serializers.Serializer):
    unidad_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
