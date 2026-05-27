import os
import sys
import django

# Add current path to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from accidentes.models import Usuario

def populate():
    print("Populating roles (Groups)...")
    roles = ["Administrador", "Operador", "Supervisor", "Despachador"]
    group_map = {}
    for r in roles:
        group, created = Group.objects.get_or_create(name=r)
        group_map[r] = group
        print(f"Group '{r}': {'Created' if created else 'Exists'}")

    print("\nPopulating fake users...")
    users_data = [
        {
            "username": "admin_sga",
            "first_name": "Carlos",
            "last_name": "Gomez",
            "email": "admin@sga.com",
            "role": "Administrador",
            "identificacion": "1724567891",
            "genero": "M",
            "password": "Password123"
        },
        {
            "username": "operador_sga",
            "first_name": "Laura",
            "last_name": "Mendoza",
            "email": "operador@sga.com",
            "role": "Operador",
            "identificacion": "1724567892",
            "genero": "F",
            "password": "Password123"
        },
        {
            "username": "supervisor_sga",
            "first_name": "Patricia",
            "last_name": "Vega",
            "email": "supervisor@sga.com",
            "role": "Supervisor",
            "identificacion": "1724567893",
            "genero": "F",
            "password": "Password123"
        },
        {
            "username": "despachador_sga",
            "first_name": "David",
            "last_name": "Torres",
            "email": "despachador@sga.com",
            "role": "Despachador",
            "identificacion": "1724567894",
            "genero": "M",
            "password": "Password123"
        }
    ]

    for ud in users_data:
        # 1. Native Auth User
        user, created = User.objects.get_or_create(
            username=ud["username"],
            defaults={
                "email": ud["email"],
                "first_name": ud["first_name"],
                "last_name": ud["last_name"],
                "password": make_password(ud["password"]),
                "is_staff": True if ud["role"] in ["Administrador", "Supervisor"] else False,
                "is_active": True
            }
        )
        
        if created:
            user.groups.add(group_map[ud["role"]])
            print(f"User '{ud['username']}' created and assigned to '{ud['role']}'.")
        else:
            print(f"User '{ud['username']}' already exists.")

        # 2. Custom SGA Usuario model mapping
        custom_u, c_created = Usuario.objects.get_or_create(
            gmail=ud["email"],
            defaults={
                "nombres": ud["first_name"],
                "apellidos": ud["last_name"],
                "identificacion": ud["identificacion"],
                "genero": ud["genero"],
                "activo": True
            }
        )
        if c_created:
            print(f"SGA custom profile for '{ud['email']}' created.")
        else:
            print(f"SGA custom profile for '{ud['email']}' already exists.")

if __name__ == "__main__":
    populate()
