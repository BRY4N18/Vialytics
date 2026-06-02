from rest_framework import serializers


class UnidadEmergenciaSerializer(serializers.Serializer):
    idunidademergencia = serializers.IntegerField()
    unidademergencia = serializers.CharField()
    tipounidademergencia = serializers.CharField()
    estadounidad = serializers.CharField()
    activo = serializers.BooleanField(required=False, default=True)


class UnidadEstadoUpdateSerializer(serializers.Serializer):
    ESTADOS = ['EN_BASE', 'EN_CAMINO', 'EN_ESCENA', 'EN_TRASLADO', 'REGRESO', 'DISPONIBLE']
    estadounidad = serializers.ChoiceField(choices=ESTADOS)
