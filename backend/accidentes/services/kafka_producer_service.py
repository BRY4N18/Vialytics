import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)
KAFKA_BROKER = 'localhost:9092'


class KafkaProducerService:
    @staticmethod
    async def publicar_evento(topic: str, mensaje: Dict[str, Any]) -> bool:
        try:
            from aiokafka import AIOKafkaProducer  # noqa: PLC0415
            producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            )
            await producer.start()
            try:
                await producer.send_and_wait(topic, mensaje)
                logger.info('Evento publicado en topic=%s', topic)
                return True
            finally:
                await producer.stop()
        except ImportError:
            logger.warning('aiokafka no está instalado — evento no publicado')
            return False
        except Exception as exc:
            logger.warning('Kafka no disponible (%s): %s', topic, exc)
            return False

    @staticmethod
    async def publicar_accidente(accidente_id: str, accion: str, datos: Dict[str, Any]) -> bool:
        return await KafkaProducerService.publicar_evento(
            'accidentes_topic',
            {'idaccidente': accidente_id, 'accion': accion, **datos},
        )

    @staticmethod
    async def publicar_despacho(accidente_id: str, unidad_id: int, datos: Dict[str, Any]) -> bool:
        return await KafkaProducerService.publicar_evento(
            'despachos_topic',
            {'idaccidente': accidente_id, 'idunidademergencia': unidad_id, **datos},
        )
