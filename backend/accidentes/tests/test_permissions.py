from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import Mock

from accidentes.shared.permissions import (
    get_user_role, USUARIOS_ROLES,
    EsOperador, EsAdministrador, EsAnalista, EsDespachador,
    EsOperadorOAdministrador, EsOperadorOAnalistaOAdministrador,
    EsDespachadorOAdministrador,
)


class GetUserRoleTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin_sga', password='test')
        self.operador = User.objects.create_user(username='operador_sga', password='test')
        self.analista = User.objects.create_user(username='analista_sga', password='test')
        self.despachador = User.objects.create_user(username='despachador_sga', password='test')
        self.unknown = User.objects.create_user(username='unknown', password='test')

    def test_admin_role(self):
        self.assertEqual(get_user_role(self.admin), 'Administrador')

    def test_operador_role(self):
        self.assertEqual(get_user_role(self.operador), 'Operador')

    def test_analista_role(self):
        self.assertEqual(get_user_role(self.analista), 'Consumidor Analítico')

    def test_despachador_role(self):
        self.assertEqual(get_user_role(self.despachador), 'Despachador')

    def test_unknown_user_returns_empty(self):
        self.assertEqual(get_user_role(self.unknown), '')

    def test_unauthenticated_returns_empty(self):
        anon = Mock(is_authenticated=False)
        self.assertEqual(get_user_role(anon), '')

    def test_none_returns_empty(self):
        self.assertEqual(get_user_role(None), '')


def _make_request(role):
    user = Mock(is_authenticated=True)
    user.username = {'Administrador': 'admin_sga', 'Operador': 'operador_sga',
                     'Consumidor Analítico': 'analista_sga', 'Despachador': 'despachador_sga'}.get(role, 'unknown')
    return Mock(user=user)


class TestEsOperador(TestCase):
    def test_operador_allowed(self):
        p = EsOperador()
        self.assertTrue(p.has_permission(_make_request('Operador'), None))

    def test_admin_denied(self):
        p = EsOperador()
        self.assertFalse(p.has_permission(_make_request('Administrador'), None))

    def test_analista_denied(self):
        p = EsOperador()
        self.assertFalse(p.has_permission(_make_request('Consumidor Analítico'), None))


class TestEsAdministrador(TestCase):
    def test_admin_allowed(self):
        p = EsAdministrador()
        self.assertTrue(p.has_permission(_make_request('Administrador'), None))

    def test_operador_denied(self):
        p = EsAdministrador()
        self.assertFalse(p.has_permission(_make_request('Operador'), None))


class TestEsAnalista(TestCase):
    def test_analista_allowed(self):
        p = EsAnalista()
        self.assertTrue(p.has_permission(_make_request('Consumidor Analítico'), None))

    def test_operador_denied(self):
        p = EsAnalista()
        self.assertFalse(p.has_permission(_make_request('Operador'), None))


class TestEsDespachador(TestCase):
    def test_despachador_allowed(self):
        p = EsDespachador()
        self.assertTrue(p.has_permission(_make_request('Despachador'), None))

    def test_operador_denied(self):
        p = EsDespachador()
        self.assertFalse(p.has_permission(_make_request('Operador'), None))


class TestEsOperadorOAdministrador(TestCase):
    def test_operador_allowed(self):
        p = EsOperadorOAdministrador()
        self.assertTrue(p.has_permission(_make_request('Operador'), None))

    def test_admin_allowed(self):
        p = EsOperadorOAdministrador()
        self.assertTrue(p.has_permission(_make_request('Administrador'), None))

    def test_analista_denied(self):
        p = EsOperadorOAdministrador()
        self.assertFalse(p.has_permission(_make_request('Consumidor Analítico'), None))


class TestEsOperadorOAnalistaOAdministrador(TestCase):
    def test_operador_allowed(self):
        p = EsOperadorOAnalistaOAdministrador()
        self.assertTrue(p.has_permission(_make_request('Operador'), None))

    def test_admin_allowed(self):
        p = EsOperadorOAnalistaOAdministrador()
        self.assertTrue(p.has_permission(_make_request('Administrador'), None))

    def test_analista_allowed(self):
        p = EsOperadorOAnalistaOAdministrador()
        self.assertTrue(p.has_permission(_make_request('Consumidor Analítico'), None))

    def test_despachador_denied(self):
        p = EsOperadorOAnalistaOAdministrador()
        self.assertFalse(p.has_permission(_make_request('Despachador'), None))


class TestEsDespachadorOAdministrador(TestCase):
    def test_despachador_allowed(self):
        p = EsDespachadorOAdministrador()
        self.assertTrue(p.has_permission(_make_request('Despachador'), None))

    def test_admin_allowed(self):
        p = EsDespachadorOAdministrador()
        self.assertTrue(p.has_permission(_make_request('Administrador'), None))

    def test_operador_denied(self):
        p = EsDespachadorOAdministrador()
        self.assertFalse(p.has_permission(_make_request('Operador'), None))
