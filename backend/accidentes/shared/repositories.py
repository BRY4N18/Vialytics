import json
import time
import logging
from typing import Any
import requests
import threading
from confluent_kafka import Producer
from django.conf import settings

logger = logging.getLogger(__name__)


class KafkaRepository:
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1
    MAX_BACKOFF = 8
    _instance = None
    _lock = threading.Lock()
    _producer = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._producer is None:
            self._init_producer()

    def _init_producer(self):
        try:
            self._producer = Producer({
                "bootstrap.servers": settings.KAFKA_BROKER,
                "acks": "all",
                "retries": 3,
                "retry.backoff.ms": 100,
            })
            logger.info(f"Kafka producer initialized with broker: {settings.KAFKA_BROKER}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise

    @property
    def producer(self):
        if self._producer is None:
            self._init_producer()
        return self._producer

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


kafka_repository = KafkaRepository()


class BaseWriteRepository:
    topic = ""
    primary_key_field = ""

    @classmethod
    def create(cls, payload):
        ahora_ms = int(time.time() * 1000)
        payload.setdefault("fecha_actualizacion", ahora_ms)
        try:
            return kafka_repository.enviar_mensaje(
                topic=cls.topic,
                clave_primaria=payload.get(cls.primary_key_field, ""),
                datos_json=payload,
                operacion="INSERT",
            )
        except Exception as e:
            logger.error("Error enviando a Kafka (topic=%s): %s", cls.topic, e)
            return False

    @classmethod
    def update(cls, primary_key, payload):
        ahora_ms = int(time.time() * 1000)
        payload["fecha_actualizacion"] = ahora_ms
        try:
            return kafka_repository.enviar_mensaje(
                topic=cls.topic,
                clave_primaria=primary_key,
                datos_json=payload,
                operacion="INSERT",
            )
        except Exception as e:
            logger.error("Error actualizando en Kafka (topic=%s): %s", cls.topic, e)
            return False


class QueryTimeout:
    CATALOGO = 3.0
    BUSQUEDA = 5.0
    EXPEDIENTE = 10.0
    ESCRITURA = 5.0
    DEFAULT = 5.0


class PinotRepository:
    _instance = None
    _lock = threading.Lock()
    _session = None
    _session_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def _get_session(cls) -> requests.Session:
        if cls._session is None:
            with cls._session_lock:
                if cls._session is None:
                    cls._session = requests.Session()
                    adapter = requests.adapters.HTTPAdapter(
                        pool_connections=10,
                        pool_maxsize=20,
                        max_retries=3,
                        pool_block=False
                    )
                    cls._session.mount('http://', adapter)
                    cls._session.mount('https://', adapter)
        return cls._session

    @staticmethod
    def escape_sql_str(value: str) -> str:
        escaped = value.replace("'", "''")
        escaped = escaped.replace("\\", "\\\\")
        return escaped

    @staticmethod
    def safe_value(value: Any) -> str:
        if isinstance(value, (int, float)):
            return str(value)
        if value is None:
            return "NULL"
        escaped = PinotRepository.escape_sql_str(str(value))
        return f"'{escaped}'"

    @staticmethod
    def build_safe_query(template: str, *args: Any) -> str:
        escaped_args = [PinotRepository.safe_value(a) for a in args]
        parts = template.split("?")
        if len(parts) - 1 != len(escaped_args):
            raise ValueError(
                f"Placeholder count ({len(parts) - 1}) "
                f"does not match argument count ({len(escaped_args)})"
            )
        result = parts[0]
        for i, part in enumerate(parts[1:]):
            result += escaped_args[i] + part
        return result

    def _execute(self, sql_query, use_multistage=False, timeout=None):
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

        session = self._get_session()

        try:
            logger.debug(f"Executing Pinot query: {sql_query[:100]}...")

            response = session.post(
                url,
                json=payload,
                headers=headers,
                timeout=timeout or QueryTimeout.DEFAULT
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

    @staticmethod
    def execute_query(sql_query, use_multistage=False, timeout=None):
        return pinot_repository._execute(sql_query, use_multistage, timeout)

    @staticmethod
    def safe_query(template: str, *args, use_multistage=False, timeout=None):
        safe_sql = PinotRepository.build_safe_query(template, *args)
        return pinot_repository._execute(safe_sql, use_multistage, timeout)


pinot_repository = PinotRepository()
