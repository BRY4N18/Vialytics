import json
import time
import logging
import requests
from confluent_kafka import Producer
from django.conf import settings

logger = logging.getLogger(__name__)


class KafkaRepository:
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1
    MAX_BACKOFF = 8

    def __init__(self):
        try:
            self.producer = Producer({
                "bootstrap.servers": settings.KAFKA_BROKER,
                "acks": "all",
                "retries": 3,
                "retry.backoff.ms": 100,
            })
            logger.info(f"Kafka producer initialized with broker: {settings.KAFKA_BROKER}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise

    def enviar_mensaje(self, topic, clave_primaria, datos_json, operacion="INSERT"):
        if not topic or not isinstance(topic, str):
            logger.error(f"Invalid topic: {topic}")
            raise ValueError("Topic must be a non-empty string")

        if clave_primaria is None:
            logger.error("Primary key cannot be None")
            raise ValueError("Primary key cannot be None")

        if not isinstance(datos_json, dict):
            logger.error(f"Invalid data type: {type(datos_json)}")
            raise ValueError("Data must be a dictionary")

        operaciones_validas = ["INSERT", "AUDIT_INSERT", "DELETE"]
        if operacion not in operaciones_validas:
            logger.error(
                f"Invalid operation: {operacion}. "
                f"Must be one of: {', '.join(operaciones_validas)}"
            )
            raise ValueError(
                f"Operation must be one of: {', '.join(operaciones_validas)}"
            )

        datos_con_operacion = datos_json.copy()
        datos_con_operacion["operacion"] = operacion

        valor_str = json.dumps(datos_con_operacion)
        clave_str = str(clave_primaria)

        backoff = self.INITIAL_BACKOFF

        for intento in range(self.MAX_RETRIES):
            try:
                self.producer.produce(
                    topic=topic,
                    key=clave_str,
                    value=valor_str
                )
                self.producer.flush(timeout=10)
                logger.info(
                    f"Message sent to topic '{topic}' with key '{clave_str}' "
                    f"and operation '{operacion}'"
                )
                return True

            except Exception as e:
                logger.warning(
                    f"Attempt {intento + 1}/{self.MAX_RETRIES} failed to send to Kafka: {e}"
                )

                if intento < self.MAX_RETRIES - 1:
                    time.sleep(backoff)
                    backoff = min(backoff * 2, self.MAX_BACKOFF)
                else:
                    logger.error(
                        f"Failed to send message to Kafka after {self.MAX_RETRIES} attempts: {e}"
                    )
                    return False

        return False


class BaseWriteRepository:
    topic = ""
    primary_key_field = ""

    @classmethod
    def create(cls, payload):
        ahora_ms = int(time.time() * 1000)
        payload.setdefault("fecha_actualizacion", ahora_ms)
        try:
            kafka = KafkaRepository()
            return kafka.enviar_mensaje(
                topic=cls.topic,
                clave_primaria=payload.get(cls.primary_key_field, ""),
                datos_json=payload,
                operacion="INSERT",
            )
        except Exception as e:
            logger.error("Error enviando a Kafka (topic=%s): %s", cls.topic, e)
            return False


class PinotRepository:
    @staticmethod
    def escape_sql_str(value: str) -> str:
        escaped = value.replace("'", "''")
        escaped = escaped.replace("\\", "\\\\")
        return escaped

    @staticmethod
    def execute_query(sql_query, use_multistage=False):
        if not sql_query or not isinstance(sql_query, str):
            logger.error(f"Invalid SQL query: {sql_query}")
            raise ValueError("SQL query must be a non-empty string")

        url = (
            f"{settings.PINOT_SCHEME}://{settings.PINOT_HOST}:"
            f"{settings.PINOT_PORT}{settings.PINOT_PATH}"
        )

        payload = {"sql": sql_query}

        if use_multistage:
            payload["queryOptions"] = (
                "useMultistageEngine=true;"
                "maxRowsInJoin=50000000;"
                "joinOverflowMode=BREAK"
            )

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            logger.debug(f"Executing Pinot query: {sql_query[:100]}...")

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=5.0
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("exceptions") and len(data["exceptions"]) > 0:
                    error_msg = data["exceptions"][0].get(
                        "message",
                        "Unknown error in Pinot"
                    )
                    logger.warning(
                        f"Pinot returned exception: {error_msg}\n"
                        f"Query: {sql_query}"
                    )
                    return []

                if "resultTable" in data and "rows" in data["resultTable"]:
                    columnas = data["resultTable"]["dataSchema"]["columnNames"]
                    filas = data["resultTable"]["rows"]
                    resultado = [dict(zip(columnas, fila)) for fila in filas]
                    logger.debug(f"Query returned {len(resultado)} rows")
                    return resultado

                logger.debug("Query returned no results")
                return []
            else:
                logger.error(
                    f"Pinot error: {response.status_code} - {response.text}"
                )
                return []

        except requests.exceptions.ConnectionError as e:
            logger.error(
                f"Connection error to Pinot (is Docker running?): {e}"
            )
            return []
        except requests.exceptions.Timeout as e:
            logger.error(f"Pinot query timeout: {e}")
            return []
        except Exception as e:
            logger.error(f"Exception executing Pinot query: {e}")
            return []
