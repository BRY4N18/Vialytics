from django.test import TestCase
from accidentes.PKG1_Gestion_Accidentes.CU06_Asignar_Severidad.services import SeveridadService


class SeveridadServiceTest(TestCase):
    def test_leve(self):
        self.assertEqual(SeveridadService.calcular(0, 0, 1), 1)

    def test_moderado_1_herido(self):
        self.assertEqual(SeveridadService.calcular(1, 0, 1), 2)

    def test_moderado_2_vehiculos(self):
        self.assertEqual(SeveridadService.calcular(0, 0, 2), 2)

    def test_grave_3_heridos(self):
        self.assertEqual(SeveridadService.calcular(3, 0, 1), 3)

    def test_grave_4_vehiculos(self):
        self.assertEqual(SeveridadService.calcular(0, 0, 4), 3)

    def test_grave_3_heridos_y_4_vehiculos(self):
        self.assertEqual(SeveridadService.calcular(3, 0, 4), 3)

    def test_fatal_1_fallecido(self):
        self.assertEqual(SeveridadService.calcular(0, 1, 1), 4)

    def test_fatal_ignores_other_counts(self):
        self.assertEqual(SeveridadService.calcular(10, 1, 10), 4)

    def test_zero_values(self):
        self.assertEqual(SeveridadService.calcular(0, 0, 0), 1)

    def test_large_numbers(self):
        self.assertEqual(SeveridadService.calcular(100, 0, 50), 3)
