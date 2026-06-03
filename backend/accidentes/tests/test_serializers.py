from django.test import TestCase
from accidentes.PKG1_Gestion_Accidentes.CU01_Registrar_Accidente.serializers import (
    AccidenteRegistroSerializer, VehiculoDetalleSerializer
)
from accidentes.PKG1_Gestion_Accidentes.CU03_Actualizar_Estado.serializers import (
    ActualizarEstadoSerializer
)


class VehiculoDetalleSerializerTest(TestCase):
    def test_valid_data(self):
        data = {"tipovehiculo": "Sedan", "modelovehiculo": "Toyota"}
        s = VehiculoDetalleSerializer(data=data)
        self.assertTrue(s.is_valid())

    def test_empty_data_uses_defaults(self):
        s = VehiculoDetalleSerializer(data={})
        self.assertTrue(s.is_valid())
        self.assertEqual(s.validated_data["tipovehiculo"], "Automóvil")
        self.assertEqual(s.validated_data["modelovehiculo"], "Genérico")


class AccidenteRegistroSerializerTest(TestCase):
    def test_minimal_valid_data(self):
        data = {
            "latitudinicio": -0.18,
            "longitudinicio": -78.46,
            "numheridos": 0,
            "numfallecidos": 0,
            "numvehiculos": 1,
            "descripcion": "Accidente de prueba con mínimo de caracteres",
            "idpais_id": 1,
            "idestado_id": 1,
            "idcondado_id": 1,
            "idciudad_id": 1,
            "idcalle_id": 1,
            "idtiporeportado_id": 1,
        }
        s = AccidenteRegistroSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_missing_required_latitud(self):
        data = {"longitudinicio": -78.46, "numheridos": 0, "numfallecidos": 0,
                "numvehiculos": 1, "descripcion": "Accidente de prueba en serializer",
                "idpais_id": 1, "idestado_id": 1, "idcondado_id": 1,
                "idciudad_id": 1, "idcalle_id": 1, "idtiporeportado_id": 1}
        s = AccidenteRegistroSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("latitudinicio", s.errors)

    def test_invalid_numheridos_negative(self):
        data = {"latitudinicio": -0.18, "longitudinicio": -78.46,
                "numheridos": -1, "numfallecidos": 0, "numvehiculos": 1,
                "descripcion": "Accidente de prueba en serializer",
                "idpais_id": 1, "idestado_id": 1, "idcondado_id": 1,
                "idciudad_id": 1, "idcalle_id": 1, "idtiporeportado_id": 1}
        s = AccidenteRegistroSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("numheridos", s.errors)


class ActualizarEstadoSerializerTest(TestCase):
    def test_valid_estado_id(self):
        s = ActualizarEstadoSerializer(data={"idtipoestadoincidente_id": 2})
        self.assertTrue(s.is_valid())

    def test_missing_required(self):
        s = ActualizarEstadoSerializer(data={})
        self.assertFalse(s.is_valid())
        self.assertIn("idtipoestadoincidente_id", s.errors)

    def test_with_nota(self):
        s = ActualizarEstadoSerializer(data={"idtipoestadoincidente_id": 3, "nota": "Test note"})
        self.assertTrue(s.is_valid())
        self.assertEqual(s.validated_data["nota"], "Test note")
