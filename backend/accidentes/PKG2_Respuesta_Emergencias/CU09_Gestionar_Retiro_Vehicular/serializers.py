from rest_framework import serializers


class RetiroSolicitarSerializer(serializers.Serializer):
    idaccidente = serializers.IntegerField()
    idunidademergencia = serializers.IntegerField()
    descripcion = serializers.CharField(required=False, allow_blank=True, default='')


class RetiroAceptarSerializer(serializers.Serializer):
    nota = serializers.CharField(required=False, allow_blank=True, default='')


class RetiroFinalizarSerializer(serializers.Serializer):
    nota_informe = serializers.CharField(required=True)
    urls_fotos = serializers.ListField(
        child=serializers.URLField(), required=False, default=[]
    )


class RetiroSerializer(serializers.Serializer):
    iddespacho = serializers.IntegerField()
    idaccidente = serializers.IntegerField()
    idunidademergencia = serializers.IntegerField()
    fechahoradespacho = serializers.CharField(required=False, allow_blank=True, default='')
    fechahorallegada = serializers.CharField(required=False, allow_blank=True, default='', allow_null=True)
    activo = serializers.BooleanField(required=False, default=True)
