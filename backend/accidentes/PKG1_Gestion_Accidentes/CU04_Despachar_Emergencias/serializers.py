from rest_framework import serializers


class DespachoSerializer(serializers.Serializer):
    iddespacho = serializers.IntegerField()
    idaccidente = serializers.CharField()
    idunidademergencia = serializers.IntegerField()
    unidad_nombre = serializers.CharField(required=False, allow_blank=True, default='')
    tipo_unidad = serializers.CharField(required=False, allow_blank=True, default='')
    fechahoradespacho = serializers.CharField(required=False, allow_blank=True, default='')
    fechahoraconfirmacion = serializers.CharField(required=False, allow_blank=True, default='')
    fechahorallegada = serializers.CharField(required=False, allow_blank=True, default='')


class DespachoCrearSerializer(serializers.Serializer):
    unidades_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
