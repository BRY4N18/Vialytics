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
    name="Respuesta a Emergencias",
    description="Módulo para despachadores. Gestión de unidades de emergencia, recepción de despachos y actualización de estado en tiempo real durante la respuesta a incidentes.",
    icon="emergency",
    landing_route="/unidades",
    roles_allowed=["Despachador", "Administrador"],
    nav_items=[
        NavItem(
            label="Unidades de Emergencia",
            route="/unidades",
            icon="local_fire_department",
            cu="CU-08",
            description="Listado y mapa de unidades disponibles, en servicio y fuera de servicio",
            permission="view_unidades",
        ),
        NavItem(
            label="Estado de Unidad",
            route="/unidades/estado",
            icon="toggle_on",
            cu="CU-08",
            description="Actualizar estado de una unidad: Disponible, En Servicio, Fuera de Servicio",
            permission="change_unidad_estado",
        ),
        NavItem(
            label="Recibir Despacho",
            route="/despachos/recibir",
            icon="inbox",
            cu="CU-07",
            description="Recepción y confirmación de despachos asignados (pendiente de implementación)",
            permission="recibir_despacho",
        ),
        NavItem(
            label="Retiro Vehicular",
            route="/retiro-vehicular",
            icon="tow_truck",
            cu="CU-09",
            description="Gestión de retiro de vehículos involucrados (pendiente de implementación)",
            permission="gestionar_retiro",
        ),
    ],
)
