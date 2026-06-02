from django.db import models


class Severidad(models.Model):
    idseveridad = models.AutoField(primary_key=True)
    severidad = models.IntegerField()
    descripcion = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'severidades'


class TipoReportado(models.Model):
    idtiporeportado = models.AutoField(primary_key=True)
    tiporeportado = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'tiposreportados'


class TipoEstadoIncidente(models.Model):
    ESTADOS = [
        ('Reportado', 'Reportado'),
        ('En atencion', 'En atención'),
        ('Atendido', 'Atendido'),
        ('Despejado', 'Despejado'),
        ('Archivado', 'Archivado'),
    ]
    idtipoestadoincidente = models.AutoField(primary_key=True)
    tipoestadoincidente = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'tiposestadosincidentes'


class Calle(models.Model):
    idcalle = models.AutoField(primary_key=True)
    calle = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'calles'


class Ciudad(models.Model):
    idciudad = models.AutoField(primary_key=True)
    ciudad = models.CharField(max_length=100)
    condado = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'ciudades'


class Condado(models.Model):
    idcondado = models.AutoField(primary_key=True)
    condado = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'condados'


class EstadoGeografico(models.Model):
    idestado = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'estados'


class Pais(models.Model):
    idpais = models.AutoField(primary_key=True)
    pais = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'paises'


class PeriodoDia(models.Model):
    idperiododia = models.AutoField(primary_key=True)
    amaneceranochecer = models.CharField(max_length=50)
    crepusculocivil = models.CharField(max_length=50)
    crepusculonautico = models.CharField(max_length=50)
    crepusculoastronomico = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'periodosdias'


class EstadoClima(models.Model):
    idestadoclima = models.AutoField(primary_key=True)
    direccionviento = models.CharField(max_length=50, blank=True)
    condicionclima = models.CharField(max_length=100)
    temperaturaf = models.FloatField(null=True, blank=True)
    sensaciontermicaf = models.FloatField(null=True, blank=True)
    humedadporcentaje = models.FloatField(null=True, blank=True)
    presionpulgadas = models.FloatField(null=True, blank=True)
    visibilidadmillas = models.FloatField(null=True, blank=True)
    velocidadvientomph = models.FloatField(null=True, blank=True)
    precipitacionpulgadas = models.FloatField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'estadoclima'


class ElementoFisico(models.Model):
    idelementofisico = models.AutoField(primary_key=True)
    cercacruce = models.BooleanField(default=False)
    cercasemaforo = models.BooleanField(default=False)
    cercaparada = models.BooleanField(default=False)
    cercaestacion = models.BooleanField(default=False)
    cercabache = models.BooleanField(default=False)
    cercaviatren = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'elementosfisicos'


class ReferenciaEstacion(models.Model):
    idreferenciaestacion = models.AutoField(primary_key=True)
    codigoaeropuerto = models.CharField(max_length=20)
    zonahoraria = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'referenciaestacion'


class Fecha(models.Model):
    idfecha = models.AutoField(primary_key=True)
    fechacompleta = models.CharField(max_length=20)
    anio = models.IntegerField()
    mes = models.IntegerField()
    dia = models.IntegerField()
    trimestre = models.IntegerField()
    semanaanio = models.IntegerField()
    diasemana = models.CharField(max_length=20)
    esfinsemana = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'fechas'


class UnidadEmergencia(models.Model):
    TIPOS = [
        ('AMBULANCIA', 'Ambulancia'),
        ('POLICIA', 'Policía'),
        ('GRUA', 'Grúa'),
        ('BOMBEROS', 'Bomberos'),
    ]
    ESTADOS_UNIDAD = [
        ('EN_BASE', 'En Base'),
        ('EN_CAMINO', 'En Camino'),
        ('EN_ESCENA', 'En Escena'),
        ('EN_TRASLADO', 'En Traslado'),
        ('REGRESO', 'Regreso'),
        ('DISPONIBLE', 'Disponible'),
    ]
    idunidademergencia = models.AutoField(primary_key=True)
    unidademergencia = models.CharField(max_length=100)
    tipounidademergencia = models.CharField(max_length=20, choices=TIPOS)
    estadounidad = models.CharField(max_length=20, choices=ESTADOS_UNIDAD, default='EN_BASE')
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'unidadesemergencia'
        verbose_name = 'Unidad de Emergencia'


class Usuario(models.Model):
    GENEROS = [('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')]
    idusuario = models.AutoField(primary_key=True)
    apellidos = models.CharField(max_length=100)
    nombres = models.CharField(max_length=100)
    gmail = models.EmailField(unique=True)
    identificacion = models.CharField(max_length=20, unique=True)
    genero = models.CharField(max_length=1, choices=GENEROS)
    fechanacimiento = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'accidentes'
        db_table = 'usuarios'
