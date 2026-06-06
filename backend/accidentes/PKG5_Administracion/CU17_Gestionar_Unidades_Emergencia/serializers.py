from rest_framework import serializers


class UnidadEmergenciaCrearSerializer(serializers.Serializer):
    TIPOS = ['AMBULANCIA', 'BOMBEROS', 'TRANSITO', 'GRUA']

    unidademergencia = serializers.CharField(max_length=100)
    tipounidademergencia = serializers.ChoiceField(choices=TIPOS)


class UnidadEmergenciaActualizarSerializer(serializers.Serializer):
    TIPOS = ['AMBULANCIA', 'BOMBEROS', 'TRANSITO', 'GRUA']

    unidademergencia = serializers.CharField(max_length=100)
    tipounidademergencia = serializers.ChoiceField(choices=TIPOS)


class UnidadEmergenciaActivarSerializer(serializers.Serializer):
    activo = serializers.BooleanField()


class UnidadEmergenciaSerializer(serializers.Serializer):
    idunidademergencia = serializers.IntegerField()
    unidademergencia = serializers.CharField()
    tipounidademergencia = serializers.CharField()
    estadounidad = serializers.CharField()
    activo = serializers.BooleanField(required=False, default=True)
