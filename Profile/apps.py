from django.apps import AppConfig


class FasticketAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Profile'

    def ready(self):
        import Profile.signals