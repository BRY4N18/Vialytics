import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

import logging
from accidentes.shared.repositories import PinotRepository
from accidentes.PKG2_Respuesta_Emergencias.CU07_Recibir_Despacho.repositories import NotificacionWriteRepository

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def deactivate_bad_notifications():
    rows = PinotRepository.execute_query(
        "SELECT idnotificaciondespacho, idaccidente FROM notificacionesdespachos "
        "WHERE activo = true AND (idaccidente = 0 OR idaccidente IS NULL) "
        "ORDER BY idnotificaciondespacho DESC LIMIT 500"
    )

    if not rows:
        logger.info("No se encontraron notificaciones con idaccidente = 0")
        return

    logger.info("Se encontraron %d notificaciones con idaccidente = 0", len(rows))
    exito = 0
    fallo = 0

    for r in rows:
        nid = int(r["idnotificaciondespacho"])
        try:
            ok = NotificacionWriteRepository.desactivar(nid)
            if ok:
                exito += 1
                logger.info("Desactivada notificacion %s", nid)
            else:
                fallo += 1
                logger.warning("Fallo al desactivar notificacion %s", nid)
        except Exception as e:
            fallo += 1
            logger.error("Error desactivando notificacion %s: %s", nid, e)

    logger.info("Resumen: %d desactivadas, %d fallos", exito, fallo)


if __name__ == "__main__":
    deactivate_bad_notifications()
