import requests

PINOT_CONTROLLER = "http://localhost:9000"

# Schema: estadosunidadesemergencias
estados_schema = {
    "schemaName": "estadosunidadesemergencias",
    "dimensionFieldSpecs": [
        {"name": "idestadounidad", "dataType": "INT"},
        {"name": "estadounidad", "dataType": "STRING"},
        {"name": "activo", "dataType": "BOOLEAN"},
    ],
    "dateTimeFieldSpecs": [
        {
            "name": "fecha_actualizacion",
            "dataType": "TIMESTAMP",
            "format": "1:MILLISECONDS:EPOCH",
            "granularity": "1:MILLISECONDS",
        }
    ],
    "primaryKeyColumns": ["idestadounidad"],
}

# Schema: historialesestadosunidadesemergencias
historial_schema = {
    "schemaName": "historialesestadosunidadesemergencias",
    "dimensionFieldSpecs": [
        {"name": "idhistorial", "dataType": "INT"},
        {"name": "idunidademergencia", "dataType": "INT"},
        {"name": "unidademergencia", "dataType": "STRING"},
        {"name": "tipounidademergencia", "dataType": "STRING"},
        {"name": "estadoanterior", "dataType": "STRING"},
        {"name": "estadonuevo", "dataType": "STRING"},
        {"name": "activo", "dataType": "BOOLEAN"},
    ],
    "dateTimeFieldSpecs": [
        {
            "name": "fecha_actualizacion",
            "dataType": "TIMESTAMP",
            "format": "1:MILLISECONDS:EPOCH",
            "granularity": "1:MILLISECONDS",
        }
    ],
    "primaryKeyColumns": ["idhistorial"],
}

# Table: estadosunidadesemergencias
estados_table = {
    "tableName": "estadosunidadesemergencias",
    "schemaName": "estadosunidadesemergencias",
    "tableType": "REALTIME",
    "segmentsConfig": {
        "timeColumnName": "fecha_actualizacion",
        "replication": "1",
        "replicasPerPartition": "1",
    },
    "tenants": {},
    "tableIndexConfig": {
        "loadMode": "MMAP",
        "streamConfigs": {
            "streamType": "kafka",
            "stream.kafka.topic.name": "estadosunidadesemergencias_topic",
            "stream.kafka.broker.list": "kafka:29092",
            "stream.kafka.consumer.type": "lowlevel",
            "stream.kafka.consumer.prop.auto.offset.reset": "smallest",
            "stream.kafka.consumer.factory.class.name": "org.apache.pinot.plugin.stream.kafka20.KafkaConsumerFactory",
            "stream.kafka.decoder.class.name": "org.apache.pinot.plugin.stream.kafka.KafkaJSONMessageDecoder",
        },
    },
    "routing": {"instanceSelectorType": "strictReplicaGroup"},
    "upsertConfig": {"mode": "FULL", "comparisonColumn": "fecha_actualizacion"},
    "metadata": {"customConfigs": {}},
}

# Table: historialesestadosunidadesemergencias
historial_table = {
    "tableName": "historialesestadosunidadesemergencias",
    "schemaName": "historialesestadosunidadesemergencias",
    "tableType": "REALTIME",
    "segmentsConfig": {
        "timeColumnName": "fecha_actualizacion",
        "replication": "1",
        "replicasPerPartition": "1",
    },
    "tenants": {},
    "tableIndexConfig": {
        "loadMode": "MMAP",
        "streamConfigs": {
            "streamType": "kafka",
            "stream.kafka.topic.name": "historialesestadosunidadesemergencias_topic",
            "stream.kafka.broker.list": "kafka:29092",
            "stream.kafka.consumer.type": "lowlevel",
            "stream.kafka.consumer.prop.auto.offset.reset": "smallest",
            "stream.kafka.consumer.factory.class.name": "org.apache.pinot.plugin.stream.kafka20.KafkaConsumerFactory",
            "stream.kafka.decoder.class.name": "org.apache.pinot.plugin.stream.kafka.KafkaJSONMessageDecoder",
        },
    },
    "routing": {"instanceSelectorType": "strictReplicaGroup"},
    "upsertConfig": {"mode": "FULL", "comparisonColumn": "fecha_actualizacion"},
    "metadata": {"customConfigs": {}},
}


def create_schema(schema):
    url = f"{PINOT_CONTROLLER}/schemas/"
    r = requests.post(url, json=schema, timeout=10)
    print(f"Schema {schema['schemaName']}: {r.status_code} {r.text[:200]}")
    return r.status_code == 200


def create_table(table):
    url = f"{PINOT_CONTROLLER}/tables/"
    r = requests.post(url, json=table, timeout=10)
    print(f"Table {table['tableName']}: {r.status_code} {r.text[:200]}")
    return r.status_code == 200


if __name__ == "__main__":
    print("Creating schemas...")
    if create_schema(estados_schema):
        print("  estadosunidadesemergencias schema created")
    if create_schema(historial_schema):
        print("  historialesestadosunidadesemergencias schema created")

    print("\nCreating tables...")
    if create_table(estados_table):
        print("  estadosunidadesemergencias table created")
    if create_table(historial_table):
        print("  historialesestadosunidadesemergencias table created")

    print("\nDone!")
