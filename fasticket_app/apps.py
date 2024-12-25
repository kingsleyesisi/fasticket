from django.apps import AppConfig


class FasticketAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fasticket_app'

    def ready(self):
        import fasticket_app.signals