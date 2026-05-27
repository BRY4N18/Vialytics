import os
import sys
import django
import time

# Add current path to system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Group
from accidentes.models import Usuario
from accidentes.repositories import KafkaRepository

def publish():
    print("Publishing Roles and Users to Pinot's Kafka topics...")
    kafka = KafkaRepository()
    ahora_ms = int(time.time() * 1000)

    # 1. Publish Roles
    print("\nPublishing Roles...")
    roles_data = [
        {"idrol": 1, "rol": "Administrador", "descripcion": "Acceso total", "activo": True, "fecha_actualizacion": ahora_ms},
        {"idrol": 2, "rol": "Operador", "descripcion": "Registro y despachos", "activo": True, "fecha_actualizacion": ahora_ms},
        {"idrol": 3, "rol": "Supervisor", "descripcion": "Monitoreo y analiticas", "activo": True, "fecha_actualizacion": ahora_ms},
        {"idrol": 4, "rol": "Despachador", "descripcion": "Control de unidades", "activo": True, "fecha_actualizacion": ahora_ms}
    ]
    for r in roles_data:
        res = kafka.enviar_mensaje(
            topic="roles_topic",
            clave_primaria=r["idrol"],
            datos_json=r,
            operacion="INSERT"
        )
        print(f"Role '{r['rol']}' published to roles_topic: {res}")

    # 2. Publish Users (from our custom Usuario model)
    print("\nPublishing Users...")
    usuarios_qs = Usuario.objects.all()
    for u in usuarios_qs:
        # Map birthdate if present, otherwise default to a timestamp
        fn_ms = int(time.mktime(u.fechanacimiento.timetuple()) * 1000) if u.fechanacimiento else ahora_ms
        fa_ms = int(u.fecha_actualizacion.timestamp() * 1000) if u.fecha_actualizacion else ahora_ms
        
        user_payload = {
            "idusuario": u.idusuario,
            "apellidos": u.apellidos,
            "nombres": u.nombres,
            "gmail": u.gmail,
            "identificacion": u.identificacion,
            "genero": u.genero,
            "activo": u.activo,
            "fechanacimiento": fn_ms,
            "fecha_actualizacion": fa_ms
        }
        
        res = kafka.enviar_mensaje(
            topic="usuarios_topic",
            clave_primaria=u.idusuario,
            datos_json=user_payload,
            operacion="INSERT"
        )
        print(f"User '{u.nombres} {u.apellidos}' published to usuarios_topic: {res}")

    # 3. Publish User Roles relations (from Django User groups relations)
    print("\nPublishing User Roles mapping...")
    django_users = User.objects.all()
    for du in django_users:
        # Find corresponding Custom profile id
        try:
            custom_u = Usuario.objects.get(gmail=du.email)
            idusuario = custom_u.idusuario
        except Usuario.DoesNotExist:
            continue
            
        for g in du.groups.all():
            # Map group name to idrol
            idrol = 1
            if g.name == "Administrador":
                idrol = 1
            elif g.name == "Operador":
                idrol = 2
            elif g.name == "Supervisor":
                idrol = 3
            elif g.name == "Despachador":
                idrol = 4
                
            idusuariorol = int(f"{idusuario}{idrol}")
            
            mapping_payload = {
                "idusuariorol": idusuariorol,
                "idusuario": idusuario,
                "idrol": idrol,
                "activo": True,
                "fecha_actualizacion": ahora_ms
            }
            
            res = kafka.enviar_mensaje(
                topic="usuariosroles_topic",
                clave_primaria=idusuariorol,
                datos_json=mapping_payload,
                operacion="INSERT"
            )
            print(f"Relation User ID {idusuario} -> Role ID {idrol} published to usuariosroles_topic: {res}")

    # 4. Publish User Credentials mapping
    print("\nPublishing Credentials mapping...")
    for du in django_users:
        try:
            custom_u = Usuario.objects.get(gmail=du.email)
            idusuario = custom_u.idusuario
        except Usuario.DoesNotExist:
            continue
            
        idcredencial = idusuario
        
        cred_payload = {
            "idcredencial": idcredencial,
            "idusuario": idusuario,
            "contraseña": du.password, # hashed password
            "activo": True,
            "fecha_actualizacion": ahora_ms
        }
        
        res = kafka.enviar_mensaje(
            topic="credenciales_topic",
            clave_primaria=idcredencial,
            datos_json=cred_payload,
            operacion="INSERT"
        )
        print(f"Credential for User ID {idusuario} published to credenciales_topic: {res}")

if __name__ == "__main__":
    publish()
