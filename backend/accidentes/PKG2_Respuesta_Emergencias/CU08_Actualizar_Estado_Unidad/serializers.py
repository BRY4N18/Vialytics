from rest_framework import serializers


class UnidadEmergenciaSerializer(serializers.Serializer):
    idunidademergencia = serializers.IntegerField()
    unidademergencia = serializers.CharField()
    tipounidademergencia = serializers.CharField()
    estadounidad = serializers.CharField()
    activo = serializers.BooleanField(required=False, default=True)


class UnidadEstadoUpdateSerializer(serializers.Serializer):
    ESTADOS = ['En base', 'En camino', 'En escena', 'En traslado', 'Regreso', 'Disponible']
    estadounidad = serializers.ChoiceField(choices=ESTADOS)
