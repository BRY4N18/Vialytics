from django.apps import AppConfig


class AccidentesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accidentes'
    verbose_name = 'Sistema de Gestión de Accidentes'

    def ready(self):
        pass
