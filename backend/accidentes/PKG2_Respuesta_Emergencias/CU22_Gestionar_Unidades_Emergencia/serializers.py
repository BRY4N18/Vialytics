from rest_framework import serializers


class UnidadEmergenciaCrearSerializer(serializers.Serializer):
    unidademergencia = serializers.CharField(max_length=100)
    tipounidad_id = serializers.IntegerField()


class UnidadEmergenciaActualizarSerializer(serializers.Serializer):
    unidademergencia = serializers.CharField(max_length=100)
    tipounidad_id = serializers.IntegerField()


class UnidadEmergenciaActivarSerializer(serializers.Serializer):
    activo = serializers.BooleanField()


class UnidadEmergenciaSerializer(serializers.Serializer):
    idunidademergencia = serializers.IntegerField()
    unidademergencia = serializers.CharField()
    tipounidademergencia = serializers.CharField()
    estadounidad = serializers.CharField()
    activo = serializers.BooleanField(required=False, default=True)
