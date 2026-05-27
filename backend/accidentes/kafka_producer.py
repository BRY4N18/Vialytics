"""
Productor Kafka asíncrono para el SGA.
Maneja elegantemente la ausencia de Kafka en entornos de desarrollo.
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Intento de importar aiokafka; si no está disponible, se usa modo degradado
try:
    from aiokafka import AIOKafkaProducer
    KAFKA_DISPONIBLE = True
except ImportError:
    AIOKafkaProducer = None
    KAFKA_DISPONIBLE = False
    logger.warning(
        "aiokafka no está instalado. Los eventos Kafka serán ignorados. "
        "Instala con: pip install aiokafka"
    )

from django.conf import settings


class KafkaProducerService:
    """
    Servicio productor Kafka asíncrono con manejo gracioso de errores.
    Si Kafka no está disponible, registra warnings y continúa sin interrumpir el flujo.
    """

    KAFKA_BOOTSTRAP_SERVERS: str = getattr(
        settings, "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
    )

    @classmethod
    async def publicar_evento(cls, topic: str, mensaje: dict[str, Any]) -> None:
        """
        Publica un evento en el topic Kafka especificado.

        Args:
            topic: Nombre del topic Kafka.
            mensaje: Diccionario con los datos del evento.
        """
        if not KAFKA_DISPONIBLE:
            logger.warning(
                "Kafka no disponible. Evento no publicado. Topic: %s, Mensaje: %s",
                topic,
                mensaje,
            )
            return

        try:
            await cls._publicar_con_producer(topic, mensaje)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Error al publicar evento en Kafka. Topic: %s, Error: %s",
                topic,
                exc,
                exc_info=True,
            )

    @classmethod
    async def _publicar_con_producer(
        cls, topic: str, mensaje: dict[str, Any]
    ) -> None:
        """
        Crea un producer temporal, publica el mensaje y lo cierra.

        Args:
            topic: Nombre del topic Kafka.
            mensaje: Datos del evento a publicar.
        """
        producer = AIOKafkaProducer(
            bootstrap_servers=cls.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        )
        await producer.start()
        try:
            await producer.send_and_wait(topic, mensaje)
            logger.debug(
                "Evento publicado en Kafka. Topic: %s, Keys: %s",
                topic,
                list(mensaje.keys()),
            )
        finally:
            await producer.stop()

    @classmethod
    async def publicar_evento_accidente(
        cls,
        accion: str,
        accidente_id: str,
        datos_adicionales: dict[str, Any] | None = None,
    ) -> None:
        """
        Publica un evento relacionado con un accidente.

        Args:
            accion: Acción realizada (CREADO, ESTADO_ACTUALIZADO, etc.).
            accidente_id: UUID del accidente.
            datos_adicionales: Datos extra del evento.
        """
        mensaje: dict[str, Any] = {
            "accion": accion,
            "accidente_id": accidente_id,
            **(datos_adicionales or {}),
        }
        await cls.publicar_evento("accidentes_topic", mensaje)

    @classmethod
    async def publicar_evento_despacho(
        cls,
        accion: str,
        despacho_id: int,
        accidente_id: str,
        unidad_id: int,
        datos_adicionales: dict[str, Any] | None = None,
    ) -> None:
        """
        Publica un evento relacionado con un despacho de unidad de emergencia.

        Args:
            accion: Acción realizada (DESPACHADO, CONFIRMADO, etc.).
            despacho_id: ID del despacho.
            accidente_id: UUID del accidente.
            unidad_id: ID de la unidad de emergencia.
            datos_adicionales: Datos extra del evento.
        """
        mensaje: dict[str, Any] = {
            "accion": accion,
            "despacho_id": despacho_id,
            "accidente_id": accidente_id,
            "unidad_id": unidad_id,
            **(datos_adicionales or {}),
        }
        await cls.publicar_evento("despachos_topic", mensaje)
