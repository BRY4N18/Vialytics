from rest_framework import serializers


class VehiculoDetalleSerializer(serializers.Serializer):
    # Vehiculo fields
    tipovehiculo = serializers.CharField(max_length=50, required=False, default="Automóvil")
    modelovehiculo = serializers.CharField(max_length=100, required=False, default="Genérico")
    categoriausovehiculo = serializers.CharField(max_length=50, required=False, default="Particular")
    mercanciapeligrosa = serializers.BooleanField(required=False, default=False)
    ejes = serializers.IntegerField(required=False, default=2)

    # Conductor fields
    nombres = serializers.CharField(max_length=100, required=False, default="Nombre")
    apellidos = serializers.CharField(max_length=100, required=False, default="Apellido")
    identificacion = serializers.CharField(max_length=20, required=False, default="")
    genero = serializers.CharField(max_length=1, required=False, default="M")
    tipolicencia = serializers.CharField(max_length=10, required=False, default="B")
    estadolicencia = serializers.CharField(max_length=20, required=False, default="Vigente")
    ciudadresidencia = serializers.CharField(max_length=100, required=False, default="Quito")
    aniosexperiencia = serializers.IntegerField(required=False, default=0)

    # Estado Conductor fields
    estadosobriedad = serializers.BooleanField(required=False, default=True)
    nivelatencion = serializers.BooleanField(required=False, default=True)
    condicionfisica = serializers.BooleanField(required=False, default=True)
    usoseguridad = serializers.BooleanField(required=False, default=True)


class AccidenteRegistroSerializer(serializers.Serializer):
    idaccidente = serializers.CharField(read_only=True)
    vehiculos_detalles = VehiculoDetalleSerializer(many=True, required=False)
    latitudinicio = serializers.FloatField()
    longitudinicio = serializers.FloatField()
    numvehiculos = serializers.IntegerField(min_value=1, max_value=50)
    numheridos = serializers.IntegerField(min_value=0, max_value=200)
    numfallecidos = serializers.IntegerField(min_value=0, max_value=100)
    descripcion = serializers.CharField(min_length=10, max_length=500)
    
    # Mapped catalog keys
    idpais_id = serializers.IntegerField()
    idestado_id = serializers.IntegerField()
    idcondado_id = serializers.IntegerField()
    idciudad_id = serializers.IntegerField()
    idcalle_id = serializers.IntegerField()
    idperiododia_id = serializers.IntegerField(required=False)
    idestadoclima_id = serializers.IntegerField(required=False)
    idelementofisico_id = serializers.IntegerField(required=False)
    idtiporeportado_id = serializers.IntegerField()
    idfecha_id = serializers.IntegerField(required=False)
    
    idseveridad_id = serializers.IntegerField(required=False)
    nota_inicial = serializers.CharField(required=False, allow_blank=True, default="")
    codigopostal = serializers.CharField(required=False, allow_blank=True)

    # New detailed weather, elements, period and driver state fields
    condicion_clima = serializers.CharField(required=False, allow_blank=True, default="")
    temperatura_f = serializers.FloatField(required=False, default=72.0)
    humedad_porcentaje = serializers.FloatField(required=False, default=50.0)
    visibilidad_millas = serializers.FloatField(required=False, default=10.0)
    velocidad_viento_mph = serializers.FloatField(required=False, default=0.0)
    
    cerca_cruce = serializers.BooleanField(required=False, default=False)
    cerca_semaforo = serializers.BooleanField(required=False, default=False)
    cerca_parada = serializers.BooleanField(required=False, default=False)
    cerca_estacion = serializers.BooleanField(required=False, default=False)
    cerca_bache = serializers.BooleanField(required=False, default=False)
    cerca_viatren = serializers.BooleanField(required=False, default=False)
    
    estadosobriedad = serializers.BooleanField(required=False, default=True)
    nivelatencion = serializers.BooleanField(required=False, default=True)
    condicionfisica = serializers.BooleanField(required=False, default=True)
    usoseguridad = serializers.BooleanField(required=False, default=True)
    
    amaneceranochecer = serializers.CharField(required=False, allow_blank=True, default="Day")
    crepusculocivil = serializers.CharField(required=False, allow_blank=True, default="Day")
    crepusculonautico = serializers.CharField(required=False, allow_blank=True, default="Day")
    crepusculoastronomico = serializers.CharField(required=False, allow_blank=True, default="Day")
    
    codigoaeropuerto = serializers.CharField(required=False, allow_blank=True, default="KJFK")
    zonahoraria = serializers.CharField(required=False, allow_blank=True, default="US/Eastern")


class AccidenteDetalleSerializer(serializers.Serializer):
    idaccidente = serializers.CharField()
    latitudinicio = serializers.FloatField()
    longitudinicio = serializers.FloatField()
    numvehiculos = serializers.IntegerField()
    numheridos = serializers.IntegerField()
    numfallecidos = serializers.IntegerField()
    numvictimas = serializers.IntegerField()
    descripcion = serializers.CharField()
    horainicio = serializers.CharField()
    horafin = serializers.CharField(required=False, allow_blank=True)
    codigopostal = serializers.CharField(required=False, allow_blank=True)
    fecha_actualizacion = serializers.CharField()
    fechahoraclima = serializers.CharField()
    estado_actual = serializers.CharField()
    calle_nombre = serializers.CharField()
    ciudad_nombre = serializers.CharField()
    severidad_nivel = serializers.IntegerField()
    severidad_descripcion = serializers.CharField()
    despachos = serializers.ListField(child=serializers.DictField())
    notas = serializers.ListField(child=serializers.DictField())


class AccidenteMapaSerializer(serializers.Serializer):
    idaccidente = serializers.CharField()
    latitudinicio = serializers.FloatField()
    longitudinicio = serializers.FloatField()
    severidad_nivel = serializers.IntegerField()
    estado_actual = serializers.CharField()
    numheridos = serializers.IntegerField()
    numfallecidos = serializers.IntegerField()
    fecha_actualizacion = serializers.CharField()
    descripcion = serializers.CharField()
    calle_nombre = serializers.CharField()
    ciudad_nombre = serializers.CharField()
