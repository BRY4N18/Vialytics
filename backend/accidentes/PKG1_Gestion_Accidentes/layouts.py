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
    name="Gestión de Accidentes",
    description="Módulo principal para operadores. Gestión del ciclo de vida completo de accidentes viales: registro, visualización en mapa, actualización de estado, despacho de emergencias y dashboard de KPIs.",
    icon="warning_amber",
    landing_route="/dashboard",
    roles_allowed=["Operador", "Administrador", "Supervisor", "Despachador"],
    nav_items=[
        NavItem(
            label="Dashboard",
            route="/dashboard",
            icon="dashboard",
            cu="CU-20",
            description="KPIs, tendencias mensuales, distribución por severidad, estados y clima",
            permission="view_dashboard",
        ),
        NavItem(
            label="Registrar Accidente",
            route="/registro",
            icon="add_circle",
            cu="CU-01",
            description="Formulario de registro con ubicación, vehículos, conductores y clima",
            permission="add_accidente",
        ),
        NavItem(
            label="Mapa en Tiempo Real",
            route="/mapa",
            icon="map",
            cu="CU-02",
            description="Visualización geoespacial de accidentes activos con filtros por severidad, ubicación y fecha",
            permission="view_mapa",
        ),
        NavItem(
            label="Listado de Accidentes",
            route="/lista",
            icon="list",
            cu="CU-10",
            description="Búsqueda paginada con filtros por severidad, estado, fechas, heridos y matrícula",
            permission="view_lista",
        ),
        NavItem(
            label="Detalle y Expediente",
            route="/detalle",
            icon="description",
            cu="CU-14",
            description="Vista completa del accidente con datos de clima, vehículos, conductores, notas y despachos",
            permission="view_detalle",
        ),
        NavItem(
            label="Actualizar Estado",
            route="/estado",
            icon="update",
            cu="CU-03",
            description="Transiciones de estado: Reportado → En Atención → Despejado → Archivado",
            permission="change_estado",
        ),
        NavItem(
            label="Despachar Unidades",
            route="/despacho",
            icon="local_police",
            cu="CU-04",
            description="Asignación de unidades de emergencia (ambulancias, policía, bomberos) a un accidente",
            permission="add_despacho",
        ),
        NavItem(
            label="Archivar Accidente",
            route="/archivar",
            icon="archive",
            cu="CU-05",
            description="Archivar accidentes cerrados (pendiente de implementación)",
            permission="archive_accidente",
        ),
    ],
)
