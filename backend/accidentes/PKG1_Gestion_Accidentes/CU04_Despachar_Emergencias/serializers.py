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
    tipos = serializers.ListField(child=serializers.CharField(), min_length=1, required=False)
    unidad_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1, required=False)

    def validate(self, data):
        if not data.get('tipos') and not data.get('unidad_ids'):
            raise serializers.ValidationError("Debe proporcionar 'tipos' o 'unidad_ids'")
        return data
