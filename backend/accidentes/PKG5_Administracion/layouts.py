from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class NavItem:
    label: str
    route: str
    icon: str
    cu: str
    description: str
    permission: Optional[str] = None
    children: List['NavItem'] = field(default_factory=list)


@dataclass
class ModuleLayout:
    name: str
    description: str
    icon: str
    landing_route: str
    roles_allowed: List[str]
    nav_items: List[NavItem]


LAYOUT = ModuleLayout(
    name="Administración del Sistema",
    description="Módulo exclusivo para administradores. Gestión de usuarios, roles y permisos, auditoría de accesos y configuración del sistema.",
    icon="admin_panel_settings",
    landing_route="/admin/usuarios",
    roles_allowed=["Administrador"],
    nav_items=[
        NavItem(
            label="Iniciar Sesión",
            route="/login",
            icon="login",
            cu="CU-21",
            description="Autenticación JWT para todos los roles del sistema",
            permission=None,
        ),
        NavItem(
            label="Usuarios",
            route="/admin/usuarios",
            icon="group",
            cu="CU-17",
            description="CRUD de usuarios del sistema (pendiente de implementación)",
            permission="gestionar_usuarios",
        ),
        NavItem(
            label="Roles y Permisos",
            route="/admin/roles",
            icon="security",
            cu="CU-18",
            description="Gestión de roles y asignación de permisos (pendiente de implementación)",
            permission="gestionar_roles",
        ),
        NavItem(
            label="Auditoría de Accesos",
            route="/admin/auditoria",
            icon="receipt_long",
            cu="CU-19",
            description="Registro de accesos y actividades de usuarios (pendiente de implementación)",
            permission="view_auditoria",
        ),
    ],
)
