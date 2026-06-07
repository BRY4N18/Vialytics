from rest_framework.permissions import BasePermission


USUARIOS_ROLES = {
    'operador_sga': {'nombre': 'Laura Mendoza', 'rol': 'Operador'},
    'admin_sga': {'nombre': 'Carlos Gomez', 'rol': 'Administrador'},
    'analista_sga': {'nombre': 'Patricia Vega', 'rol': 'Consumidor Analítico'},
    'despachador_sga': {'nombre': 'David Torres', 'rol': 'Despachador'},
    'unidad_emergencia_sga': {'nombre': 'Unidad Alfa 1', 'rol': 'Unidad de Emergencia'},
}


def get_user_role(user):
    if not user or not user.is_authenticated:
        return ''
    perfil = USUARIOS_ROLES.get(user.username, {})
    return perfil.get('rol', '')


class RolePermission(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return get_user_role(request.user) in self.allowed_roles


class EsAdministrador(RolePermission):
    allowed_roles = ['Administrador']


class EsOperador(RolePermission):
    allowed_roles = ['Operador']


class EsAnalista(RolePermission):
    allowed_roles = ['Consumidor Analítico']


class EsDespachador(RolePermission):
    allowed_roles = ['Despachador']


class EsOperadorOAdministrador(RolePermission):
    allowed_roles = ['Operador', 'Administrador']


class EsOperadorOAnalistaOAdministrador(RolePermission):
    allowed_roles = ['Operador', 'Consumidor Analítico', 'Administrador']


class EsDespachadorOAdministrador(RolePermission):
    allowed_roles = ['Despachador', 'Administrador']


class EsUnidadEmergencia(RolePermission):
    allowed_roles = ['Unidad de Emergencia']
