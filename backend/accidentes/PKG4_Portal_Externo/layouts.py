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
    name="Portal Externo",
    description="Módulo público accesible sin autenticación. Consulta de mapa de accidentes y estadísticas históricas para ciudadanos, prensa y entidades externas.",
    icon="public",
    landing_route="/public/mapa",
    roles_allowed=["*"],
    nav_items=[
        NavItem(
            label="Mapa Público",
            route="/public/mapa",
            icon="map",
            cu="CU-15",
            description="Mapa de accidentes visible al público sin datos sensibles (heridos, fallecidos y descripción ocultos)",
            permission=None,
        ),
        NavItem(
            label="Estadísticas Públicas",
            route="/public/estadisticas",
            icon="bar_chart",
            cu="CU-16",
            description="Dashboard de KPIs público con tendencias y distribuciones",
            permission=None,
        ),
    ],
)
