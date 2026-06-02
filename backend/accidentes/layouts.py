from accidentes.PKG1_Gestion_Accidentes.layouts import LAYOUT as PKG1_LAYOUT
from accidentes.PKG2_Respuesta_Emergencias.layouts import LAYOUT as PKG2_LAYOUT
from accidentes.PKG3_Consulta_Analisis.layouts import LAYOUT as PKG3_LAYOUT
from accidentes.PKG4_Portal_Externo.layouts import LAYOUT as PKG4_LAYOUT
from accidentes.PKG5_Administracion.layouts import LAYOUT as PKG5_LAYOUT

PKG_LAYOUTS = {
    "PKG1": PKG1_LAYOUT,
    "PKG2": PKG2_LAYOUT,
    "PKG3": PKG3_LAYOUT,
    "PKG4": PKG4_LAYOUT,
    "PKG5": PKG5_LAYOUT,
}


def get_layout(pkg_id: str):
    return PKG_LAYOUTS.get(pkg_id)


def get_all_layouts():
    return dict(PKG_LAYOUTS)
