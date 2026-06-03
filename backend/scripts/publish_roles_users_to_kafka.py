import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from accidentes.shared.repositories import KafkaRepository

def publish():
    print("Publishing Roles and Users to Kafka / Pinot...")
    kafka = KafkaRepository()
    ahora_ms = int(time.time() * 1000)

    # 1. Publish Roles
    print("\nPublishing Roles...")
    roles_data = [
        {"idrol": 1, "rol": "Administrador", "descripcion": "Acceso total", "activo": True, "fecha_actualizacion": ahora_ms},
        {"idrol": 2, "rol": "Operador", "descripcion": "Registro y despachos", "activo": True, "fecha_actualizacion": ahora_ms},
        {"idrol": 3, "rol": "Consumidor Analítico", "descripcion": "Monitoreo y analiticas", "activo": True, "fecha_actualizacion": ahora_ms},
        {"idrol": 4, "rol": "Despachador", "descripcion": "Control de unidades", "activo": True, "fecha_actualizacion": ahora_ms}
    ]
    for r in roles_data:
        res = kafka.enviar_mensaje(
            topic="roles_topic",
            clave_primaria=r["idrol"],
            datos_json=r,
            operacion="INSERT"
        )
        print(f"Role '{r['rol']}' published: {res}")

    # 2. Publish Users (seed data)
    print("\nPublishing Users...")
    seed_users = [
        {"idusuario": 1, "nombres": "Admin", "apellidos": "Sistema", "gmail": "admin@sga.com", "identificacion": "0000000001", "genero": "M", "activo": True, "fechanacimiento": ahora_ms, "fecha_actualizacion": ahora_ms, "rol": 1, "password": "pbkdf2_sha256$admin123"},
        {"idusuario": 2, "nombres": "Operador", "apellidos": "Principal", "gmail": "operador@sga.com", "identificacion": "0000000002", "genero": "F", "activo": True, "fechanacimiento": ahora_ms, "fecha_actualizacion": ahora_ms, "rol": 2, "password": "pbkdf2_sha256$operador123"},
        {"idusuario": 3, "nombres": "Analista", "apellidos": "General", "gmail": "analista@sga.com", "identificacion": "0000000003", "genero": "M", "activo": True, "fechanacimiento": ahora_ms, "fecha_actualizacion": ahora_ms, "rol": 3, "password": "pbkdf2_sha256$analista123"},
        {"idusuario": 4, "nombres": "Despachador", "apellidos": "Central", "gmail": "despachador@sga.com", "identificacion": "0000000004", "genero": "F", "activo": True, "fechanacimiento": ahora_ms, "fecha_actualizacion": ahora_ms, "rol": 4, "password": "pbkdf2_sha256$despachador123"},
    ]
    for u in seed_users:
        user_payload = {
            "idusuario": u["idusuario"],
            "apellidos": u["apellidos"],
            "nombres": u["nombres"],
            "gmail": u["gmail"],
            "identificacion": u["identificacion"],
            "genero": u["genero"],
            "activo": u["activo"],
            "fechanacimiento": u["fechanacimiento"],
            "fecha_actualizacion": u["fecha_actualizacion"]
        }
        res = kafka.enviar_mensaje(
            topic="usuarios_topic",
            clave_primaria=u["idusuario"],
            datos_json=user_payload,
            operacion="INSERT"
        )
        print(f"User '{u['nombres']} {u['apellidos']}' published: {res}")

        # 3. Publish User Roles mapping
        idusuariorol = int(f"{u['idusuario']}{u['rol']}")
        mapping_payload = {
            "idusuariorol": idusuariorol,
            "idusuario": u["idusuario"],
            "idrol": u["rol"],
            "activo": True,
            "fecha_actualizacion": ahora_ms
        }
        res = kafka.enviar_mensaje(
            topic="usuariosroles_topic",
            clave_primaria=idusuariorol,
            datos_json=mapping_payload,
            operacion="INSERT"
        )
        print(f"Relation User ID {u['idusuario']} -> Role ID {u['rol']} published: {res}")

        # 4. Publish Credentials
        cred_payload = {
            "idcredencial": u["idusuario"],
            "idusuario": u["idusuario"],
            "contraseña": u["password"],
            "activo": True,
            "fecha_actualizacion": ahora_ms
        }
        res = kafka.enviar_mensaje(
            topic="credenciales_topic",
            clave_primaria=u["idusuario"],
            datos_json=cred_payload,
            operacion="INSERT"
        )
        print(f"Credential for User ID {u['idusuario']} published: {res}")

if __name__ == "__main__":
    publish()
