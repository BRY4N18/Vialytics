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
    name="Consulta y Análisis",
    description="Módulo para analistas y consumidores de datos. Búsqueda avanzada de accidentes históricos, generación de informes estadísticos, exportación de datos y visualización de mapas de calor.",
    icon="analytics",
    landing_route="/buscar",
    roles_allowed=["Analista", "Administrador", "Supervisor"],
    nav_items=[
        NavItem(
            label="Buscar Accidentes",
            route="/buscar",
            icon="search",
            cu="CU-10",
            description="Búsqueda avanzada con filtros por severidad, fechas, ubicación, heridos y matrícula",
            permission="view_busqueda",
        ),
        NavItem(
            label="Generar Informes",
            route="/informes",
            icon="bar_chart",
            cu="CU-11",
            description="Informes estadísticos con tendencias, distribución por severidad y top estados",
            permission="view_informes",
        ),
        NavItem(
            label="Exportar Datos",
            route="/exportar",
            icon="file_download",
            cu="CU-12",
            description="Exportación a CSV y PDF de resultados de búsqueda (pendiente de implementación)",
            permission="exportar_datos",
        ),
        NavItem(
            label="Mapa de Calor",
            route="/mapa-calor",
            icon="heat_map",
            cu="CU-13",
            description="Visualización de densidad de accidentes por zona geográfica (pendiente de implementación)",
            permission="view_mapa_calor",
        ),
        NavItem(
            label="Solicitar Expediente",
            route="/expediente",
            icon="folder_open",
            cu="CU-14",
            description="Expediente oficial completo del accidente con evidencias, clima, vehículos y notas",
            permission="view_expediente",
        ),
    ],
)
