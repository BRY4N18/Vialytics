from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Seed Django auth users for JWT login'

    USERS = [
        {'username': 'operador_sga', 'password': 'sga_secure_pwd_2026',
         'first_name': 'Laura', 'last_name': 'Mendoza'},
        {'username': 'admin_sga', 'password': 'sga_secure_pwd_2026',
         'first_name': 'Carlos', 'last_name': 'Gomez'},
        {'username': 'analista_sga', 'password': 'sga_secure_pwd_2026',
         'first_name': 'Patricia', 'last_name': 'Vega'},
        {'username': 'despachador_sga', 'password': 'sga_secure_pwd_2026',
         'first_name': 'David', 'last_name': 'Torres'},
    ]

    def handle(self, *args, **options):
        for u in self.USERS:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={
                    'password': make_password(u['password']),
                    'first_name': u['first_name'],
                    'last_name': u['last_name'],
                    'is_active': True,
                }
            )
            if not created:
                user.password = make_password(u['password'])
                user.first_name = u['first_name']
                user.last_name = u['last_name']
                user.is_active = True
                user.save()

            self.stdout.write(self.style.SUCCESS(
                f"OK Usuario '{u['username']}' ({u['first_name']} {u['last_name']}) listo"
            ))

        self.stdout.write(self.style.SUCCESS('\nSeed de usuarios JWT completado.'))
