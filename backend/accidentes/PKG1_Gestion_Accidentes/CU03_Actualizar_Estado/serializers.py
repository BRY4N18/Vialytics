from rest_framework import serializers


class ActualizarEstadoSerializer(serializers.Serializer):
    idtipoestadoincidente_id = serializers.IntegerField()
    nota = serializers.CharField(required=False, allow_blank=True, default='')


class NotaAccidenteSerializer(serializers.Serializer):
    idnotaaccidentes = serializers.IntegerField()
    idaccidente = serializers.CharField()
    nota = serializers.CharField()
    tipo = serializers.BooleanField(required=False, default=True)
    fecha_actualizacion = serializers.CharField()
