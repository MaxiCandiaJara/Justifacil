from django.apps import AppConfig


class JustificacionesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "justificaciones"

    def ready(self):
        # Lugar para señales futuras
        return super().ready()
